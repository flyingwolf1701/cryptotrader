import logging
import httpx
import time
import hmac
import hashlib
import json
import asyncio
import threading
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Union
import websockets

from models.binance_models import (
    PriceData, BinanceEndpoints, OrderRequest, Candle,
    AccountAsset, AccountBalance, OrderStatus, SymbolInfo
)

logger = logging.getLogger(__name__)

class BinanceAPIRequest:
    """Handles API request preparation and execution"""
    
    def __init__(self, client, method, endpoint):
        self.client = client
        self.method = method
        self.endpoint = endpoint
        self.query_params = {}
        self.body_params = {}
        
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
            return response.json()
            
        except httpx.HTTPStatusError as e:
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
                    
                    # Subscribe to the default symbol
                    await self.subscribe("BTCUSDT")
                    
                    # Listen for messages
                    while True:
                        message = await websocket.recv()
                        await self._on_message(message)
                        
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
    
    async def _on_message(self, message):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            logger.info(f"Received: {message[:100]}...")
            
            if 'e' in data:
                if data['e'] == "bookTicker":
                    symbol = data['s']
                    self.client.prices[symbol] = PriceData(
                        bid=float(data['b']),
                        ask=float(data['a'])
                    )
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def subscribe(self, symbol):
        """Subscribe to a WebSocket channel"""
        if not self.ws_connected or not self.ws:
            logger.warning("Cannot subscribe: WebSocket not connected")
            return
        
        data = {
            "method": "SUBSCRIBE",
            "params": [f"{symbol.lower()}@bookTicker"],
            "id": self.id
        }
        
        try:
            await self.ws.send(json.dumps(data))
            self.id += 1
            logger.info(f"Subscribed to {symbol} channel")
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
    
    def subscribe_sync(self, symbol):
        """Synchronous wrapper for subscribe"""
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self.subscribe(symbol), 
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
        
        # HTTP client
        self.http = httpx.Client(timeout=30.0)
        
        # WebSocket manager
        self.ws_manager = WebSocketManager(self)
        self.ws_manager.start()
        
        logger.info("Binance Client successfully initialized")
    
    def generate_signature(self, data):
        """Generate HMAC-SHA256 signature for API authentication"""
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha256
        ).hexdigest()
    
    def request(self, method, endpoint):
        """Create a new API request builder"""
        return BinanceAPIRequest(self, method, endpoint)
    
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
        response = self.request("GET", "/api/v3/account") \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response is not None:
            return AccountBalance.from_api_response(response)
        
        return AccountBalance(assets={})
    
    def place_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> Optional[OrderStatus]:
        """Place a new order"""
        # Create a request builder
        request = self.request("POST", "/api/v3/order")
        
        # Add parameters based on request type
        if isinstance(order_request, OrderRequest):
            # Add query parameters
            request.with_query_params(
                symbol=order_request.symbol,
                side=order_request.side,
                type=order_request.order_type
            )
            
            # Add body parameters
            body_params = {"quantity": order_request.quantity}
            
            if order_request.price is not None:
                body_params["price"] = order_request.price
                
            if order_request.time_in_force is not None:
                body_params["timeInForce"] = order_request.time_in_force
                
            request.with_body_params(**body_params)
        else:
            # Handle dictionary input
            request.with_query_params(
                symbol=order_request['symbol'],
                side=order_request['side'],
                type=order_request['type']
            )
            
            body_params = {"quantity": order_request['quantity']}
            
            if 'price' in order_request and order_request['price'] is not None:
                body_params["price"] = order_request['price']
                
            if 'timeInForce' in order_request and order_request['timeInForce'] is not None:
                body_params["timeInForce"] = order_request['timeInForce']
                
            request.with_body_params(**body_params)
        
        # Add timestamp and signature, then execute
        response = request.with_timestamp().sign().execute()
        
        if response:
            return OrderStatus.from_api_response(response)
        return None
    
    def cancel_order(self, symbol, order_id) -> Optional[OrderStatus]:
        """Cancel an existing order"""
        response = self.request("DELETE", "/api/v3/order") \
            .with_query_params(symbol=symbol, orderId=order_id) \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response:
            return OrderStatus.from_api_response(response)
        return None
    
    def get_order_status(self, symbol, order_id) -> Optional[OrderStatus]:
        """Get status of an existing order"""
        response = self.request("GET", "/api/v3/order") \
            .with_query_params(symbol=symbol, orderId=order_id) \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response:
            return OrderStatus.from_api_response(response)
        return None
    
    def get_historical_candles(self, symbol: str, interval: str) -> List[Candle]:
        """Get historical candlestick data"""
        response = self.request("GET", "/api/v3/klines") \
            .with_query_params(
                symbol=symbol,
                interval=interval,
                limit=1000
            ) \
            .execute()
            
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
        
        return candles
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """Get available trading symbols"""
        try:
            with httpx.Client() as client:
                response = client.get("https://api.binance.us/api/v3/exchangeInfo")
                response.raise_for_status()
                
                symbols = []
                for symbol_data in response.json()['symbols']:
                    symbols.append(symbol_data['symbol'])
                return symbols
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Error fetching Binance symbols: {e}")
            return []
    
    def subscribe_channel(self, symbol):
        """Subscribe to a WebSocket channel"""
        self.ws_manager.subscribe_sync(symbol)
        
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