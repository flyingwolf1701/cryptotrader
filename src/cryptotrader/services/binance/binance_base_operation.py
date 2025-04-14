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

from cryptotrader.config import get_logger, settings
from cryptotrader.services.binance.binance_models import (
    RateLimit, RateLimitType, RateLimitInterval, BinanceEndpoints
)

logger = get_logger(__name__)

class BinanceAPIRequest:
    """
    Builds and executes requests to the Binance API.
    
    Handles authentication, signing, parameter formatting, and error handling.
    Includes integrated rate limiting to prevent API request limit violations.
    """
    whatsYourSecre = settings.Secrets.BINANCE_API_KEY
    
    def __init__(self, method: str, endpoint: str, 
                public_key: str = settings.Secrets.BINANCE_API_KEY, 
                secret_key: str = settings.Secrets.BINANCE_API_SECRET, 
                limit_type: RateLimitType = RateLimitType.REQUEST_WEIGHT,
                weight: int = 1,
                base_url: str = "https://api.binance.us/",
                timeout: int = 10):
        """
        Initialize a new API request.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            public_key: Binance API key for authentication
            secret_key: Binance API secret for signing
            limit_type: Type of rate limit for this request
            weight: Weight of this request for rate limiting
            base_url: Base URL for Binance API
            timeout: Request timeout in seconds
        """
        self.method = method
        self.endpoint = endpoint
        self.public_key = public_key
        self.secret_key = secret_key
        self.limit_type = limit_type
        self.weight = weight
        self.base_url = base_url
        self.timeout = timeout
        
        # Initialize internal rate limiter
        self.rate_limiter = RateLimiter()
        
        self.params = {}
        self.needs_signature = public_key is not None and secret_key is not None
    
    def with_query_params(self, **kwargs) -> 'BinanceAPIRequest':
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
    
    def sign_request(self) -> None:
        """
        Sign the request with the API secret.
        
        Adds timestamp and signature to the parameters.
        """
        # Add timestamp
        self.params['timestamp'] = str(int(time.time() * 1000))
        
        # Create signature
        query_string = urllib.parse.urlencode(self.params)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Add signature to params
        self.params['signature'] = signature
    
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
                if not self.rate_limiter.check_rate_limit(self.limit_type, self.weight):
                    retry_after = self.rate_limiter.get_retry_after()
                    if retry_after > 0:
                        logger.warning(f"Rate limit hit, retrying after {retry_after}s")
                        time.sleep(retry_after)
                    else:
                        # Use exponential backoff
                        current_delay = retry_delay * (2 ** retries)
                        logger.warning(f"Rate limit hit, retrying after {current_delay}s")
                        time.sleep(current_delay)
                    retries += 1
                    continue
                
                # Sign the request if needed
                if self.needs_signature:
                    self.sign_request()
                
                # Set up headers
                headers = {}
                if self.public_key:
                    headers['X-MBX-APIKEY'] = self.public_key
                
                # Execute the request
                with httpx.Client() as client:
                    if self.method == 'GET':
                        logger.debug(f"Making GET request to {url} with params: {self.params}")
                        response = client.get(
                            url, 
                            params=self.params, 
                            headers=headers,
                            timeout=self.timeout
                        )
                    elif self.method == 'POST':
                        logger.debug(f"Making POST request to {url} with params: {self.params}")
                        response = client.post(
                            url, 
                            params=self.params, 
                            headers=headers,
                            timeout=self.timeout
                        )
                    elif self.method == 'DELETE':
                        logger.debug(f"Making DELETE request to {url} with params: {self.params}")
                        response = client.delete(
                            url, 
                            params=self.params, 
                            headers=headers,
                            timeout=self.timeout
                        )
                    else:
                        logger.error(f"Unsupported HTTP method: {self.method}")
                        return None
                
                # Update rate limiter with response headers
                self.rate_limiter.update_limits(response.headers)
                
                # Handle response status
                if response.status_code == 200:
                    # Successful response - increment the rate limiter usage
                    self.rate_limiter.increment_usage(self.limit_type, self.weight)
                    return response.json()
                elif response.status_code == 429 or response.status_code == 418:
                    # Rate limit exceeded
                    retry_after = int(response.headers.get('Retry-After', 1))
                    logger.warning(f"Rate limit exceeded (status {response.status_code}), retrying after {retry_after}s")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                else:
                    # Other error
                    logger.error(f"Error while making {self.method} request to {self.endpoint}: {response.text} (error code {response.status_code})")
                    return None
                
            except httpx.RequestError as e:
                # Network-related error
                if retries < max_retries:
                    current_delay = retry_delay * (2 ** retries)
                    logger.warning(f"Request error: {str(e)}, retrying after {current_delay}s")
                    time.sleep(current_delay)
                    retries += 1
                    continue
                else:
                    logger.error(f"Max retries reached. Request error: {str(e)}")
                    return None
        
        # If we get here, we've exhausted retries
        logger.error(f"Failed to execute request after {max_retries} retries")
        return None
        
    def get_rate_limit_usage(self) -> Dict[str, int]:
        """
        Get current rate limit usage information.
        
        Returns:
            Dictionary with rate limit usage statistics
        """
        return self.rate_limiter.get_rate_limit_usage()

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
            RateLimit(RateLimitType.RAW_REQUESTS, RateLimitInterval.MINUTE, 1, 6000)
        ]
        
        # Tracking current usage
        self.usage = {
            f"{limit.rate_limit_type}_{limit.interval}_{limit.interval_num}": 0
            for limit in self.rate_limits
        }
        
        # Timestamps for usage tracking
        self.reset_times = {
            f"{limit.rate_limit_type}_{limit.interval}_{limit.interval_num}": time.time()
            for limit in self.rate_limits
        }
        
        # Last response headers for updating limits
        self.last_headers = {}
    
    def update_limits(self, headers: Dict[str, str]):
        """
        Update rate limits based on response headers.
        """
        self.last_headers = dict(headers)
        
        # Update usage from headers if available
        # Format: X-MBX-USED-WEIGHT-1M
        for limit in self.rate_limits:
            interval_code = limit.interval.value[0]  # First letter of interval
            header_key = f"X-MBX-USED-{limit.rate_limit_type.value}-{limit.interval_num}{interval_code}"
            header_key = header_key.upper()
            
            if header_key in headers:
                usage_key = f"{limit.rate_limit_type}_{limit.interval}_{limit.interval_num}"
                self.usage[usage_key] = int(headers[header_key])
                logger.debug(f"Updated {usage_key} usage to {self.usage[usage_key]}")
    
    def check_rate_limit(self, limit_type: RateLimitType, weight: int = 1) -> bool:
        """
        Check if a request can be made without exceeding rate limits.
        """
        # Check and possibly reset each applicable limit
        now = time.time()
        for limit in self.rate_limits:
            if limit.rate_limit_type == limit_type:
                key = f"{limit.rate_limit_type}_{limit.interval}_{limit.interval_num}"
                
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
                
                interval_duration = interval_seconds * limit.interval_num
                
                # Reset usage if interval has passed
                if now - self.reset_times[key] >= interval_duration:
                    self.usage[key] = 0
                    self.reset_times[key] = now
                
                # Check if this request would exceed the limit
                if self.usage[key] + weight > limit.limit:
                    logger.warning(f"Rate limit would be exceeded: {key} (current: {self.usage[key]}, request weight: {weight}, limit: {limit.limit})")
                    return False
        
        return True
    
    def increment_usage(self, limit_type: RateLimitType, weight: int = 1):
        """
        Increment usage counter for a rate limit.
        
        Args:
            limit_type: Type of rate limit
            weight: Weight of the request
        """
        for limit in self.rate_limits:
            if limit.rate_limit_type == limit_type:
                key = f"{limit.rate_limit_type}_{limit.interval}_{limit.interval_num}"
                self.usage[key] += weight
                logger.debug(f"Incremented {key} usage by {weight} to {self.usage[key]}")
    
    def get_retry_after(self) -> int:
        """
        Get retry-after time from last response headers.
        
        Returns:
            Retry time in seconds, or 0 if not specified
        """
        if 'Retry-After' in self.last_headers:
            return int(self.last_headers['Retry-After'])
        return 0
    
    def get_rate_limit_usage(self) -> Dict[str, int]:
        """
        Get current rate limit usage.
        
        Returns:
            Dictionary with rate limit usage
        """
        return self.usage

    # Create a request to extract rate limit info if needed
        self._rate_limit_request = self.request("GET", "/api/v3/time")