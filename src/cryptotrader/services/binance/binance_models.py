"""
Binance API Data Models

This module defines the data structures and enumerations used by the Binance API client.
It provides strongly-typed models for requests and responses to improve type safety
and code readability.

Key components:
- Enumerations for API constants (OrderType, OrderSide, etc.)
- Data classes for request and response objects
- Type conversion and validation logic for API responses
- Convenience properties and utility methods

These models are used by both the REST and WebSocket clients to ensure
consistent handling of Binance API data across the application.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Any


class OrderType(str, Enum):
    """Order types supported by Binance API"""
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    LIMIT_MAKER = "LIMIT_MAKER"


class OrderSide(str, Enum):
    """Order sides supported by Binance API"""
    BUY = "BUY"
    SELL = "SELL"


class TimeInForce(str, Enum):
    """Time in force options supported by Binance API"""
    GTC = "GTC"  # Good Till Canceled
    IOC = "IOC"  # Immediate or Cancel
    FOK = "FOK"  # Fill or Kill


class KlineInterval(str, Enum):
    """Kline/Candlestick intervals supported by Binance API"""
    MINUTE_1 = "1m"
    MINUTE_3 = "3m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_6 = "6h"
    HOUR_8 = "8h"
    HOUR_12 = "12h"
    DAY_1 = "1d"
    DAY_3 = "3d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


class OrderStatus(str, Enum):
    """Order statuses returned by Binance API"""
    NEW = "NEW"  # The order has been accepted by the engine
    PARTIALLY_FILLED = "PARTIALLY_FILLED"  # Part of the order has been filled
    FILLED = "FILLED"  # The order has been completed
    CANCELED = "CANCELED"  # The order has been canceled by the user
    PENDING_CANCEL = "PENDING_CANCEL"  # Currently unused
    REJECTED = "REJECTED"  # The order was not accepted by the engine and not processed
    EXPIRED = "EXPIRED"  # Canceled according to order type's rules or by the exchange
    EXPIRED_IN_MATCH = "EXPIRED_IN_MATCH"  # Canceled by the exchange due to STP


class SelfTradePreventionMode(str, Enum):
    """Self-trade prevention modes supported by Binance API"""
    EXPIRE_MAKER = "EXPIRE_MAKER"  # Expire the maker order
    EXPIRE_TAKER = "EXPIRE_TAKER"  # Expire the taker order
    EXPIRE_BOTH = "EXPIRE_BOTH"  # Expire both orders


class SymbolStatus(str, Enum):
    """Symbol statuses returned by Binance API"""
    PRE_TRADING = "PRE_TRADING"
    TRADING = "TRADING"
    POST_TRADING = "POST_TRADING"
    END_OF_DAY = "END_OF_DAY"
    HALT = "HALT"
    AUCTION_MATCH = "AUCTION_MATCH"
    BREAK = "BREAK"


class RateLimitType(str, Enum):
    """Rate limit types used by Binance API"""
    REQUEST_WEIGHT = "REQUEST_WEIGHT"
    ORDERS = "ORDERS"
    RAW_REQUESTS = "RAW_REQUESTS"


class RateLimitInterval(str, Enum):
    """Rate limit intervals used by Binance API"""
    SECOND = "SECOND"  # Corresponds to 'S' in headers
    MINUTE = "MINUTE"  # Corresponds to 'M' in headers
    HOUR = "HOUR"      # Corresponds to 'H' in headers
    DAY = "DAY"        # Corresponds to 'D' in headers


@dataclass
class RateLimit:
    """Data structure for rate limit info"""
    rate_limit_type: RateLimitType
    interval: RateLimitInterval
    interval_num: int
    limit: int


@dataclass
class SystemStatus:
    """System status information"""
    status_code: int  # 0: normal, 1: system maintenance, -1: unknown
    
    @property
    def is_normal(self) -> bool:
        """Check if system status is normal"""
        return self.status_code == 0
    
    @property
    def is_maintenance(self) -> bool:
        """Check if system is under maintenance"""
        return self.status_code == 1
    
    @property
    def status_description(self) -> str:
        """Get human-readable status description"""
        if self.status_code == 0:
            return "Normal"
        elif self.status_code == 1:
            return "System Maintenance"
        else:
            return "Unknown"


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
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    time_in_force: Optional[TimeInForce] = None
    stop_price: Optional[float] = None
    iceberg_qty: Optional[float] = None
    new_client_order_id: Optional[str] = None
    self_trade_prevention_mode: Optional[str] = None


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
class OrderStatusResponse:
    """Data structure for order status"""
    symbol: str
    orderId: int
    orderListId: int
    clientOrderId: str
    price: float
    origQty: float
    executedQty: float
    cummulativeQuoteQty: float
    status: OrderStatus
    timeInForce: TimeInForce
    type: OrderType
    side: OrderSide
    stopPrice: float
    time: int
    updateTime: int
    isWorking: bool
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderStatusResponse':
        return cls(
            symbol=response.get('symbol', ''),
            orderId=int(response.get('orderId', 0)),
            orderListId=int(response.get('orderListId', -1)),
            clientOrderId=response.get('clientOrderId', ''),
            price=float(response.get('price', 0)),
            origQty=float(response.get('origQty', 0)),
            executedQty=float(response.get('executedQty', 0)),
            cummulativeQuoteQty=float(response.get('cummulativeQuoteQty', 0)),
            status=OrderStatus(response.get('status', 'NEW')),
            timeInForce=TimeInForce(response.get('timeInForce', 'GTC')),
            type=OrderType(response.get('type', 'LIMIT')),
            side=OrderSide(response.get('side', 'BUY')),
            stopPrice=float(response.get('stopPrice', 0)),
            time=int(response.get('time', 0)),
            updateTime=int(response.get('updateTime', 0)),
            isWorking=bool(response.get('isWorking', False))
        )


@dataclass
class SymbolInfo:
    """Data structure for symbol information"""
    symbol: str
    status: SymbolStatus
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    orderTypes: List[OrderType]
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'SymbolInfo':
        return cls(
            symbol=response.get('symbol', ''),
            status=SymbolStatus(response.get('status', 'TRADING')),
            baseAsset=response.get('baseAsset', ''),
            baseAssetPrecision=int(response.get('baseAssetPrecision', 0)),
            quoteAsset=response.get('quoteAsset', ''),
            quotePrecision=int(response.get('quotePrecision', 0)),
            quoteAssetPrecision=int(response.get('quoteAssetPrecision', 0)),
            orderTypes=[OrderType(order_type) for order_type in response.get('orderTypes', [])]
        )