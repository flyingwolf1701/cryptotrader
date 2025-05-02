# File: src/gui/components/logic/watchlist_logic.py
"""
Watchlist Logic

Handles symbol validation, searching, and fetching price updates using the Unified Client.
"""

from typing import Callable, Optional, List
from config import get_logger
from cryptotrader.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class WatchlistLogic:
    """Business logic for symbol validation, lookup, and price updates."""

    def __init__(self, client: Optional[BinanceRestUnifiedClient] = None):
        # Use provided client or default to BinanceRestUnifiedClient
        self.client = client or BinanceRestUnifiedClient()

    def fetch_symbol_data(self, symbol: str, callback: Callable[[str, dict], None]) -> None:
        """Fetch latest bid/ask prices for a symbol and invoke the callback."""
        try:
            ticker = self.client.get_24h_ticker_price(symbol)
            if ticker:
                callback(symbol, ticker)
            else:
                logger.warning(f"No ticker data returned for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching ticker data for {symbol}: {e}")

    def search_symbols(self, query: str) -> List[str]:
        """Return a sorted list of symbols containing the query substring (case-insensitive)."""
        try:
            # Retrieves a Set[str] of symbols from unified client
            all_syms = self.client.get_binance_symbols()
            q = query.strip().upper()
            # Filter symbols by substring match
            matches = [sym for sym in all_syms if q in sym]
            return sorted(matches)
        except Exception as e:
            logger.error(f"Error searching symbols for query '{query}': {e}")
            return []

    def validate_symbol(self, symbol: str) -> bool:
        """Check if the exact symbol exists on Binance."""
        try:
            # Exact membership check against Set[str]
            return symbol.strip().upper() in self.client.get_binance_symbols()
        except Exception as e:
            logger.error(f"Error validating symbol '{symbol}': {e}")
            return False
