"""
Unified client for Crypto.com REST API.
Follows the BinanceRestUnifiedClient composition pattern: uses CryptoBaseOperations and free API functions.
"""
from typing import Any, Dict, List, Optional
from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.crypto.restAPI.crypto_api_request import CryptoBaseOperations
from cryptotrader.services.crypto.restAPI.crypto_api import (
    get_exchange_info,
    get_ticker_24h,
    get_account_summary,
    place_order,
    cancel_order,
    get_my_trades,
)

logger = get_logger(__name__)

class CryptoRestUnifiedClient:
    """High-level unified client for Crypto.com REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False
    ):
        """
        :param api_key: Crypto.com API key (defaults to Secrets.CRYPTO_API_KEY)
        :param api_secret: Crypto.com API secret (defaults to Secrets.CRYPTO_API_SECRET)
        :param testnet: If True, use the testnet endpoint
        """
        self.logger = get_logger(__name__)
        key = api_key or Secrets.CRYPTO_API_KEY
        secret = api_secret or Secrets.CRYPTO_API_SECRET
        self.client = CryptoBaseOperations(key, secret, testnet=testnet)

    def get_exchange_info(self) -> Dict[str, Any]:
        return get_exchange_info(self.client)

    def get_ticker_24h(self, instrument_name: str) -> Dict[str, Any]:
        return get_ticker_24h(self.client, instrument_name)

    def get_account_summary(self) -> Dict[str, Any]:
        return get_account_summary(self.client)

    def place_order(
        self,
        instrument_name: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        return place_order(
            self.client, instrument_name, side, type_, quantity, price
        )

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return cancel_order(self.client, order_id)

    def get_my_trades(
        self, instrument_name: str, **kwargs
    ) -> List[Dict[str, Any]]:
        return get_my_trades(self.client, instrument_name, **kwargs)
