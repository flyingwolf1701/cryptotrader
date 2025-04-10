import logging
import requests
import time
import hmac
import hashlib
import websocket
import threading
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlencode
from flask import Flask, jsonify, request

logger = logging.getLogger()

# Initialize Flask app
app = Flask(__name__)

@dataclass
class PriceData:
    bid: float
    ask: float

@dataclass
class BinanceEndpoints:
    base_url: str = "https://fapi.binance.com"
    wss_url: str = "wss://fstream.binance.com/ws"

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

        # Start WebSocket connection in a separate thread
        t = threading.Thread(target=self.start_ws, daemon=True)  # Use daemon=True for clean exit
        t.start()
      
        logger.info("Binance Futures Client successfully initialized")
      
    def generate_signature(self, data):
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha256
        ).hexdigest()
        
    def make_request(self, method, endpoint, data):
        if method == "GET":
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == "POST":
            response = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
        elif method == "DELETE":
            response = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)  # Fixed typo (posdeletet -> delete)
        else:
            raise ValueError("Invalid request method")
          
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", 
                method, endpoint, response.json(), response.status_code)
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

        order_status = self.make_request("DELETE", "/fapi/v1/order", data)  # Fixed incomplete endpoint
        return order_status
    
    def get_order_status(self, symbol, order_id):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request("GET", "/fapi/v1/order", data)
        return order_status

    @dataclass
    class Candle:
        timestamp: int
        open_price: float
        high_price: float
        low_price: float
        close_price: float
        volume: float
        quote_volume: float

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
                # Create Candle dataclass instances
                candle = self.Candle(
                    timestamp=int(c[0]),
                    open_price=float(c[1]),
                    high_price=float(c[2]),
                    low_price=float(c[3]),
                    close_price=float(c[4]),
                    volume=float(c[5]),
                    quote_volume=float(c[7])  # Fixed to use the actual quote volume
                )
                candles.append(candle)
        
        return candles

    @staticmethod
    def get_contracts_binance():
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        response_object = requests.get(url)
        contracts = []

        for contract in response_object.json()['symbols']:
            contracts.append(contract['pair'])
        return contracts

    @staticmethod
    def get_contracts_bitmex():
        contracts = []
        url = "https://www.bitmex.com/api/v1/instrament/active"
        response_object = requests.get(url)
        for contract in response_object.json():
            contracts.append(contract['symbol'])
        return contracts

    def on_open(self, ws):
        logger.info("Binance Connection Opened")
        self.subscribe_channel("BTCUSDT")

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning("Binance websocket connection closed")

    def on_error(self, ws, error):
        logger.error(f"Binance connection error {error}")

    def on_message(self, ws, message):
        logger.info(f"Received: {message}")
        data = json.loads(message)

        if 'e' in data:
            if data['e'] == "bookTicker":
                symbol = data['s']
                # Use PriceData dataclass
                self.prices[symbol] = PriceData(
                    bid=float(data['b']),
                    ask=float(data['a'])
                )
            
    def start_ws(self):
        self.ws = websocket.WebSocketApp(
            self.wss_url,
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, msg: self.on_message(ws, msg),
            on_error=lambda ws, err: self.on_error(ws, err),
            on_close=lambda ws, code, msg: self.on_close(ws, code, msg)
        )
        self.ws.run_forever()

    def subscribe_channel(self, symbol):
        data = dict()
        data["method"] = "SUBSCRIBE"
        data["params"] = []
        data["params"].append(symbol.lower() + "@bookTicker")
        data["id"] = self.id

        self.ws.send(json.dumps(data))
        self.id += 1

# Flask routes
@app.route('/api/symbols', methods=['GET'])
def get_symbols():
    try:
        contracts = Client.get_contracts_binance()
        return jsonify({"status": "success", "symbols": contracts})
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/price', methods=['GET'])
def get_price():
    symbol = request.args.get('symbol', 'BTCUSDT')
    try:
        if not hasattr(app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        price_data = app.binance_client.get_bid_ask(symbol)
        if price_data:
            # Convert dataclass to dict for JSON serialization
            data = {
                "bid": price_data.bid,
                "ask": price_data.ask
            }
            return jsonify({"status": "success", "symbol": symbol, "data": data})
        else:
            return jsonify({"status": "error", "message": f"No price data available for {symbol}"}), 404
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/balance', methods=['GET'])
def get_balance():
    try:
        if not hasattr(app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        balance = app.binance_client.get_balance()
        return jsonify({"status": "success", "balance": balance})
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/order', methods=['POST'])
def place_order():
    try:
        if not hasattr(app, 'binance_client'):
            return jsonify({"status": "error", "message": "Binance client not initialized"}), 500
        
        data = request.json
        required_fields = ['symbol', 'side', 'quantity', 'type']
        
        for field in required_fields:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing required field: {field}"}), 400
        
        # Create OrderRequest dataclass instance
        order_request = OrderRequest(
            symbol=data['symbol'],
            side=data['side'],
            quantity=float(data['quantity']),
            order_type=data['type'],
            price=float(data['price']) if 'price' in data and data['price'] is not None else None,
            time_in_force=data.get('timeInForce')
        )
        
        order_status = app.binance_client.place_order(order_request)
        
        if order_status:
            return jsonify({"status": "success", "order": order_status})
        else:
            return jsonify({"status": "error", "message": "Failed to place order"}), 500
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def index():
    return jsonify({"status": "success", "message": "Binance Futures API is running"})

def init_app(public_key, secret_key):
    # Initialize the Binance client and attach it to the app
    app.binance_client = Client(public_key, secret_key)
    return app

if __name__ == "__main__":
    # For testing purposes - in production, use environment variables for keys
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    public_key = os.getenv("BINANCE_API_KEY")
    secret_key = os.getenv("BINANCE_API_SECRET")
    
    if not public_key or not secret_key:
        logger.error("API keys not found in environment variables")
        exit(1)
    
    init_app(public_key, secret_key)
    app.run(debug=True, port=5000)