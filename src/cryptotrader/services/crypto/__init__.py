"""High‑level unified client mirroring BinanceRestUnifiedClient surface."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from cryptotrader.config import get_logger
from .base_operations import CryptoBaseOperations

logger = get_logger(__name__)


class CryptoComRestUnifiedClient(CryptoBaseOperations):
    """Subset of endpoints required by existing app logic."""

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------
    def get_exchange_info(self) -> Dict[str, Any]:
        """Return symbol metadata (mirror Binance get_exchange_info)."""
        # Crypto.com: /public/get-instruments
        return self._request("GET", "/public/get-instruments")

    def get_ticker_24h(self, instrument_name: str) -> Dict[str, Any]:
        """24h stats; instrument_name like "BTC_USDT"."""
        return self._request(
            "GET", "/public/get-ticker", instrument_name=instrument_name
        )

    # ------------------------------------------------------------------
    # Account / Orders (minimal for watchlist & PnL)
    # ------------------------------------------------------------------
    def get_account_summary(self) -> Dict[str, Any]:
        return self._request("POST", "/private/get-account-summary")

    def place_order(
        self,
        instrument_name: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Simple order placement (LIMIT or MARKET)."""
        return self._request(
            "POST",
            "/private/create-order",
            instrument_name=instrument_name,
            side=side,
            type=type_,
            price=price,
            quantity=quantity,
        )

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return self._request("POST", "/private/cancel-order", order_id=order_id)

    def get_my_trades(self, instrument_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Mirror Binance `get_my_trades`."""
        res = self._request(
            "POST", "/private/get-trades", instrument_name=instrument_name, **kwargs
        )
        return res.get("data", [])
