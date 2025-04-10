
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

from models.binance_models import PriceData, BinanceEndpoints, OrderRequest, Candle

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, public_key: str, secret_key: str):
        # Use dataclass for endpoints
        endpoints = BinanceEndpoints()
        
        self.base_url = endpoints.base_url
        self.wss_url = endpoints.wss_url
              
        self.id = 1    
        self.public_key = public_key
        self.secret_key = secret_key
        self.headers = {'X-MBX-APIKEY': public_key}
        self.prices: Dict[str, PriceData] = {}
        self.ws = None
        self.ws_connected = False
        self.ws_loop = None
        self.ws_thread = None
        
        # Create httpx client
        self.client = httpx.Client(timeout=30.0)

        # Start WebSocket connection in a separate thread
        self.ws_thread = threading.Thread(target=self.start_ws_thread, daemon=True)
        self.ws_thread.start()
      
        logger.info("Binance Futures Client successfully initialized")
      
    def generate_signature(self, data):
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha256
        ).hexdigest()
        
    def make_request(self, method, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.client.get(url, params=data, headers=self.headers)
            elif method == "POST":
                response = self.client.post(url, params=data, headers=self.headers)
            elif method == "DELETE":
                response = self.client.delete(url, params=data, headers=self.headers)
            else:
                raise ValueError("Invalid request method")
            
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("Error while making %s request to %s: %s (error code %s)", 
                method, endpoint, e.response.text, e.response.status_code)
            return None
        except httpx.RequestError as e:
            logger.error("Request error while making %s request to %s: %s", 
                method, endpoint, str(e))
            return None
      
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        data = {'symbol': symbol}
        ob_data = self.make_request("GET", "/fapi/v1/ticker/bookTicker", data)

        if ob_data is not None:
            # Use PriceData dataclass instead of dict
            price_data = PriceData(
                bid=float(ob_data['bidPrice']),
                ask=float(ob_data['askPrice'])
            )
            self.prices[symbol] = price_data
            return price_data
        
        return self.prices.get(symbol)
    
    def get_balance(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        balance = dict()
        account_data = self.make_request("GET", "/fapi/v1/account", data)
       
        if account_data is not None:
            for a in account_data['assets']:
                balance[a['asset']] = a

        return balance
    
    def place_order(self, 
                order_request: Union[OrderRequest, Dict[str, Any]]
            ) -> Optional[Dict[str, Any]]:
        """
        Place an order using either an OrderRequest object or a dictionary
        """
        # Handle both OrderRequest objects and dictionaries for flexibility
        if isinstance(order_request, OrderRequest):
            data = {
                'symbol': order_request.symbol,
                'side': order_request.side,
                'quantity': order_request.quantity,
                'type': order_request.order_type
            }
            
            if order_request.price is not None:
                data['price'] = order_request.price
                
            if order_request.time_in_force is not None:
                data['timeInForce'] = order_request.time_in_force
        else:
            # Assume it's a dictionary
            data = {
                'symbol': order_request['symbol'],
                'side': order_request['side'],
                'quantity': order_request['quantity'],
                'type': order_request['type']
            }
            
            if 'price' in order_request and order_request['price'] is not None:
                data['price'] = order_request['price']
                
            if 'timeInForce' in order_request and order_request['timeInForce'] is not None:
                data['timeInForce'] = order_request['timeInForce']

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        return self.make_request("POST", "/fapi/v1/order", data)
    
    def cancel_order(self, symbol, order_id):
        data = dict()
        data['symbol'] = symbol
        data['orderId'] = order_id    

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("DELETE", "/fapi/v1/order", data)
        return order_status
    
    def get_order_status(self, symbol, order_id):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("GET", "/fapi/v1/order", data)
        return order_status

    def get_historical_candles(self, symbol: str, interval: str) -> List[Candle]:
        data = {
            'symbol': symbol,
            'interval': interval,
            'limit': 1000
        }

        raw_candles = self.make_request("GET", "/fapi/v1/klines", data)
        candles = []

        if raw_candles is not None:
            for c in raw_candles:
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
    def get_contracts_binance():
        try:
            with httpx.Client() as client:
                response = client.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
                response.raise_for_status()
                contracts = []
                for contract in response.json()['symbols']:
                    contracts.append(contract['pair'])
                return contracts
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Error fetching Binance contracts: {e}")
            return []

    # WebSocket methods using the websockets library
    def start_ws_thread(self):
        """Start the WebSocket connection in a separate thread with its own event loop"""
        # Create a new event loop for the thread
        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        
        # Run the WebSocket connection
        self.ws_loop.run_until_complete(self.ws_handler())
    
    async def ws_handler(self):
        """Main WebSocket connection handler"""
        while True:
            try:
                logger.info("Connecting to Binance WebSocket...")
                async with websockets.connect(self.wss_url) as websocket:
                    self.ws = websocket
                    self.ws_connected = True
                    logger.info("Binance WebSocket Connection Opened")
                    
                    # Subscribe to the default symbol
                    await self.subscribe_channel("BTCUSDT")
                    
                    # Listen for messages
                    while True:
                        message = await websocket.recv()
                        await self.on_message(message)
                        
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
    
    async def on_message(self, message):
        """Process incoming WebSocket messages"""
        try:
            data = json.loads(message)
            logger.info(f"Received: {message[:100]}...")  # Log first 100 chars to avoid massive logs
            
            if 'e' in data:
                if data['e'] == "bookTicker":
                    symbol = data['s']
                    # Use PriceData dataclass
                    self.prices[symbol] = PriceData(
                        bid=float(data['b']),
                        ask=float(data['a'])
                    )
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    async def subscribe_channel(self, symbol):
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
    
    def subscribe_channel(self, symbol):
        """Synchronous wrapper for subscribe_channel to maintain API compatibility"""
        if self.ws_loop and self.ws_connected:
            asyncio.run_coroutine_threadsafe(
                self.subscribe_channel(symbol), 
                self.ws_loop
            )
        else:
            logger.warning(f"Cannot subscribe to {symbol}: WebSocket not ready")
        
    def __del__(self):
        """Cleanup resources when instance is being destroyed"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
        
        # Close the WebSocket connection and event loop
        if self.ws_loop and self.ws_loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self.cleanup_ws(), 
                self.ws_loop
            )
    
    async def cleanup_ws(self):
        """Cleanup WebSocket resources"""
        if self.ws and self.ws_connected:
            await self.ws.close()
            self.ws_connected = False
            self.ws = None