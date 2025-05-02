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
    openPrice: float
    highPrice: float
    lowPrice: float
    closePrice: float
    volume: float
    quoteVolume: float


@dataclass
class Trade:
    """Data structure for a single trade"""

    id: int
    price: float
    quantity: float
    quoteQuantity: float
    time: int
    isBuyerMaker: bool
    isBestMatch: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "Trade":
        return cls(
            id=int(response["id"]),
            price=float(response["price"]),
            quantity=float(response["qty"]),
            quoteQuantity=float(response["quoteQty"]),
            time=int(response["time"]),
            isBuyerMaker=bool(response["isBuyerMaker"]),
            isBestMatch=bool(response["isBestMatch"]),
        )


@dataclass
class AggTrade:
    """Data structure for aggregate trade"""

    aggregateTradeId: int
    price: float
    quantity: float
    firstTradeId: int
    lastTradeId: int
    timestamp: int
    isBuyerMaker: bool
    isBestMatch: bool

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "AggTrade":
        return cls(
            aggregateTradeId=int(response["a"]),
            price=float(response["p"]),
            quantity=float(response["q"]),
            firstTradeId=int(response["f"]),
            lastTradeId=int(response["l"]),
            timestamp=int(response["T"]),
            isBuyerMaker=bool(response["m"]),
            isBestMatch=bool(response["M"]),
        )


@dataclass
class OrderBookEntry:
    """Single order book entry (price and quantity)"""

    price: float
    quantity: float


@dataclass
class OrderBook:
    """Data structure for order book depth"""

    lastUpdateId: int
    bids: List[OrderBookEntry]
    asks: List[OrderBookEntry]

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "OrderBook":
        bids = [
            OrderBookEntry(float(item[0]), float(item[1]))
            for item in response.get("bids", [])
        ]
        asks = [
            OrderBookEntry(float(item[0]), float(item[1]))
            for item in response.get("asks", [])
        ]
        return cls(lastUpdateId=int(response["lastUpdateId"]), bids=bids, asks=asks)


@dataclass
class TickerPrice:
    """Data structure for ticker price"""

    symbol: str
    price: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "TickerPrice":
        return cls(symbol=response["symbol"], price=float(response["price"]))


@dataclass
class AvgPrice:
    """Data structure for average price"""

    mins: int
    price: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "AvgPrice":
        return cls(mins=int(response["mins"]), price=float(response["price"]))


@dataclass
class PriceStatsMini:
    """
    Data structure for 24hr price change statistics (MINI version)

    This contains the reduced fields returned when type=MINI is specified.
    """

    symbol: str
    priceChange: float
    lastPrice: float
    openPrice: float
    highPrice: float
    lowPrice: float
    volume: float
    quoteVolume: float
    openTime: int
    closeTime: int
    firstId: int
    lastId: int
    count: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "PriceStatsMini":
        return cls(
            symbol=response["symbol"],
            priceChange=float(response["priceChange"]),
            lastPrice=float(response["lastPrice"]),
            openPrice=float(response["openPrice"]),
            highPrice=float(response["highPrice"]),
            lowPrice=float(response["lowPrice"]),
            volume=float(response["volume"]),
            quoteVolume=float(response["quoteVolume"]),
            openTime=int(response["openTime"]),
            closeTime=int(response["closeTime"]),
            firstId=int(response["firstId"]),
            lastId=int(response["lastId"]),
            count=int(response["count"]),
        )


@dataclass
class PriceStats(PriceStatsMini):
    """
    Data structure for 24hr price change statistics (FULL version)

    This extends PriceStatsMini with additional fields available in the FULL response.
    """

    priceChangePercent: float
    weightedAvgPrice: float
    prevClosePrice: float
    lastQty: float
    bidPrice: float
    bidQty: float
    askPrice: float
    askQty: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "PriceStats":
        # First create a base object with the mini fields
        mini = PriceStatsMini.from_api_response(response)

        # Then extend it with the full fields
        return cls(
            symbol=mini.symbol,
            priceChange=mini.priceChange,
            lastPrice=mini.lastPrice,
            openPrice=mini.openPrice,
            highPrice=mini.highPrice,
            lowPrice=mini.lowPrice,
            volume=mini.volume,
            quoteVolume=mini.quoteVolume,
            openTime=mini.openTime,
            closeTime=mini.closeTime,
            firstId=mini.firstId,
            lastId=mini.lastId,
            count=mini.count,
            # Additional fields for FULL response
            priceChangePercent=float(response["priceChangePercent"]),
            weightedAvgPrice=float(response["weightedAvgPrice"]),
            prevClosePrice=float(response["prevClosePrice"]),
            lastQty=float(response.get("lastQty", 0)),
            bidPrice=float(response.get("bidPrice", 0)),
            bidQty=float(response.get("bidQty", 0)),
            askPrice=float(response.get("askPrice", 0)),
            askQty=float(response.get("askQty", 0)),
        )


@dataclass
class RollingWindowStatsMini:
    """
    Data structure for rolling window price change statistics (MINI version)

    This contains the reduced fields returned when type=MINI is specified.
    """

    symbol: str
    priceChange: float
    lastPrice: float
    openPrice: float
    highPrice: float
    lowPrice: float
    volume: float
    quoteVolume: float
    openTime: int
    closeTime: int
    firstId: int
    lastId: int
    count: int

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "RollingWindowStatsMini":
        return cls(
            symbol=response["symbol"],
            priceChange=float(response["priceChange"]),
            lastPrice=float(response["lastPrice"]),
            openPrice=float(response["openPrice"]),
            highPrice=float(response["highPrice"]),
            lowPrice=float(response["lowPrice"]),
            volume=float(response["volume"]),
            quoteVolume=float(response["quoteVolume"]),
            openTime=int(response["openTime"]),
            closeTime=int(response["closeTime"]),
            firstId=int(response["firstId"]),
            lastId=int(response["lastId"]),
            count=int(response["count"]),
        )


@dataclass
class RollingWindowStats(RollingWindowStatsMini):
    """
    Data structure for rolling window price change statistics (FULL version)

    This extends RollingWindowStatsMini with additional fields available in the FULL response.
    """

    priceChangePercent: float
    weightedAvgPrice: float

    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "RollingWindowStats":
        # First create a base object with the mini fields
        mini = RollingWindowStatsMini.from_api_response(response)

        # Then extend it with the full fields
        return cls(
            symbol=mini.symbol,
            priceChange=mini.priceChange,
            lastPrice=mini.lastPrice,
            openPrice=mini.openPrice,
            highPrice=mini.highPrice,
            lowPrice=mini.lowPrice,
            volume=mini.volume,
            quoteVolume=mini.quoteVolume,
            openTime=mini.openTime,
            closeTime=mini.closeTime,
            firstId=mini.firstId,
            lastId=mini.lastId,
            count=mini.count,
            # Additional fields for FULL response
            priceChangePercent=float(response["priceChangePercent"]),
            weightedAvgPrice=float(response["weightedAvgPrice"]),
        )
