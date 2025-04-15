import json
import time
import asyncio
import threading
import websockets
from typing import Dict, List, Set, Optional, Any, Callable

from cryptotrader.services.binance.models.base_models import (
    BinanceEndpoints, PriceData, Candle
)

from cryptotrader.config import get_logger
logger = get_logger(__name__)


class WebSocketClient:
    """
    Binance WebSocket client for real-time market data.
    
    This client handles WebSocket connections to Binance's streaming API,
    providing real-time market data such as price tickers and candlestick updates.
    """
    
    def __init__(self, callback: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        """
        Initialize the WebSocket client.
        
        Args:
            callback: Optional callback function to process received data.
                     The callback receives (event_type, data) arguments.
        """
        # Initialize endpoints
        endpoints = BinanceEndpoints()
        self.wss_url = endpoints.wss_url
        
        # WebSocket state
        self.ws = None
        self.ws_connected = False
        self.ws_loop = None
        self.ws_thread = None
        self.callback = callback
        
        # Message ID counter for message tracking
        self.id = 1
        
        # Tracking subscriptions for reconnection
        self.subscriptions: Set[str] = set()
        self.subscription_params: Dict[str, List[str]] = {}
        
        # Connection health tracking
        self.last_ping = 0
        self.last_message = 0
        
        # Market data
        self.prices: Dict[str, PriceData] = {}
        self.candles: Dict[str, Dict[str, List[Candle]]] = {}
    
    def start(self):
        """Start the WebSocket connection in a background thread"""
        if self.ws_thread and self.ws_thread.is_alive():
            logger.info("WebSocket client already running")
            return
            
        self.ws_thread = threading.Thread(target=self._start_ws_thread, daemon=True)
        self.ws_thread.start()
        logger.info("WebSocket client thread started")
        
    def _start_ws_thread(self):
        """Thread function that runs the WebSocket event loop"""
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        self.ws_loop.run_until_complete(self._ws_handler())
        
    async def _ws_handler(self):
        """Main WebSocket connection handler"""
        reconnect_delay = 1  # Start with 1 second delay
        
        while True:
            try:
                logger.info("Connecting to Binance WebSocket...")
                async with websockets.connect(self.wss_url) as websocket:
                    self.ws = websocket
                    self.ws_connected = True
                    self.last_message = time.time()
                    self.last_ping = time.time()
                    
                    logger.info("Binance WebSocket Connection Opened")
                    
                    # Reset reconnect delay on successful connection
                    reconnect_delay = 1
                    
                    # Resubscribe to existing channels
                    await self._resubscribe_all()
                    
                    # Setup ping task for connection health
                    ping_task = asyncio.create_task(self._ping_websocket())
                    health_check_task = asyncio.create_task(self._check_connection_health())
                    
                    # Listen for messages
                    try:
                        while True:
                            message = await websocket.recv()
                            self.last_message = time.time()
                            await self._on_message(message)
                    finally:
                        # Cancel background tasks when main loop exits
                        ping_task.cancel()
                        health_check_task.cancel()
                        
            except websockets.exceptions.ConnectionClosed as e:
                self.ws_connected = False
                self.ws = None
                logger.warning(f"Binance WebSocket connection closed: {e}")
            except Exception as e:
                self.ws_connected = False
                self.ws = None
                logger.error(f"Binance WebSocket error: {e}")
            
            # Exponential backoff for reconnection attempts
            logger.info(f"Reconnecting to WebSocket in {reconnect_delay} seconds...")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)  # Double delay, max 60 seconds
    
    async def _resubscribe_all(self):
        """Resubscribe to all previously subscribed channels after reconnection"""
        for symbol in self.subscriptions:
            streams = self.subscription_params.get(symbol, ["bookTicker"])
            await self._subscribe(symbol, streams)
            
            # Add small delay to avoid overwhelming the connection
            await asyncio.sleep(0.1)
    
    async def _ping_websocket(self):
        """Send periodic pings to keep WebSocket connection alive"""
        while True:
            try:
                if self.ws_connected and self.ws:
                    # Send ping every 30 seconds
                    if time.time() - self.last_ping > 30:
                        await self.ws.ping()
                        self.last_ping = time.time()
                        logger.debug("Sent WebSocket ping")
            except Exception as e:
                logger.error(f"Error in WebSocket ping: {e}")
            
            await asyncio.sleep(15)
    
    async def _check_connection_health(self):
        """Check connection health and reconnect if needed"""
        while True:
            try:
                if self.ws_connected and time.time() - self.last_message > 120:
                    logger.warning("No messages received for 120 seconds, reconnecting...")
                    if self.ws:
                        await self.ws.close()
                    self.ws_connected = False
            except Exception as e:
                logger.error(f"Error in connection health check: {e}")
            
            await asyncio.sleep(30)
    
    async def _on_message(self, message):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            logger.debug(f"Received WS: {message[:100]}...")
            
            # Extract event type
            event_type = None
            
            # Handle different message types based on structure
            if isinstance(data, dict):
                # Stream data contains 'e' for event type
                if 'e' in data:
                    event_type = data['e']
                    await self._process_event(event_type, data)
                # Subscription responses have 'result' or 'id'
                elif 'result' in data or 'id' in data:
                    logger.debug(f"Received subscription response: {data}")
                    
            # Call custom callback if provided
            if self.callback and event_type:
                self.callback(event_type, data)
                
        except json.JSONDecodeError:
            logger.warning(f"Received non-JSON message: {message[:100]}...")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def _process_event(self, event_type: str, data: Dict[str, Any]):
        """Process different event types from the WebSocket"""
        try:
            if event_type == "bookTicker":
                # Process order book ticker update
                symbol = data['s']
                self.prices[symbol] = PriceData(
                    bid=float(data['b']),
                    ask=float(data['a'])
                )
                logger.debug(f"Updated price for {symbol}: bid=${data['b']}, ask=${data['a']}")
                
            elif event_type == "kline":
                # Process kline/candlestick update
                symbol = data['s']
                k = data['k']
                candle = Candle(
                    timestamp=k['t'],
                    open_price=float(k['o']),
                    high_price=float(k['h']),
                    low_price=float(k['l']),
                    close_price=float(k['c']),
                    volume=float(k['v']),
                    quote_volume=float(k['q'])
                )
                
                # Store the candle
                interval = k['i']
                if symbol not in self.candles:
                    self.candles[symbol] = {}
                if interval not in self.candles[symbol]:
                    self.candles[symbol][interval] = []
                
                # Add candle if it's a new one or update the last one if it's still the same interval
                if (not self.candles[symbol][interval] or 
                    candle.timestamp != self.candles[symbol][interval][-1].timestamp):
                    self.candles[symbol][interval].append(candle)
                    # Keep only the last 1000 candles per interval
                    if len(self.candles[symbol][interval]) > 1000:
                        self.candles[symbol][interval].pop(0)
                else:
                    self.candles[symbol][interval][-1] = candle
                
        except Exception as e:
            logger.error(f"Error processing event '{event_type}': {e}")
    
    async def _subscribe(self, symbol: str, streams: List[str]):
        """Subscribe to WebSocket channels for a symbol"""
        if not self.ws_connected or not self.ws:
            logger.warning("Cannot subscribe: WebSocket not connected")
            return
        
        # Format streams properly (handle kline streams)
        formatted_streams = []
        for stream in streams:
            if stream.startswith("kline_"):
                interval = stream.split("_")[1]
                formatted_streams.append(f"{symbol.lower()}@kline_{interval}")
            else:
                formatted_streams.append(f"{symbol.lower()}@{stream}")
        
        subscription_data = {
            "method": "SUBSCRIBE",
            "params": formatted_streams,
            "id": self.id
        }
        
        try:
            await self.ws.send(json.dumps(subscription_data))
            self.id += 1
            
            # Add to subscription tracking for reconnection
            self.subscriptions.add(symbol)
            self.subscription_params[symbol] = streams
            
            logger.info(f"Subscribed to {symbol} channels: {streams}")
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
    
    def subscribe(self, symbol: str, streams: Optional[List[str]] = None):
        """
        Subscribe to a symbol's WebSocket streams.
        
        Args:
            symbol: The symbol to subscribe to (e.g., "BTCUSDT")
            streams: List of stream types. Default is ["bookTicker"].
                     Options include:
                     - "bookTicker" - Best bid/ask updates
                     - "kline_1m", "kline_5m", etc. - Candlestick updates
                     - "trade" - Real-time trade data
                     - "aggTrade" - Aggregate trade data
        """
        if streams is None:
            streams = ["bookTicker"]
            
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self._subscribe(symbol, streams), 
                self.ws_loop
            )
        else:
            logger.warning(f"Cannot subscribe to {symbol}: WebSocket not ready")
            # Store subscription request for when connection is established
            self.subscriptions.add(symbol)
            self.subscription_params[symbol] = streams
    
    async def _unsubscribe(self, symbol: str, streams: List[str]):
        """Unsubscribe from WebSocket channels"""
        if not self.ws_connected or not self.ws:
            logger.warning("Cannot unsubscribe: WebSocket not connected")
            return
        
        # Format streams properly
        formatted_streams = []
        for stream in streams:
            if stream.startswith("kline_"):
                interval = stream.split("_")[1]
                formatted_streams.append(f"{symbol.lower()}@kline_{interval}")
            else:
                formatted_streams.append(f"{symbol.lower()}@{stream}")
        
        unsubscribe_data = {
            "method": "UNSUBSCRIBE",
            "params": formatted_streams,
            "id": self.id
        }
        
        try:
            await self.ws.send(json.dumps(unsubscribe_data))
            self.id += 1
            
            # Remove from subscription tracking
            if symbol in self.subscriptions:
                self.subscriptions.remove(symbol)
            if symbol in self.subscription_params:
                del self.subscription_params[symbol]
                
            logger.info(f"Unsubscribed from {symbol} channels: {streams}")
        except Exception as e:
            logger.error(f"Error unsubscribing from channel: {e}")
    
    def unsubscribe(self, symbol: str, streams: Optional[List[str]] = None):
        """
        Unsubscribe from a symbol's WebSocket streams.
        
        Args:
            symbol: The symbol to unsubscribe from (e.g., "BTCUSDT")
            streams: List of stream types to unsubscribe from.
                     If None, unsubscribes from all streams for this symbol.
        """
        if streams is None and symbol in self.subscription_params:
            streams = self.subscription_params[symbol]
        elif streams is None:
            streams = ["bookTicker"]
            
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self._unsubscribe(symbol, streams), 
                self.ws_loop
            )
        else:
            # Still remove from tracking even if WS not connected
            if symbol in self.subscriptions:
                self.subscriptions.remove(symbol)
            if symbol in self.subscription_params:
                del self.subscription_params[symbol]
    
    def get_price(self, symbol: str) -> Optional[PriceData]:
        """Get the latest price for a symbol"""
        return self.prices.get(symbol)
    
    def get_candles(self, symbol: str, interval: str) -> List[Candle]:
        """Get cached candles for a symbol and interval"""
        if symbol in self.candles and interval in self.candles[symbol]:
            return self.candles[symbol][interval]
        return []
    
    async def _close(self):
        """Close the WebSocket connection"""
        if self.ws and self.ws_connected:
            await self.ws.close()
            self.ws_connected = False
            self.ws = None
    
    def close(self):
        """Gracefully close the WebSocket connection"""
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self._close(), 
                self.ws_loop
            )
            
        # Wait for thread to finish if it's running
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=1.0)
    
    def __del__(self):
        """Cleanup resources when instance is being destroyed"""
        self.close()