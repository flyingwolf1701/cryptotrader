# File: src/gui/components/logic/symbol_search_logic.py
"""
Business logic for fetching, caching, and filtering trading symbols.
"""
import threading
from typing import List, Set, Callable, Optional
from src.config import get_logger

from src.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class SymbolSearchLogic:
    """Logic for loading and filtering trading symbols (cached)."""
    def __init__(
        self,
        client: Optional[BinanceRestUnifiedClient] = None
    ):
        # Injected REST client (defaults to real unified client)
        self.client = client or BinanceRestUnifiedClient()
        # Cached symbol lists
        self.available_symbols: List[str] = []
        self.filtered_symbols: List[str] = []
        # Listener callbacks
        self.on_symbols_updated: Set[Callable[[List[str]], None]] = set()
        self.on_filtered_symbols_updated: Set[Callable[[List[str]], None]] = set()
        self.is_initialized: bool = False

    def initialize(self) -> None:
        """Start one-time asynchronous fetch of symbols."""
        thread = threading.Thread(target=self._fetch_symbols, daemon=True)
        thread.start()

    def _fetch_symbols(self) -> None:
        """Fetch symbols once, populate cache, notify listeners."""
        try:
            # Fetch exchange info via MarketOperations REST method
            # Try standard and REST-specific methods for exchange info
            if hasattr(self.client.market, 'get_exchange_info'):
                exchange_info = self.client.market.get_exchange_info()
            elif hasattr(self.client.market, 'get_exchange_info_rest'):
                exchange_info = self.client.market.get_exchange_info_rest()
            else:
                raise AttributeError("MarketOperations client missing exchange info method")

            symbols = []
            if exchange_info and 'symbols' in exchange_info:
                symbols = [s['symbol'] for s in exchange_info['symbols'] if s.get('status') == 'TRADING']

            if symbols:
                self.available_symbols = sorted(symbols)
                self.filtered_symbols = list(self.available_symbols)
                self.is_initialized = True
                self._notify_symbols_updated()
                self._notify_filtered_symbols_updated()
                logger.info(f"Loaded {len(symbols)} trading symbols")
                return

            logger.warning("No trading symbols found in exchange_info")
        except AttributeError:
            logger.error("MarketOperations client missing 'get_exchange_info' or 'get_exchange_info_rest' method")
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")

        # Fallback static list
        fallback = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        self.available_symbols = fallback
        self.filtered_symbols = list(fallback)
        self.is_initialized = True
        self._notify_symbols_updated()
        self._notify_filtered_symbols_updated()

    def filter_symbols(self, search_text: str) -> None:
        """Filter cached symbols by search_text (case-insensitive)."""
        if not search_text:
            self.filtered_symbols = list(self.available_symbols)
        else:
            text = search_text.upper()
            # Exact match first
            exact = [s for s in self.available_symbols if s == text]
            if exact:
                self.filtered_symbols = exact
            else:
                # Contains match
                contains = [s for s in self.available_symbols if text in s]
                if contains:
                    self.filtered_symbols = contains
                else:
                    # Split pairs into base/quote
                    quote_currencies = ["USDT", "BTC", "ETH", "BNB", "BUSD", "USD", "EUR"]
                    base_matches = []
                    quote_matches = []
                    for s in self.available_symbols:
                        quote = next((q for q in quote_currencies if s.endswith(q)), None)
                        base = s[:-len(quote)] if quote else s[:-3]
                        if text in base:
                            base_matches.append(s)
                        elif quote and text in quote:
                            quote_matches.append(s)
                    self.filtered_symbols = base_matches + quote_matches
        self._notify_filtered_symbols_updated()

    def register_symbols_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Register for updates to the full symbol list."""
        self.on_symbols_updated.add(callback)
        if self.is_initialized:
            callback(self.available_symbols)

    def unregister_symbols_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Unregister a full-symbols listener."""
        self.on_symbols_updated.discard(callback)

    def register_filtered_symbols_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Register for updates to the filtered symbol list."""
        self.on_filtered_symbols_updated.add(callback)
        if self.is_initialized:
            callback(self.filtered_symbols)

    def unregister_filtered_symbols_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Unregister a filtered-symbols listener."""
        self.on_filtered_symbols_updated.discard(callback)

    def _notify_symbols_updated(self) -> None:
        """Notify all listeners of available_symbols change."""
        for cb in list(self.on_symbols_updated):
            try:
                cb(self.available_symbols)
            except Exception as e:
                logger.error(f"Listener error (symbols): {e}")

    def _notify_filtered_symbols_updated(self) -> None:
        """Notify all listeners of filtered_symbols change."""
        for cb in list(self.on_filtered_symbols_updated):
            try:
                cb(self.filtered_symbols)
            except Exception as e:
                logger.error(f"Listener error (filtered): {e}")

    def get_all_symbols(self) -> List[str]:
        """Return the full list of symbols."""
        return self.available_symbols

    def get_filtered_symbols(self) -> List[str]:
        """Return the current filtered symbols."""
        return self.filtered_symbols
