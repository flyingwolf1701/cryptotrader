# File: cryptotrader/services/cryptocom/restAPI/baseOperations.py
"""
Crypto.com Exchange Base Operations

This module provides the foundational infrastructure for making API requests to Crypto.com Exchange.
It handles:
- Request building, signing (HMAC SHA256), and execution
- Simple rate limiting per endpoint
- Error handling and retries
- HTTP client management
"""
import time
import json
import hmac
import hashlib
from typing import Optional, Any, Dict

import httpx

from cryptotrader.config import get_logger, Secrets

logger = get_logger(__name__)


class CryptoAPIRequest:
    """
    Builds and executes requests to the Crypto.com Exchange REST API.

    Uses HMAC-SHA256 signatures as required by the Exchange v1 API.
    """

    BASE_URL = "https://api.crypto.com/exchange/v1"

    def __init__(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new API request.

        Args:
            method: API method path (e.g., "public/get-book", "private/create-order").
            params: JSON-RPC parameters object.
        """
        self.method = method
        self.params = params or {}
        self.id = int(time.time() * 1000)
        self.nonce = int(time.time() * 1000)
        self.api_key = Secrets.CRYPTO_API_KEY
        self.secret_key = Secrets.CRYPTO_API_SECRET
        self.rate_limiter = RateLimiter()

    def _sign(self, payload: Dict[str, Any]) -> str:
        """
        Create HMAC-SHA256 signature of the JSON payload.
        """
        # Canonical JSON: sorted keys, no spaces
        body = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def execute(self, timeout: int = 10) -> Optional[Any]:
        """
        Execute the API request, handling rate limits and errors.

        Returns parsed JSON `result` on success or None on failure.
        """
        # Build JSON-RPC payload
        payload: Dict[str, Any] = {
            'id': self.id,
            'method': self.method,
            'params': self.params,
            'nonce': self.nonce,
        }
        if self.api_key:
            payload['api_key'] = self.api_key
        # Sign
        payload['sig'] = self._sign(payload)

        url = f"{self.BASE_URL}/{self.method}"
        headers = {'Content-Type': 'application/json'}

        # Rate limit check
        if not self.rate_limiter.check(self.method):
            retry = self.rate_limiter.get_retry_after(self.method)
            logger.warning(f"Rate limit hit for {self.method}, retrying after {retry}s")
            time.sleep(retry)

        try:
            resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
            self.rate_limiter.update(self.method, resp)
            resp.raise_for_status()
            data = resp.json()
            # Crypto.com returns code=0 on success
            if data.get('code') != 0:
                logger.error(f"API error {data.get('code')} on {self.method}: {data}")
                return None
            return data.get('result')
        except httpx.HTTPError as e:
            logger.error(f"HTTP error on {self.method}: {e}")
            return None


class RateLimiter:
    """
    Simple per-method rate limiter based on Crypto.com documented limits.
    """
    # Map method -> (interval_seconds, max_calls)
    DEFAULT_LIMITS: Dict[str, tuple] = {
        'private/create-order': (0.1, 15),  # 15 calls per 100ms
        'private/cancel-order': (0.1, 15),
        'private/cancel-all-orders': (0.1, 15),
        'private/get-order-detail': (0.1, 30),
        'private/get-trades': (1.0, 1),      # 1 call per second
        'private/get-order-history': (1.0, 1),
        # All others: 3 calls per 100ms
    }
    DEFAULT_LIMITS['default'] = (0.1, 3)

    def __init__(self):
        self.usage: Dict[str, int] = {}
        self.reset_at: Dict[str, float] = {}

    def check(self, method: str) -> bool:
        interval, limit = self.DEFAULT_LIMITS.get(method, self.DEFAULT_LIMITS['default'])
        now = time.time()
        last = self.reset_at.get(method, now)
        if now - last >= interval:
            self.usage[method] = 0
            self.reset_at[method] = now
        count = self.usage.get(method, 0)
        if count >= limit:
            return False
        self.usage[method] = count + 1
        return True

    def update(self, method: str, response: httpx.Response) -> None:
        # No dynamic limits exposed via headers for Crypto.com v1
        pass

    def get_retry_after(self, method: str) -> float:
        interval, _ = self.DEFAULT_LIMITS.get(method, self.DEFAULT_LIMITS['default'])
        return interval
