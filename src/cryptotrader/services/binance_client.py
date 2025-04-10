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
from dataclasses import dataclass

from models.binance_models import PriceData, BinanceEndpoints, OrderRequest, Candle

logger = logging.getLogger(__name__)

@dataclass
class AccountAsset:
    asset: str
    walletBalance: float
    unrealizedProfit: float
    marginBalance: float
    maintMargin: float
    initialMargin: float
    positionInitialMargin: float
    openOrderInitialMargin: float
    maxWithdrawAmount: float
    crossWalletBalance: float
    crossUnPnl: float
    availableBalance: float
    marginAvailable: bool
    updateTime: int

    @dataclass
    class PriceData:
        bid: float
        ask: float

    @dataclass
    class OrderRequest:
        symbol: str
        side: str  # "BUY" or "SELL"
        quantity: float
        order_type: str  # "LIMIT", "MARKET", etc.
        price: Optional[float] = None
        time_in_force: Optional[str] = None  # "GTC", "IOC", "FOK"

    @dataclass
    class Candle:
        timestamp: int
        open_price: float
        high_price: float
        low_price: float
        close_price: float
        volume: float
        quote_volume: float

@dataclass
class AccountBalance:
    assets: Dict[str, AccountAsset]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AccountBalance':
        assets = {}
        for asset_data in response.get('assets', []):
            asset_name = asset_data['asset']
            assets[asset_name] = AccountAsset(
                asset=asset_name,
                walletBalance=float(asset_data.get('walletBalance', 0)),
                unrealizedProfit=float(asset_data.get('unrealizedProfit', 0)),
                marginBalance=float(asset_data.get('marginBalance', 0)),
                maintMargin=float(asset_data.get('maintMargin', 0)),
                initialMargin=float(asset_data.get('initialMargin', 0)),
                positionInitialMargin=float(asset_data.get('positionInitialMargin', 0)),
                openOrderInitialMargin=float(asset_data.get('openOrderInitialMargin', 0)),
                maxWithdrawAmount=float(asset_data.get('maxWithdrawAmount', 0)),
                crossWalletBalance=float(asset_data.get('crossWalletBalance', 0)),
                crossUnPnl=float(asset_data.get('crossUnPnl', 0)),
                availableBalance=float(asset_data.get('availableBalance', 0)),
                marginAvailable=bool(asset_data.get('marginAvailable', False)),
                updateTime=int(asset_data.get('updateTime', 0))
            )
        return cls(assets=assets)

@dataclass
class OrderStatus:
    clientOrderId: str
    cumQty: float
    cumQuote: float
    executedQty: float
    orderId: int
    avgPrice: float
    origQty: float
    price: float
    reduceOnly: bool
    side: str
    positionSide: str
    status: str
    stopPrice: float
    closePosition: bool
    symbol: str
    timeInForce: str
    type: str
    origType: str
    updateTime: int
    workingType: str
    priceProtect: bool
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderStatus':
        return cls(
            clientOrderId=response.get('clientOrderId', ''),
            cumQty=float(response.get('cumQty', 0)),
            cumQuote=float(response.get('cumQuote', 0)),
            executedQty=float(response.get('executedQty', 0)),
            orderId=int(response.get('orderId', 0)),
            avgPrice=float(response.get('avgPrice', 0)),
            origQty=float(response.get('origQty', 0)),
            price=float(response.get('price', 0)),
            reduceOnly=bool(response.get('reduceOnly', False)),
            side=response.get('side', ''),
            positionSide=response.get('positionSide', ''),
            status=response.get('status', ''),
            stopPrice=float(response.get('stopPrice', 0)),
            closePosition=bool(response.get('closePosition', False)),
            symbol=response.get('symbol', ''),
            timeInForce=response.get('timeInForce', ''),
            type=response.get('type', ''),
            origType=response.get('origType', ''),
            updateTime=int(response.get('updateTime', 0)),
            workingType=response.get('workingType', ''),
            priceProtect=bool(response.get('priceProtect', False))
        )

@dataclass
class ContractInfo:
    pair: str
    baseAsset: str
    quoteAsset: str
    marginAsset: str
    status: str
    tradingStatus: bool
    pricePrecision: int
    quantityPrecision: int
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'ContractInfo':
        return cls(
            pair=response.get('pair', ''),
            baseAsset=response.get('baseAsset', ''),
            quoteAsset=response.get('quoteAsset', ''),
            marginAsset=response.get('marginAsset', ''),
            status=response.get('status', ''),
            tradingStatus=bool(response.get('onboardDate', 0) > 0),
            pricePrecision=int(response.get('pricePrecision', 0)),
            quantityPrecision=int(response.get('quantityPrecision', 0))
        )

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
        
    def make_request(self, method, endpoint, data, query_params=None, body_params=None):
        """
        Makes a request to the Binance API with proper signature handling.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            data: Parameters for backward compatibility
            query_params: Parameters to be sent in the URL query string
            body_params: Parameters to be sent in the request body
            
        Returns:
            API response as dictionary or None if an error occurs
        """
        url = f"{self.base_url}{endpoint}"
        
        # Handle the case where data is provided (for backward compatibility)
        if query_params is None and body_params is None:
            if method == "GET" or method == "DELETE":
                query_params = data
                body_params = {}
            elif method == "POST":
                # For backward compatibility, we'll put everything in query_params
                # This works for most Binance endpoints
                query_params = data
                body_params = {}
        
        # Ensure params are initialized
        if query_params is None:
            query_params = {}
        if body_params is None:
            body_params = {}
            
        # Combine parameters for signature calculation
        all_params = {**query_params, **body_params}
        
        # Add timestamp if not already present
        if 'timestamp' not in all_params:
            all_params['timestamp'] = int(time.time() * 1000)
            
        # Update the original dictionaries with timestamp
        if method == "GET" or method == "DELETE" or len(body_params) == 0:
            query_params['timestamp'] = all_params['timestamp']
        else:
            # If body_params exist, put timestamp there
            body_params['timestamp'] = all_params['timestamp']
            
        # Generate signature from the combined parameters
        signature = self.generate_signature(all_params)
        
        # Add signature to the appropriate parameter set
        if method == "GET" or method == "DELETE" or len(body_params) == 0:
            query_params['signature'] = signature
        else:
            # If using both query and body params, put signature in query params
            query_params['signature'] = signature
        
        try:
            if method == "GET":
                response = self.client.get(url, params=query_params, headers=self.headers)
            elif method == "POST":
                if len(body_params) == 0:
                    # If no specific body params, use query params as in original implementation
                    response = self.client.post(url, params=query_params, headers=self.headers)
                else:
                    # Handle the case with both query params and body params
                    response = self.client.post(url, params=query_params, data=body_params, headers=self.headers)
            elif method == "DELETE":
                response = self.client.delete(url, params=query_params, headers=self.headers)
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
        query_params = {'symbol': symbol}
        ob_data = self.make_request("GET", "/fapi/v1/ticker/bookTicker", {}, query_params)

        if ob_data is not None:
            # Use PriceData dataclass instead of dict
            price_data = PriceData(
                bid=float(ob_data['bidPrice']),
                ask=float(ob_data['askPrice'])
            )
            self.prices[symbol] = price_data
            return price_data
        
        return self.prices.get(symbol)
    
    def get_balance(self) -> AccountBalance:
        # For GET requests, all parameters should be in the query string
        query_params = {}  # No specific parameters needed for this endpoint
        
        # Timestamp and signature will be added by make_request
        account_data = self.make_request("GET", "/fapi/v1/account", {}, query_params)
        
        if account_data is not None:
            return AccountBalance.from_api_response(account_data)
        
        # Return empty balance if request failed
        return AccountBalance(assets={})
    
    def place_order(self, 
                order_request: Union[OrderRequest, Dict[str, Any]]
            ) -> Optional[OrderStatus]:
        """
        Place an order using either an OrderRequest object or a dictionary
        
        This method demonstrates using both query parameters and body parameters
        for Binance API requests, as per their documentation.
        """
        # Handle both OrderRequest objects and dictionaries for flexibility
        if isinstance(order_request, OrderRequest):
            # For this example, we'll split parameters between query and body
            # Query parameters - typically symbol and basic info
            query_params = {
                'symbol': order_request.symbol,
                'side': order_request.side,
                'type': order_request.order_type,
            }
            
            # Body parameters - typically quantity, price, etc.
            body_params = {
                'quantity': order_request.quantity,
            }
            
            if order_request.price is not None:
                body_params['price'] = order_request.price
                
            if order_request.time_in_force is not None:
                body_params['timeInForce'] = order_request.time_in_force
        else:
            # Assume it's a dictionary
            # For this example, we'll split parameters between query and body
            query_params = {
                'symbol': order_request['symbol'],
                'side': order_request['side'],
                'type': order_request['type'],
            }
            
            body_params = {
                'quantity': order_request['quantity'],
            }
            
            if 'price' in order_request and order_request['price'] is not None:
                body_params['price'] = order_request['price']
                
            if 'timeInForce' in order_request and order_request['timeInForce'] is not None:
                body_params['timeInForce'] = order_request['timeInForce']

        # We don't need to add timestamp or signature here anymore as make_request will handle it
        response = self.make_request("POST", "/fapi/v1/order", {}, query_params, body_params)
        if response:
            return OrderStatus.from_api_response(response)
        return None
    
    def cancel_order(self, symbol, order_id) -> Optional[OrderStatus]:
        query_params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        # Timestamp and signature will be added by make_request
        response = self.make_request("DELETE", "/fapi/v1/order", {}, query_params)
        if response:
            return OrderStatus.from_api_response(response)
        return None
    
    def get_order_status(self, symbol, order_id) -> Optional[OrderStatus]:
        query_params = {
            'symbol': symbol,
            'orderId': order_id
        }
        
        # Timestamp and signature will be added by make_request
        response = self.make_request("GET", "/fapi/v1/order", {}, query_params)
        if response:
            return OrderStatus.from_api_response(response)
        return None

    def get_historical_candles(self, symbol: str, interval: str) -> List[Candle]:
        query_params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 1000
        }

        raw_candles = self.make_request("GET", "/fapi/v1/klines", {}, query_params)
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
    def get_contracts_binance() -> List[str]:
        try:
            with httpx.Client() as client:
                response = client.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
                response.raise_for_status()
                
                contracts = []
                for contract_data in response.json()['symbols']:
                    contracts.append(contract_data['pair'])
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