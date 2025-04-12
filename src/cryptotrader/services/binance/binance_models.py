from dataclasses import dataclass
from typing import Dict, List, Optional, Any

@dataclass
class BinanceEndpoints:
    """Endpoints for Binance API"""
    # Binance US endpoints
    base_url: str = "https://api.binance.us"
    wss_url: str = "wss://stream.binance.us:9443/ws"

@dataclass
class PriceData:
    """Data structure for bid/ask prices"""
    bid: float
    ask: float

@dataclass
class OrderRequest:
    """Data structure for order requests"""
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    order_type: str  # "LIMIT", "MARKET", etc.
    price: Optional[float] = None
    time_in_force: Optional[str] = None  # "GTC", "IOC", "FOK"

@dataclass
class Candle:
    """Data structure for candlestick data"""
    timestamp: int
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float

@dataclass
class AccountAsset:
    """Data structure for account asset"""
    asset: str
    free: float
    locked: float

    @classmethod
    def from_api_response(cls, asset_data: Dict[str, Any]) -> 'AccountAsset':
        return cls(
            asset=asset_data['asset'],
            free=float(asset_data.get('free', 0)),
            locked=float(asset_data.get('locked', 0))
        )

@dataclass
class AccountBalance:
    """Data structure for account balance"""
    assets: Dict[str, AccountAsset]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AccountBalance':
        assets = {}
        for asset_data in response.get('balances', []):
            asset_name = asset_data['asset']
            assets[asset_name] = AccountAsset.from_api_response(asset_data)
        return cls(assets=assets)

@dataclass
class OrderStatus:
    """Data structure for order status"""
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: str
    timeInForce: str
    type: str
    side: str
    stopPrice: float
    time: int
    updateTime: int
    isWorking: bool
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderStatus':
        return cls(
            symbol=response.get('symbol', ''),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            clientOrderId=response.get('clientOrderId', ''),
            price=float(response.get('price', 0)),
            origQty=float(response.get('origQty', 0)),
            executedQty=float(response.get('executedQty', 0)),
            cummulativeQuoteQty=float(response.get('cummulativeQuoteQty', 0)),
            status=response.get('status', ''),
            timeInForce=response.get('timeInForce', ''),
            type=response.get('type', ''),
            side=response.get('side', ''),
            stopPrice=float(response.get('stopPrice', 0)),
            time=int(response.get('time', 0)),
            updateTime=int(response.get('updateTime', 0)),
            isWorking=bool(response.get('isWorking', False))
        )

@dataclass
class SymbolInfo:
    """Data structure for symbol information"""
    symbol: str
    status: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    orderTypes: List[str]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'SymbolInfo':
        return cls(
            symbol=response.get('symbol', ''),
            status=response.get('status', ''),
            baseAsset=response.get('baseAsset', ''),
            baseAssetPrecision=int(response.get('baseAssetPrecision', 0)),
            quoteAsset=response.get('quoteAsset', ''),
            quotePrecision=int(response.get('quotePrecision', 0)),
            quoteAssetPrecision=int(response.get('quoteAssetPrecision', 0)),
            orderTypes=response.get('orderTypes', [])
        )