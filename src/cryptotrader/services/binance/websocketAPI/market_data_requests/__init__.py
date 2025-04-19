"""
Binance WebSocket API Module

This module provides a comprehensive client for interacting with the Binance WebSocket API,
including market data streams, user data streams, and trading operations.
"""

# Import base operations
from cryptotrader.services.binance.websocketAPI.base_operations import (
    BinanceWebSocketConnection,
    SecurityType
)

# order_book.py
from cryptotrader.services.binance.websocketAPI.market_data_requests.order_book import (
    get_order_book,
    process_order_book_response
)

# recent_trades.py
from cryptotrader.services.binance.websocketAPI.market_data_requests.recent_trades import (
    get_recent_trades,
    process_recent_trades_response
)

# historical_trades.py
from cryptotrader.services.binance.websocketAPI.market_data_requests.historical_trades import (
    get_historical_trades,
    process_historical_trades_response
)

# klines.py
from cryptotrader.services.binance.websocketAPI.market_data_requests.klines import (
    get_klines,
    process_klines_response
)

__all__ = [
    # Base operations
    'BinanceWebSocketConnection',
    'SecurityType',
    
    # order_book.py
    'get_order_book',
    'process_order_book_response',
    
    # recent_trades.py
    'get_recent_trades',
    'process_recent_trades_response',
    
    # historical_trades.py
    'get_historical_trades',
    'process_historical_trades_response',
    
    # klines.py
    'get_klines',
    'process_klines_response'
]