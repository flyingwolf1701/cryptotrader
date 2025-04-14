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


@dataclass
class Trade:
    """Data structure for a single trade"""
    id: int
    price: float
    quantity: float
    quote_quantity: float
    time: int
    is_buyer_maker: bool
    is_best_match: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'Trade':
        return cls(
            id=int(response['id']),
            price=float(response['price']),
            quantity=float(response['qty']),
            quote_quantity=float(response['quoteQty']),
            time=int(response['time']),
            is_buyer_maker=bool(response['isBuyerMaker']),
            is_best_match=bool(response['isBestMatch'])
        )


@dataclass
class AggTrade:
    """Data structure for aggregate trade"""
    aggregate_trade_id: int
    price: float
    quantity: float
    first_trade_id: int
    last_trade_id: int
    timestamp: int
    is_buyer_maker: bool
    is_best_match: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AggTrade':
        return cls(
            aggregate_trade_id=int(response['a']),
            price=float(response['p']),
            quantity=float(response['q']),
            first_trade_id=int(response['f']),
            last_trade_id=int(response['l']),
            timestamp=int(response['T']),
            is_buyer_maker=bool(response['m']),
            is_best_match=bool(response['M'])
        )


@dataclass
class OrderBookEntry:
    """Single order book entry (price and quantity)"""
    price: float
    quantity: float


@dataclass
class OrderBook:
    """Data structure for order book depth"""
    last_update_id: int
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'OrderBook':
        bids = [OrderBookEntry(float(item[0]), float(item[1])) for item in response.get('bids', [])]
        asks = [OrderBookEntry(float(item[0]), float(item[1])) for item in response.get('asks', [])]
        return cls(
            last_update_id=int(response['lastUpdateId']),
            bids=bids,
            asks=asks
        )


@dataclass
class TickerPrice:
    """Data structure for ticker price"""
    symbol: str
    price: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'TickerPrice':
        return cls(
            symbol=response['symbol'],
            price=float(response['price'])
        )


@dataclass
class AvgPrice:
    """Data structure for average price"""
    mins: int
    price: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'AvgPrice':
        return cls(
            mins=int(response['mins']),
            price=float(response['price'])
        )


@dataclass
class PriceStatsMini:
    """
    Data structure for 24hr price change statistics (MINI version)
    
    This contains the reduced fields returned when type=MINI is specified.
    """
    symbol: str
    price_change: float
    last_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: float
    quote_volume: float
    open_time: int
    close_time: int
    first_id: int
    last_id: int
    count: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'PriceStatsMini':
        return cls(
            symbol=response['symbol'],
            price_change=float(response['priceChange']),
            last_price=float(response['lastPrice']),
            open_price=float(response['openPrice']),
            high_price=float(response['highPrice']),
            low_price=float(response['lowPrice']),
            volume=float(response['volume']),
            quote_volume=float(response['quoteVolume']),
            open_time=int(response['openTime']),
            close_time=int(response['closeTime']),
            first_id=int(response['firstId']),
            last_id=int(response['lastId']),
            count=int(response['count'])
        )


@dataclass
class PriceStats(PriceStatsMini):
    """
    Data structure for 24hr price change statistics (FULL version)
    
    This extends PriceStatsMini with additional fields available in the FULL response.
    """
    price_change_percent: float
    weighted_avg_price: float
    prev_close_price: float
    last_qty: float
    bid_price: float
    bid_qty: float
    ask_price: float
    ask_qty: float
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'PriceStats':
        # First create a base object with the mini fields
        mini = PriceStatsMini.from_api_response(response)
        
        # Then extend it with the full fields
        return cls(
            symbol=mini.symbol,
            price_change=mini.price_change,
            last_price=mini.last_price,
            open_price=mini.open_price,
            high_price=mini.high_price,
            low_price=mini.low_price,
            volume=mini.volume,
            quote_volume=mini.quote_volume,
            open_time=mini.open_time,
            close_time=mini.close_time,
            first_id=mini.first_id,
            last_id=mini.last_id,
            count=mini.count,
            # Additional fields for FULL response
            price_change_percent=float(response['priceChangePercent']),
            weighted_avg_price=float(response['weightedAvgPrice']),
            prev_close_price=float(response['prevClosePrice']),
            last_qty=float(response.get('lastQty', 0)),
            bid_price=float(response.get('bidPrice', 0)),
            bid_qty=float(response.get('bidQty', 0)),
            ask_price=float(response.get('askPrice', 0)),
            ask_qty=float(response.get('askQty', 0))
        )


@dataclass
class RollingWindowStatsMini:
    """
    Data structure for rolling window price change statistics (MINI version)
    
    This contains the reduced fields returned when type=MINI is specified.
    """
    symbol: str
    price_change: float
    last_price: float
    open_price: float
    high_price: float
    low_price: float
    volume: float
    quote_volume: float
    open_time: int
    close_time: int
    first_id: int
    last_id: int
    count: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'RollingWindowStatsMini':
        return cls(
            symbol=response['symbol'],
            price_change=float(response['priceChange']),
            last_price=float(response['lastPrice']),
            open_price=float(response['openPrice']),
            high_price=float(response['highPrice']),
            low_price=float(response['lowPrice']),
            volume=float(response['volume']),
            quote_volume=float(response['quoteVolume']),
            open_time=int(response['openTime']),
            close_time=int(response['closeTime']),
            first_id=int(response['firstId']),
            last_id=int(response['lastId']),
            count=int(response['count'])
        )


@dataclass
class RollingWindowStats(RollingWindowStatsMini):
    """
    Data structure for rolling window price change statistics (FULL version)
    
    This extends RollingWindowStatsMini with additional fields available in the FULL response.
    """
    price_change_percent: float
    weighted_avg_price: float
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'RollingWindowStats':
        # First create a base object with the mini fields
        mini = RollingWindowStatsMini.from_api_response(response)
        
        # Then extend it with the full fields
        return cls(
            symbol=mini.symbol,
            price_change=mini.price_change,
            last_price=mini.last_price,
            open_price=mini.open_price,
            high_price=mini.high_price,
            low_price=mini.low_price,
            volume=mini.volume,
            quote_volume=mini.quote_volume,
            open_time=mini.open_time,
            close_time=mini.close_time,
            first_id=mini.first_id,
            last_id=mini.last_id,
            count=mini.count,
            # Additional fields for FULL response
            price_change_percent=float(response['priceChangePercent']),
            weighted_avg_price=float(response['weightedAvgPrice'])
        )