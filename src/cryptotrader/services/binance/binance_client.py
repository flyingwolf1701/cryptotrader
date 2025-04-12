import httpx
import time
import hmac
import hashlib
import json
import asyncio
import threading
import logging
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Union, Tuple
import websockets
from datetime import datetime, timedelta

from cryptotrader.services.binance.binance_models import (
    PriceData, BinanceEndpoints, OrderRequest, Candle,
    AccountAsset, AccountBalance, OrderStatusResponse, SymbolInfo,
    RateLimit, RateLimitType, RateLimitInterval, OrderType, 
    TimeInForce, OrderSide, KlineInterval
)

from cryptotrader.config import get_logger
logger = get_logger(__name__)

class RateLimiter:
    """Rate limiter for Binance API"""
    
    def __init__(self):
        self.rate_limits: List[RateLimit] = []
        self.request_counts: Dict[Tuple[RateLimitType, RateLimitInterval, int], List[float]] = {}
        
    def update_rate_limits(self, rate_limits: List[Dict[str, Any]]):
        """Update rate limits from exchange info"""
        self.rate_limits = []
        for limit in rate_limits:
            self.rate_limits.append(RateLimit(
                rate_limit_type=RateLimitType(limit['rateLimitType']),
                interval=RateLimitInterval(limit['interval']),
                interval_num=limit['intervalNum'],
                limit=limit['limit']
            ))
        logger.debug(f"Updated rate limits: {self.rate_limits}")
    
    def check_rate_limit(self, limit_type: RateLimitType, weight: int = 1) -> bool:
        """Check if request can be executed without hitting rate limit"""
        current_time = time.time()
        
        for rate_limit in self.rate_limits:
            if rate_limit.rate_limit_type != limit_type:
                continue
                
            # Get time window for this rate limit
            if rate_limit.interval == RateLimitInterval.SECOND:
                window_seconds = rate_limit.interval_num
            elif rate_limit.interval == RateLimitInterval.MINUTE:
                window_seconds = rate_limit.interval_num * 60
            elif rate_limit.interval == RateLimitInterval.DAY:
                window_seconds = rate_limit.interval_num * 86400
            else:
                continue
                
            # Create key for this rate limit
            key = (rate_limit.rate_limit_type, rate_limit.interval, rate_limit.interval_num)
            
            # Initialize request counts if not exists
            if key not in self.request_counts:
                self.request_counts[key] = []
                
            # Remove timestamps outside window
            self.request_counts[key] = [ts for ts in self.request_counts[key] 
                                     if current_time - ts < window_seconds]
                
            # Check if adding this request would exceed limit
            if len(self.request_counts[key]) + weight > rate_limit.limit:
                logger.warning(
                    f"Rate limit would be exceeded: {rate_limit.rate_limit_type} "
                    f"limit of {rate_limit.limit} per {rate_limit.interval_num} "
                    f"{rate_limit.interval}(s)"
                )
                return False
        
        return True
    
    def record_request(self, limit_type: RateLimitType, weight: int = 1):
        """Record a request for rate limiting purposes"""
        current_time = time.time()
        
        for rate_limit in self.rate_limits:
            if rate_limit.rate_limit_type != limit_type:
                continue
                
            # Create key for this rate limit
            key = (rate_limit.rate_limit_type, rate_limit.interval, rate_limit.interval_num)
            
            # Initialize request counts if not exists
            if key not in self.request_counts:
                self.request_counts[key] = []
                
            # Add timestamps for this request
            for _ in range(weight):
                self.request_counts[key].append(current_time)


class BinanceAPIRequest:
    """Handles API request preparation and execution"""
    
    def __init__(self, client, method, endpoint, limit_type=RateLimitType.REQUEST_WEIGHT, weight=1):
        self.client = client
        self.method = method
        self.endpoint = endpoint
        self.query_params = {}
        self.body_params = {}
        self.limit_type = limit_type
        self.weight = weight
        
    def with_query_params(self, **params):
        """Add query parameters"""
        self.query_params.update(params)
        return self
        
    def with_body_params(self, **params):
        """Add body parameters"""
        self.body_params.update(params)
        return self
    
    def with_timestamp(self):
        """Add timestamp to request"""
        timestamp = int(time.time() * 1000)
        
        # Add timestamp to appropriate location based on request type
        if self.method == "GET" or self.method == "DELETE" or not self.body_params:
            self.query_params['timestamp'] = timestamp
        else:
            self.body_params['timestamp'] = timestamp
            
        return self
    
    def sign(self):
        """Add signature to request"""
        # Combine all parameters for signing
        all_params = {**self.query_params, **self.body_params}
        
        # Generate signature
        signature = self.client.generate_signature(all_params)
        
        # Add signature to query parameters
        self.query_params['signature'] = signature
        
        return self
    
    def execute(self):
        """Execute the request and return the response"""
        url = f"{self.client.base_url}{self.endpoint}"
        
        # Check rate limit
        if not self.client.rate_limiter.check_rate_limit(self.limit_type, self.weight):
            logger.warning(f"Request would exceed rate limit for {self.limit_type}. Waiting...")
            time.sleep(1)  # Simple backoff strategy
            
            # Check again after waiting
            if not self.client.rate_limiter.check_rate_limit(self.limit_type, self.weight):
                logger.error(f"Still exceeding rate limit after waiting. Request aborted.")
                return None
        
        try:
            if self.method == "GET":
                response = self.client.http.get(url, params=self.query_params, headers=self.client.headers)
            elif self.method == "POST":
                if not self.body_params:
                    response = self.client.http.post(url, params=self.query_params, headers=self.client.headers)
                else:
                    response = self.client.http.post(
                        url, 
                        params=self.query_params, 
                        data=self.body_params, 
                        headers=self.client.headers
                    )
            elif self.method == "DELETE":
                response = self.client.http.delete(url, params=self.query_params, headers=self.client.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")
                
            response.raise_for_status()
            
            # Record the request for rate limiting
            self.client.rate_limiter.record_request(self.limit_type, self.weight)
            
            # Update API limits if present in headers
            if 'X-MBX-USED-WEIGHT-1M' in response.headers:
                logger.debug(f"Used weight: {response.headers['X-MBX-USED-WEIGHT-1M']}")
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # Handle specific error codes
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded!")
                # Extract retry-after if available
                retry_after = int(e.response.headers.get('Retry-After', 30))
                logger.info(f"Retry after {retry_after} seconds")
                return {"error": "Rate limit exceeded", "retry_after": retry_after}
            elif e.response.status_code == 418:
                logger.error("IP has been auto-banned for repeated violations!")
                return {"error": "IP banned"}
            
            logger.error(
                "Error while making %s request to %s: %s (error code %s)", 
                self.method, self.endpoint, e.response.text, e.response.status_code
            )
            return None
        except httpx.RequestError as e:
            logger.error(
                "Request error while making %s request to %s: %s", 
                self.method, self.endpoint, str(e)
            )
            return None


class WebSocketManager:
    """Manages WebSocket connections and subscriptions"""
    
    def __init__(self, client):
        self.client = client
        self.ws = None
        self.ws_connected = False
        self.ws_loop = None
        self.ws_thread = None
        self.id = 1
        self.subscriptions = set()
        self.last_ping = 0
        
    def start(self):
        """Start the WebSocket connection in a background thread"""
        self.ws_thread = threading.Thread(target=self._start_ws_thread, daemon=True)
        self.ws_thread.start()
        
    def _start_ws_thread(self):
        """Thread function that runs the WebSocket event loop"""
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        self.ws_loop.run_until_complete(self._ws_handler())
        
    async def _ws_handler(self):
        """Main WebSocket connection handler"""
        while True:
            try:
                logger.info("Connecting to Binance WebSocket...")
                async with websockets.connect(self.client.wss_url) as websocket:
                    self.ws = websocket
                    self.ws_connected = True
                    logger.info("Binance WebSocket Connection Opened")
                    
                    # Resubscribe to existing channels
                    for symbol in self.subscriptions:
                        await self.subscribe(symbol)
                    
                    # Keep track of last ping time for connection health
                    self.last_ping = time.time()
                    
                    # Setup ping task
                    ping_task = asyncio.create_task(self._ping_websocket())
                    
                    # Listen for messages
                    try:
                        while True:
                            message = await websocket.recv()
                            await self._on_message(message)
                    finally:
                        ping_task.cancel()
                        
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"Binance WebSocket connection closed: {e}")
                self.ws_connected = False
                self.ws = None
            except Exception as e:
                logger.error(f"Binance WebSocket error: {e}")
                self.ws_connected = False
                self.ws = None
            
            # Wait before reconnecting
            await asyncio.sleep(5)
    
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
    
    async def _on_message(self, message):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            logger.debug(f"Received WS: {message[:100]}...")
            
            # Handle different message types
            if isinstance(data, dict) and 'e' in data:
                event_type = data['e']
                
                if event_type == "bookTicker":
                    symbol = data['s']
                    self.client.prices[symbol] = PriceData(
                        bid=float(data['b']),
                        ask=float(data['a'])
                    )
                    logger.debug(f"Updated price for {symbol}: bid=${data['b']}, ask=${data['a']}")
                elif event_type == "kline":
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
                    if symbol not in self.client.candles:
                        self.client.candles[symbol] = {}
                    if interval not in self.client.candles[symbol]:
                        self.client.candles[symbol][interval] = []
                    
                    # Add candle if it's a new one or update the last one if it's still the same interval
                    if (not self.client.candles[symbol][interval] or 
                        candle.timestamp != self.client.candles[symbol][interval][-1].timestamp):
                        self.client.candles[symbol][interval].append(candle)
                    else:
                        self.client.candles[symbol][interval][-1] = candle
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def subscribe(self, symbol, streams=None):
        """Subscribe to WebSocket channels for a symbol"""
        if not self.ws_connected or not self.ws:
            logger.warning("Cannot subscribe: WebSocket not connected")
            return
        
        if streams is None:
            # Default to book ticker stream
            streams = ["bookTicker"]
        
        params = [f"{symbol.lower()}@{stream}" for stream in streams]
        
        data = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": self.id
        }
        
        try:
            await self.ws.send(json.dumps(data))
            self.id += 1
            
            # Add to subscription list for reconnection
            self.subscriptions.add(symbol)
            
            logger.info(f"Subscribed to {symbol} channels: {streams}")
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
    
    def subscribe_sync(self, symbol, streams=None):
        """Synchronous wrapper for subscribe"""
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self.subscribe(symbol, streams), 
                self.ws_loop
            )
        else:
            logger.warning(f"Cannot subscribe to {symbol}: WebSocket not ready")
            
    async def cleanup(self):
        """Cleanup WebSocket resources"""
        if self.ws and self.ws_connected:
            await self.ws.close()
            self.ws_connected = False
            self.ws = None


class Client:
    """Binance API client with improved OOP structure"""
    
    def __init__(self, public_key: str, secret_key: str):
        # Initialize endpoints
        endpoints = BinanceEndpoints()
        self.base_url = endpoints.base_url
        self.wss_url = endpoints.wss_url
        
        # API credentials
        self.public_key = public_key
        self.secret_key = secret_key
        self.headers = {'X-MBX-APIKEY': public_key}
        
        # State
        self.prices: Dict[str, PriceData] = {}
        self.candles: Dict[str, Dict[str, List[Candle]]] = {}
        self.exchange_info = None
        
        # Rate limiter
        self.rate_limiter = RateLimiter()
        
        # HTTP client
        self.http = httpx.Client(timeout=30.0)
        
        # Initialize rate limits - fetch exchange info
        self._init_exchange_info()
        
        # WebSocket manager
        self.ws_manager = WebSocketManager(self)
        self.ws_manager.start()
        
        logger.info("Binance Client successfully initialized")
    
    def _init_exchange_info(self):
        """Initialize exchange info and rate limits"""
        try:
            response = self.request("GET", "/api/v3/exchangeInfo").execute()
            if response:
                self.exchange_info = response
                if 'rateLimits' in response:
                    self.rate_limiter.update_rate_limits(response['rateLimits'])
                    logger.info("Rate limits initialized")
        except Exception as e:
            logger.warning(f"Error initializing exchange info: {e}")
    
    def generate_signature(self, data):
        """Generate HMAC-SHA256 signature for API authentication"""
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha256
        ).hexdigest()
    
    def request(self, method, endpoint, limit_type=RateLimitType.REQUEST_WEIGHT, weight=1):
        """Create a new API request builder"""
        return BinanceAPIRequest(self, method, endpoint, limit_type, weight)
    
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        """Get current bid/ask prices for a symbol"""
        response = self.request("GET", "/api/v3/ticker/bookTicker") \
            .with_query_params(symbol=symbol) \
            .execute()
            
        if response is not None:
            price_data = PriceData(
                bid=float(response['bidPrice']),
                ask=float(response['askPrice'])
            )
            self.prices[symbol] = price_data
            return price_data
        
        return self.prices.get(symbol)
    
    def get_balance(self) -> AccountBalance:
        """Get account balance information"""
        response = self.request("GET", "/api/v3/account", weight=10) \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response is not None:
            return AccountBalance.from_api_response(response)
        
        return AccountBalance(assets={})
    
    def place_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> Optional[OrderStatusResponse]:
        """Place a new order"""
        # Determine weight based on order type
        weight = 1
        
        # Create a request builder
        request = self.request("POST", "/api/v3/order", RateLimitType.ORDERS, weight)
        
        # Process OrderRequest object
        if isinstance(order_request, OrderRequest):
            # Convert enums to strings for API
            side = order_request.side.value if isinstance(order_request.side, OrderSide) else order_request.side
            order_type = order_request.order_type.value if isinstance(order_request.order_type, OrderType) else order_request.order_type
            
            # Add query parameters
            params = {
                "symbol": order_request.symbol,
                "side": side,
                "type": order_type,
                "quantity": order_request.quantity
            }
            
            # Add conditional parameters
            if order_request.price is not None:
                params["price"] = order_request.price
                
            if order_request.time_in_force is not None:
                time_in_force = order_request.time_in_force.value if isinstance(order_request.time_in_force, TimeInForce) else order_request.time_in_force
                params["timeInForce"] = time_in_force
                
            if order_request.stop_price is not None:
                params["stopPrice"] = order_request.stop_price
                
            if order_request.iceberg_qty is not None:
                params["icebergQty"] = order_request.iceberg_qty
                
            if order_request.new_client_order_id is not None:
                params["newClientOrderId"] = order_request.new_client_order_id
                
            request.with_query_params(**params)
        else:
            # Handle dictionary input
            request.with_query_params(**order_request)
        
        # Add timestamp and signature, then execute
        response = request.with_timestamp().sign().execute()
        
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, 
                   client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """Cancel an existing order"""
        request = self.request("DELETE", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 1) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
            
        response = request.with_timestamp().sign().execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def get_order_status(self, symbol: str, order_id: Optional[int] = None, 
                       client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """Get status of an existing order"""
        request = self.request("GET", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 2) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
            
        response = request.with_timestamp().sign().execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def get_historical_candles(self, symbol: str, interval: str, 
                              limit: int = 500, 
                              start_time: Optional[int] = None,
                              end_time: Optional[int] = None) -> List[Candle]:
        """
        Get historical candlestick data
        
        Args:
            symbol: Symbol to get candles for (e.g. "BTCUSDT")
            interval: Candle interval (e.g. "1m", "1h", "1d")
            limit: Number of candles to return (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of Candle objects
        """
        # Validate interval
        valid_intervals = [interval.value for interval in KlineInterval]
        if interval not in valid_intervals:
            logger.warning(f"Invalid interval: {interval}. Using 1h instead.")
            interval = "1h"
            
        # Adjust request weight based on limit
        weight = 1
        if limit > 100:
            weight = 2
        if limit > 500:
            weight = 5
            
        # Build request
        request = self.request("GET", "/api/v3/klines", RateLimitType.REQUEST_WEIGHT, weight) \
            .with_query_params(
                symbol=symbol,
                interval=interval,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        # Add optional parameters
        if start_time:
            request.with_query_params(startTime=start_time)
        if end_time:
            request.with_query_params(endTime=end_time)
            
        response = request.execute()
        candles = []
        
        if response is not None:
            for c in response:
                candle = Candle(
                    timestamp=int(c[0]),
                    open_price=float(c[1]),
                    high_price=float(c[2]),
                    low_price=float(c[3]),
                    close_price=float(c[4]),
                    volume=float(c[5]),
                    quote_volume=float(c[7])
                )
                candles.append(candle)
                
            # Cache the candles
            if symbol not in self.candles:
                self.candles[symbol] = {}
            self.candles[symbol][interval] = candles
        
        return candles
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information"""
        if self.exchange_info is None:
            response = self.request("GET", "/api/v3/exchangeInfo", weight=10).execute()
            if response:
                self.exchange_info = response
        
        return self.exchange_info or {}
    
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """Get information for a specific symbol"""
        exchange_info = self.get_exchange_info()
        
        if 'symbols' in exchange_info:
            for symbol_data in exchange_info['symbols']:
                if symbol_data['symbol'] == symbol:
                    return SymbolInfo.from_api_response(symbol_data)
        
        return None
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """Get available trading symbols"""
        try:
            with httpx.Client() as client:
                response = client.get("https://api.binance.us/api/v3/exchangeInfo")
                response.raise_for_status()
                
                symbols = []
                for symbol_data in response.json()['symbols']:
                    # Only include TRADING symbols
                    if symbol_data['status'] == 'TRADING':
                        symbols.append(symbol_data['symbol'])
                return symbols
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Error fetching Binance symbols: {e}")
            return []
    
    def subscribe_channel(self, symbol: str, streams: Optional[List[str]] = None):
        """
        Subscribe to WebSocket channels for a symbol
        
        Args:
            symbol: Symbol to subscribe to (e.g. "BTCUSDT")
            streams: List of stream types to subscribe to. Default is ["bookTicker"]
                     Options include: "bookTicker", "kline_1m", "kline_5m", etc.
        """
        self.ws_manager.subscribe_sync(symbol, streams)
    
    def get_server_time(self) -> int:
        """Get current server time"""
        response = self.request("GET", "/api/v3/time").execute()
        if response and 'serverTime' in response:
            return int(response['serverTime'])
        return int(time.time() * 1000)
    
    def check_server_time(self) -> int:
        """Check time difference between local and server time"""
        local_time = int(time.time() * 1000)
        server_time = self.get_server_time()
        diff = abs(local_time - server_time)
        
        if diff > 1000:  # More than 1 second difference
            logger.warning(f"Time drift detected: {diff}ms difference between local and server time")
        
        return diff
    
    def __del__(self):
        """Cleanup resources when instance is being destroyed"""
        if hasattr(self, 'http') and self.http:
            self.http.close()
        
        # Close the WebSocket connection
        if hasattr(self, 'ws_manager') and self.ws_manager.ws_loop and self.ws_manager.ws_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.ws_manager.cleanup(), 
                self.ws_manager.ws_loop
            )