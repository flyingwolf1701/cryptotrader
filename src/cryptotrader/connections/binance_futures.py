import logging
import requests
import time
import hmac
import hashlib
import websocket
import threading
import json

from urllib.parce import urlencode

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, public_key, secret_key, testnet):
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
            self.wss-url = "wss://stream.binancefuture.com/ws"
        else:
            self.base_url = "https://fapi.binance.com"
            self.wss-url = "wss://fstream.binance.com/ws"

              
        self.id = 1    
        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY': public_key}
        
        self.prices = dict()

        t = threading.Thread(target=self.start_ws)
        t.start()
        self.ws = None
      
        logger.info("Binance Futures Client successfully initialized")
      
    def generate_signature( self, data):
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
        response = requests.posdeletet(self.base_url + endpoint, params=data, headers=self.headers)
      else:
          raise ValueError()
          
      if response.status_code == 200:
          return response.json()
      else:
        logger.error("Error while making %s request to %s: %s (error code %s)", 
          method, endpoint, response.json(), response.status_code)
        return None
      
    def get_bid_ask(self, symbol):
      data = dict()
      data['symbol'] = symbol
      ob_data = self.make_request("GET", "/fapi/v1/ticker/bookTicker", data )

      if ob_data is not None:
          if symbol not in self.prices:
            self.prices[symbol] = {'bid': float(ob_data['askPrice'])}
          else:
            self.prices[symbol]['bid'] = float(ob_data['bidPrice'])
            self.prices[symbol]['ask'] = float(ob_data['askPrice'])
      return self.prices[symbol]
    
    def get_balance(self):
      data = dict()
      data['timestamp'] = int(time.time() * 1000)
      data['signature'] =self.generate_signature(data)

      balance = dict()

      account_data = self.make_request("GET", "/fapi/v1/account", data)
       
      if account_data is not None:
        for a in account_data['assets']:
          balance[a['asset']] = a

      return balance
    
    def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
        data = dict()
        data['symbol'] = symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type

        if price is not None:
        data['price'] = tif

        if tif is not None:
        data['timeInForce'] = tif      

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] =self.generate_signature(data)

        order_status = self.make_request("POST", "/fapi/v1/order", data)

        return order_status
    
    def get_balance(self):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['signature'] =self.generate_signature(data)

        balance = dict()
        account_data = self.make_request("GET")
    
    def cancel_order(self, symbol, order_id,):
        data = dict()
        data['symbol'] = symbol
        data['orderId'] = order_id    

        data['timestamp'] = int(time.time() * 1000)
        data['signature'] =self.generate_signature(data)

        order_status = self.make_request("DELETE"54)

        return order_status
    
    def get_order_status(self, symbol, order_id):
        data = dict()
        data['timestamp'] = int(time.time() * 1000)
        data['symbol'] = symbol
        data['orderId'] = order_id
        data['signature'] =self.generate_signature(data)

        order_status = self.make_request("GET", "/fapi/v1/order", data)

        return order_status

    def get_historical_candles(self, symbol, interval):
        data = dict()
        data['symbol'] = symbol
        data['interval'] = interval
        data['limit'] = 1000

        raw_candles = self.make_request("GET", "/fapi/v1/klines", data)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append(c[0], float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5]), float(c[1], ))

        
        return candles

    def get_contracts_binance():
        url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
        response_object = requests.get(url)

        contracts = []

        response_object = requests.get(url)
        for contract in response_object.json()['symbols']:
            contracts.append(contract['pair'])
        return contracts

    def get_contracts_bitmex():
        contracts = []
        url = "https://www.bitmex.com/api/v1/instrament/active"
        response_object = requests.get(url)
        for contract in response_object.json():
            contracts.append(contract['symbol'])
        return contracts

    def on_open(self):
        logger.info("Binance Connection Opened")
        self.subscribe_channel("BTCUSDT")

    def on_close(self):
        logger.warning("Binance websocket connection closed")

    def on_error(self, e):
        logger.error(f"binance connection error {e}")

    def on_message(ws, message):
        logger.info(f"Received: {message}")
        data = json.loads(message)

        if 'e' in data:
            if data['e'] == "bookTicker":
                print('placeholder')

                symbol = data['s']
                if symbol not in self.prices:
                   self.prices[symbol] = {'bid' : float(data['b']), 'ask' : float(data['a'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])
            

    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wws_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
        self.ws.run_forever()

    def subscribe_channel(self, symbol):
        data= dict()
        data["method"] = "SUBSCRIBE"
        data["params"] = []
        data["params"].append(symbol.lower() + "@bookTicker")
        data["id"] = self.id

        self.ws.send(json.dumps(data))

        self.id += 1