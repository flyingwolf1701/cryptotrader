"""
Binance Market API Models

This module defines the data structures used by the Binance Market API client.
It provides strongly-typed models for market data like prices, trades, order books, and statistics.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class PriceData:
    """Data structure for bid/ask prices"""
    bid: float
    ask: float


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