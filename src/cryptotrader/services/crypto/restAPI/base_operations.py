"""Shared helpers: timestamp, signature, and HTTP request wrapper.
Inspired by Binance `BaseOperations`, adapted for Crypto.com Exchange.
Assumptions based on exchange docs (https://exchange-docs.crypto.com).
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, Optional

import httpx

from cryptotrader.config import get_logger

logger = get_logger(__name__)


class CryptoBaseOperations:
    """Low‑level HTTP helper with HMAC SHA256 signing."""

    BASE_URL = "https://api.crypto.com/v2"

    def __init__(self, api_key: str, api_secret: str, *, testnet: bool = False):
        if testnet:
            # Sandbox host from docs
            self.BASE_URL = "https://uat-api.crypto.com/v2"
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.client = httpx.Client(base_url=self.BASE_URL, timeout=10.0)

    # ------------------------------------------------------------------
    # Signing helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _nonce() -> str:
        """Return ms‑precision unix time as string."""
        return str(int(time.time() * 1000))

    def _sign(self, method: str, path: str, params: Dict[str, Any]) -> str:
        """Create Crypto.com HMAC signature.
        Per docs signature = HMAC_SHA256(secret, method + path + nonce + sorted_params_json)
        """
        nonce = params.get("nonce") or self._nonce()
        params["nonce"] = nonce
        param_str = "" if not params else httpx.QueryParams(params).encode()
        payload = f"{method}{path}{nonce}{param_str}"
        digest = hmac.new(self.api_secret, payload.encode(), hashlib.sha256).hexdigest()
        return digest

    # ------------------------------------------------------------------
    # Request executor
    # ------------------------------------------------------------------
    def _request(self, method: str, path: str, **params) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{path}"
        # inject api_key & nonce
        params = {k: v for k, v in params.items() if v is not None}
        params["api_key"] = self.api_key
        params["nonce"] = self._nonce()
        sig = self._sign(method, path, params)
        params["sig"] = sig

        logger.debug("Request %s %s params=%s", method, url, params)
        r = self.client.request(
            method,
            url,
            json=params if method == "POST" else None,
            params=params if method == "GET" else None,
        )
        r.raise_for_status()
        data = r.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Crypto.com API error: {data}")
        return data.get("result", {})
