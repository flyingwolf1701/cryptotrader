# File: src/gui/components/logic/watchlist_logic.py
"""
Watchlist Logic

Handles fetching and updating symbol price data using the Unified Client.
"""

from typing import Callable, Optional
from config import get_logger
from src.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class WatchlistLogic:
    """Business logic for symbol price fetching and updates."""

    def __init__(self, client: Optional[BinanceRestUnifiedClient] = None):
        self.client = client or BinanceRestUnifiedClient()

    def fetch_symbol_data(self, symbol: str, callback: Callable[[str, dict], None]) -> None:
        """Fetch latest bid/ask prices for a symbol and pass to callback."""
        try:
            ticker = self.client.get_24h_ticker_price(symbol)
            if ticker:
                callback(symbol, ticker)
            else:
                logger.warning(f"No ticker data returned for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching ticker data for {symbol}: {e}")
