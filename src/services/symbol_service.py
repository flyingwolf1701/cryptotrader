# src/services/symbol_service.py
"""
Symbol Service

Provides centralized access to available trading symbols.
Acts as a service layer between the exchange API and UI components.
"""

import threading
from typing import List, Callable, Set, Optional

from src.config import get_logger
from src.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)

class SymbolService:
    """Service for retrieving and managing available trading symbols."""
    
    _instance = None
    _lock = threading.Lock()
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of SymbolService."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = SymbolService()
            return cls._instance
    
    def __init__(self):
        """Initialize the symbol service."""
        self.client = BinanceRestUnifiedClient()
        self.available_symbols: List[str] = []
        self.popular_symbols: List[str] = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Default fallback
        self.is_initialized: bool = False
        self.on_symbols_updated: Set[Callable[[List[str]], None]] = set()
        
        # Fetch symbols asynchronously at startup
        self._initialize_async()
    
    def _initialize_async(self):
        """Initialize symbol data asynchronously."""
        thread = threading.Thread(target=self._fetch_symbols)
        thread.daemon = True
        thread.start()
    
    def _fetch_symbols(self):
        """Fetch available symbols from the exchange."""
        try:
            # Use system client to get exchange info
            exchange_info = self.client.system.get_exchange_info()
            
            if exchange_info and 'symbols' in exchange_info:
                symbols = [
                    symbol['symbol'] for symbol in exchange_info['symbols']
                    if symbol.get('status') == 'TRADING'
                ]
                
                if symbols:
                    self.available_symbols = sorted(symbols)
                    # Notify listeners
                    self._notify_listeners()
                    self.is_initialized = True
                    logger.info(f"SymbolService loaded {len(symbols)} trading symbols")
                    return
            
            logger.warning("Failed to fetch symbols from exchange")
        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")
        
        # If we get here, there was an error - use fallback
        self.available_symbols = self.popular_symbols
        self._notify_listeners()
        self.is_initialized = True
    
    def get_symbols(self) -> List[str]:
        """Get the list of available trading symbols."""
        return self.available_symbols
    
    def is_valid_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid."""
        return symbol in self.available_symbols
    
    def register_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Register a listener for symbol updates."""
        self.on_symbols_updated.add(callback)
        # Immediately notify if data is already available
        if self.is_initialized:
            callback(self.available_symbols)
    
    def unregister_listener(self, callback: Callable[[List[str]], None]) -> None:
        """Unregister a listener."""
        if callback in self.on_symbols_updated:
            self.on_symbols_updated.remove(callback)
    
    def _notify_listeners(self) -> None:
        """Notify all listeners of symbol updates."""
        for callback in self.on_symbols_updated:
            try:
                callback(self.available_symbols)
            except Exception as e:
                logger.error(f"Error notifying symbol listener: {str(e)}")
    
    def get_popular_symbols(self, limit: int = 5) -> List[str]:
        """Get a list of popular trading symbols."""
        # In a real implementation, this might use volume data to determine popularity
        return self.popular_symbols[:limit]