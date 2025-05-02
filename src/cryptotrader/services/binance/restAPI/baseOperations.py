"""
Binance Base Operations

This module provides the foundational infrastructure for making API requests to Binance.
It handles:
- Request building, signing, and execution
- Rate limiting and throttling
- Error handling and retries
- HTTP client management
"""

import time
import hmac
import hashlib
import json
import urllib.parse
from typing import Dict, List, Optional, Any, Union, Tuple

import httpx

from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.binance.models import (
    RateLimit,
    RateLimitType,
    RateLimitInterval,
)

logger = get_logger(__name__)


class BinanceAPIRequest:
    """
    Builds and executes requests to the Binance API.

    Handles authentication, signing, parameter formatting, and error handling.
    Includes integrated rate limiting to prevent API request limit violations.
    """

    def __init__(
        self,
        method: str,
        endpoint: str,
        limit_type: Optional[RateLimitType] = None,
        weight: int = 1,
    ):
        """
        Initialize a new API request.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            limit_type: Type of rate limit for this request (defaults to REQUEST_WEIGHT)
            weight: Weight of this request for rate limiting
        """
        self.method = method
        self.endpoint = endpoint
        self.public_key = Secrets.BINANCE_API_KEY
        self.secret_key = Secrets.BINANCE_API_SECRET
        self.limit_type = limit_type or RateLimitType.REQUEST_WEIGHT
        self.weight = weight
        self.base_url = "https://api.binance.us"  # Remove trailing slash
        self.timeout = 10

        # Initialize internal rate limiter
        self.rate_limiter = RateLimiter()

        self.params = {}
        self.needs_signature = False  # Default to unauthenticated

    def requiresAuth(self, needed: bool = True) -> "BinanceAPIRequest":
        """
        Set whether this request requires authentication.

        Args:
            needed: Whether to add timestamp and signature

        Returns:
            Self for method chaining
        """
        self.needs_signature = (
            needed and self.public_key is not None and self.secret_key is not None
        )
        return self

    def withQueryParams(self, **kwargs) -> "BinanceAPIRequest":
        """
        Add query parameters to the request.

        Args:
            **kwargs: Key-value pairs to add as parameters

        Returns:
            Self for method chaining
        """
        for key, value in kwargs.items():
            if value is not None:
                self.params[key] = value
        return self

    def _signRequest(self) -> None:
        """
        Sign the request with the API secret.

        Adds timestamp and signature to the parameters.
        """
        # Add timestamp
        self.params["timestamp"] = str(int(time.time() * 1000))

        # Create signature
        query_string = urllib.parse.urlencode(self.params)
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Add signature to params
        self.params["signature"] = signature

    def execute(self, max_retries: int = 3, retry_delay: int = 1) -> Optional[Any]:
        """
        Execute the API request.

        Handles rate limiting, retries, and error handling.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (in seconds)

        Returns:
            Parsed JSON response or None if request failed
        """
        url = f"{self.base_url}{self.endpoint}"
        retries = 0

        while retries <= max_retries:
            try:
                # Check rate limits
                if not self.rate_limiter._checkRateLimit(self.limit_type, self.weight):
                    retry_after = self.rate_limiter._getRetryAfter()
                    if retry_after > 0:
                        logger.warning(f"Rate limit hit, retrying after {retry_after}s")
                        time.sleep(retry_after)
                    else:
                        # Use exponential backoff
                        current_delay = retry_delay * (2**retries)
                        logger.warning(
                            f"Rate limit hit, retrying after {current_delay}s"
                        )
                        time.sleep(current_delay)
                    retries += 1
                    continue

                # Sign the request if needed
                if self.needs_signature:
                    self._signRequest()

                # Set up headers
                headers = {}
                if self.public_key and self.needs_signature:
                    headers["X-MBX-APIKEY"] = self.public_key

                # Execute the request
                with httpx.Client() as client:
                    if self.method == "GET":
                        logger.debug(
                            f"Making GET request to {url} with params: {self.params}"
                        )
                        response = client.get(
                            url,
                            params=self.params,
                            headers=headers,
                            timeout=self.timeout,
                        )
                    elif self.method == "POST":
                        logger.debug(
                            f"Making POST request to {url} with params: {self.params}"
                        )
                        response = client.post(
                            url,
                            params=self.params,
                            headers=headers,
                            timeout=self.timeout,
                        )
                    elif self.method == "DELETE":
                        logger.debug(
                            f"Making DELETE request to {url} with params: {self.params}"
                        )
                        response = client.delete(
                            url,
                            params=self.params,
                            headers=headers,
                            timeout=self.timeout,
                        )
                    else:
                        logger.error(f"Unsupported HTTP method: {self.method}")
                        return None

                # Update rate limiter with response headers
                self.rate_limiter._updateLimits(response.headers)

                # Handle response status
                if response.status_code == 200:
                    # Successful response - increment the rate limiter usage
                    self.rate_limiter._incrementUsage(self.limit_type, self.weight)
                    return response.json()
                elif response.status_code == 429 or response.status_code == 418:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get("Retry-After", 1))
                    logger.warning(
                        f"Rate limit exceeded (status {response.status_code}), retrying after {retry_after}s"
                    )
                    time.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    # Other error
                    logger.error(
                        f"Error while making {self.method} request to {self.endpoint}: {response.text} (error code {response.status_code})"
                    )
                    return None

            except httpx.RequestError as e:
                # Network-related error
                if retries < max_retries:
                    current_delay = retry_delay * (2**retries)
                    logger.warning(
                        f"Request error: {str(e)}, retrying after {current_delay}s"
                    )
                    time.sleep(current_delay)
                    retries += 1
                    continue
                else:
                    logger.error(f"Max retries reached. Request error: {str(e)}")
                    return None

        # If we get here, we've exhausted retries
        logger.error(f"Failed to execute request after {max_retries} retries")
        return None

    def getRateLimitUsage(self) -> Dict[str, int]:
        """
        Get current rate limit usage information.

        Returns:
            Dictionary with rate limit usage statistics
        """
        return self.rate_limiter.getRateLimitUsage()


class RateLimiter:
    """
    Manages rate limits for Binance API requests.
    """

    def __init__(self):
        """Initialize the rate limiter with default limits"""
        # Default rate limits for Binance US
        self.rate_limits = [
            RateLimit(RateLimitType.REQUEST_WEIGHT, RateLimitInterval.MINUTE, 1, 1200),
            RateLimit(RateLimitType.ORDERS, RateLimitInterval.MINUTE, 1, 50),
            RateLimit(RateLimitType.RAW_REQUESTS, RateLimitInterval.MINUTE, 1, 6000),
        ]

        # Tracking current usage
        self.usage = {
            f"{limit.rateLimitType}_{limit.interval}_{limit.intervalNum}": 0
            for limit in self.rate_limits
        }

        # Timestamps for usage tracking
        self.reset_times = {
            f"{limit.rateLimitType}_{limit.interval}_{limit.intervalNum}": time.time()
            for limit in self.rate_limits
        }

        # Last response headers for updating limits
        self.last_headers = {}

    def _updateLimits(self, headers: Dict[str, str]):
        """
        Update rate limits based on response headers.
        """
        self.last_headers = dict(headers)

        # Update usage from headers if available
        # Format: X-MBX-USED-WEIGHT-1M
        for limit in self.rate_limits:
            interval_code = limit.interval.value[0]  # First letter of interval
            header_key = f"X-MBX-USED-{limit.rateLimitType.value}-{limit.intervalNum}{interval_code}"
            header_key = header_key.upper()

            if header_key in headers:
                usage_key = (
                    f"{limit.rateLimitType}_{limit.interval}_{limit.intervalNum}"
                )
                self.usage[usage_key] = int(headers[header_key])
                logger.debug(f"Updated {usage_key} usage to {self.usage[usage_key]}")

    def _checkRateLimit(self, limit_type: RateLimitType, weight: int = 1) -> bool:
        """
        Check if a request can be made without exceeding rate limits.
        """
        # Check and possibly reset each applicable limit
        now = time.time()
        for limit in self.rate_limits:
            if limit.rateLimitType == limit_type:
                key = f"{limit.rateLimitType}_{limit.interval}_{limit.intervalNum}"

                # Convert interval to seconds
                if limit.interval == RateLimitInterval.SECOND:
                    interval_seconds = 1
                elif limit.interval == RateLimitInterval.MINUTE:
                    interval_seconds = 60
                elif limit.interval == RateLimitInterval.HOUR:
                    interval_seconds = 3600
                elif limit.interval == RateLimitInterval.DAY:
                    interval_seconds = 86400
                else:
                    interval_seconds = 60  # Default to minute

                interval_duration = interval_seconds * limit.intervalNum

                # Reset usage if interval has passed
                if now - self.reset_times[key] >= interval_duration:
                    self.usage[key] = 0
                    self.reset_times[key] = now

                # Check if this request would exceed the limit
                if self.usage[key] + weight > limit.limit:
                    logger.warning(
                        f"Rate limit would be exceeded: {key} (current: {self.usage[key]}, request weight: {weight}, limit: {limit.limit})"
                    )
                    return False

        return True

    def _incrementUsage(self, limit_type: RateLimitType, weight: int = 1):
        """
        Increment usage counter for a rate limit.

        Args:
            limit_type: Type of rate limit
            weight: Weight of the request
        """
        for limit in self.rate_limits:
            if limit.rateLimitType == limit_type:
                key = f"{limit.rateLimitType}_{limit.interval}_{limit.intervalNum}"
                self.usage[key] += weight
                logger.debug(
                    f"Incremented {key} usage by {weight} to {self.usage[key]}"
                )

    def _getRetryAfter(self) -> int:
        """
        Get retry-after time from last response headers.

        Returns:
            Retry time in seconds, or 0 if not specified
        """
        if "Retry-After" in self.last_headers:
            return int(self.last_headers["Retry-After"])
        return 0

    def getRateLimitUsage(self) -> Dict[str, int]:
        """
        Get current rate limit usage.

        Returns:
            Dictionary with rate limit usage
        """
        return self.usage
