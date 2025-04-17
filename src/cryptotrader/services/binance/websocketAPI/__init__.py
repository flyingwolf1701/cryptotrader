"""
Binance WebSocket API Module

This module provides a comprehensive client for interacting with the Binance WebSocket API,
including market data streams, user data streams, and trading operations.
"""

# Import base operations
from cryptotrader.services.binance.websocketAPI.base_operations import (
    BinanceWebSocketConnection,
    BinanceWebSocketClient
)

__all__ = [
    # Client classes
    'BinanceWebSocketConnection',
    'BinanceWebSocketClient',
]