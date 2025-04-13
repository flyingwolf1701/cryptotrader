"""
Binance Unified Client

This module provides a high-level client that combines both REST and WebSocket
functionality for interacting with the Binance API.

The unified client serves as the main entry point for applications using this library,
offering access to all Binance API features through a single, consistent interface.

Key features:
- Combined REST and WebSocket access
- Automatic fallback from WebSocket to REST when needed
- Simplified API for common trading operations
- Comprehensive error handling and retry logic
- Rate limit management and optimization

This class follows the facade pattern, providing a simpler interface to the
underlying REST and WebSocket clients while handling the coordination between them.

Usage:
    client = Client(api_key, api_secret)
    
    # Get real-time price updates
    client.subscribe_channel("BTCUSDT", ["bookTicker"])
    
    # Place an order
    client.place_order(OrderRequest(...))
    
    # Check system status
    status = client.get_system_status()
"""

from typing import Dict, List, Optional, Any, Union, Callable

from cryptotrader.services.binance.binance_models import (
    PriceData, OrderRequest, Candle, AccountBalance, 
    OrderStatusResponse, SymbolInfo, SystemStatus, SelfTradePreventionMode
)
from cryptotrader.services.binance.binance_rest_client import RestClient
from cryptotrader.services.binance.binance_ws_client import WebSocketClient

from cryptotrader.config import get_logger
logger = get_logger(__name__)


class Client:
    """
    Unified Binance API client that combines REST and WebSocket functionality.
    
    This client serves as the main entry point for interacting with the Binance API,
    providing access to both REST endpoints and WebSocket streams.
    """
    
    def __init__(self, public_key: str, secret_key: str):
        """
        Initialize the Binance client.
        
        Args:
            public_key: The Binance API key
            secret_key: The Binance API secret
        """
        # Initialize the underlying clients
        self.rest_client = RestClient(public_key, secret_key)
        self.ws_client = WebSocketClient(callback=self._ws_callback)
        
        # Start the WebSocket client
        self.ws_client.start()
        
        logger.info("Binance Client successfully initialized")
    
    def _ws_callback(self, event_type: str, data: Dict[str, Any]):
        """
        Callback for WebSocket events.
        
        This can be extended to implement custom event handling for WebSocket data.
        """
        # Currently just log the event, but could do more complex handling
        logger.debug(f"WebSocket event: {event_type}")
    
    #
    # WebSocket methods
    #
    
    def subscribe_channel(self, symbol: str, streams: Optional[List[str]] = None):
        """
        Subscribe to WebSocket channels for a symbol.
        
        Args:
            symbol: The symbol to subscribe to (e.g. "BTCUSDT")
            streams: List of stream types. Default is ["bookTicker"].
                     Options include:
                     - "bookTicker" - Best bid/ask updates
                     - "kline_1m", "kline_5m", etc. - Candlestick updates
                     - "trade" - Real-time trade data
                     - "aggTrade" - Aggregate trade data
        """
        self.ws_client.subscribe(symbol, streams)
    
    def unsubscribe_channel(self, symbol: str, streams: Optional[List[str]] = None):
        """
        Unsubscribe from WebSocket channels for a symbol.
        
        Args:
            symbol: The symbol to unsubscribe from (e.g. "BTCUSDT")
            streams: List of stream types to unsubscribe from.
                     If None, unsubscribes from all streams for this symbol.
        """
        self.ws_client.unsubscribe(symbol, streams)
    
    #
    # Market data methods
    #
    
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        """
        Get current bid/ask prices for a symbol.
        
        First tries to get the price from WebSocket cache (most up-to-date),
        then falls back to REST API if needed.
        
        Args:
            symbol: The symbol to get prices for (e.g. "BTCUSDT")
            
        Returns:
            PriceData object with bid and ask prices, or None if not available
        """
        # Try WebSocket cached price first (more real-time)
        ws_price = self.ws_client.get_price(symbol)
        if ws_price:
            return ws_price
        
        # Fall back to REST API
        return self.rest_client.get_bid_ask(symbol)
    
    def get_historical_candles(self, symbol: str, interval: str, 
                              limit: int = 500, 
                              start_time: Optional[int] = None,
                              end_time: Optional[int] = None) -> List[Candle]:
        """
        Get historical candlestick data.
        
        Args:
            symbol: Symbol to get candles for (e.g. "BTCUSDT")
            interval: Candle interval (e.g. "1m", "1h", "1d")
            limit: Number of candles to return (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of Candle objects
        """
        return self.rest_client.get_historical_candles(
            symbol, interval, limit, start_time, end_time
        )
    
    #
    # Account methods
    #
    
    def get_balance(self) -> AccountBalance:
        """
        Get account balance information.
        
        Returns:
            AccountBalance object with asset balances
        """
        return self.rest_client.get_balance()
    
    def place_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> Optional[OrderStatusResponse]:
        """
        Place a new order.
        
        Args:
            order_request: The order details as OrderRequest object or dictionary
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.rest_client.place_order(order_request)
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, 
                   client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """
        Cancel an existing order.
        
        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.rest_client.cancel_order(symbol, order_id, client_order_id)
    
    def get_order_status(self, symbol: str, order_id: Optional[int] = None, 
                       client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """
        Get status of an existing order.
        
        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        return self.rest_client.get_order_status(symbol, order_id, client_order_id)
    
    #
    # Exchange information methods
    #
    
    def get_exchange_info(self, symbol: Optional[str] = None,
                         symbols: Optional[List[str]] = None,
                         permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange information.
        
        Args:
            symbol: Single symbol to get info for
            symbols: Multiple symbols to get info for
            permissions: Permissions to filter by (e.g. ["SPOT"])
            
        Returns:
            Dictionary containing exchange information
        """
        return self.rest_client.get_exchange_info(symbol, symbols, permissions)
    
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Get information for a specific symbol.
        
        Args:
            symbol: The symbol to get information for (e.g. "BTCUSDT")
            
        Returns:
            SymbolInfo object with symbol details, or None if not found
        """
        return self.rest_client.get_symbol_info(symbol)
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """
        Get available trading symbols.
        
        Returns:
            List of available trading symbols
        """
        return RestClient.get_symbols_binance()
    
    def get_server_time(self) -> int:
        """
        Get current server time.
        
        Returns:
            Server time in milliseconds
        """
        return self.rest_client.get_server_time()
    
    def check_server_time(self) -> int:
        """
        Check time difference between local and server time.
        
        Returns:
            Time difference in milliseconds
        """
        return self.rest_client.check_server_time()
    
    def get_system_status(self) -> SystemStatus:
        """
        Get system status.
        
        Returns:
            SystemStatus object with status code (0: normal, 1: maintenance)
        """
        return self.rest_client.get_system_status()
    
    def get_self_trade_prevention_modes(self) -> Dict[str, Any]:
        """
        Get self-trade prevention modes from exchange info.
        
        Returns:
            Dictionary with default and allowed modes
        """
        return self.rest_client.get_self_trade_prevention_modes()
    
    def get_rate_limit_usage(self) -> Dict[str, int]:
        """
        Get current rate limit usage information.
        
        Returns:
            Dictionary with rate limit usage details
        """
        return self.rest_client.rate_limiter.get_rate_limit_usage()
    
    def __del__(self):
        """Cleanup resources when instance is being destroyed"""
        # Clean up the clients
        if hasattr(self, 'ws_client'):
            self.ws_client.close()