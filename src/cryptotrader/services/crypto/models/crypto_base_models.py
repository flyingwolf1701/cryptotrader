# File: cryptotrader/services/cryptocom/models/crypto_base_models.py
"""
Crypto.com Exchange Data Models

Defines enums and dataclasses for Crypto.com Exchange API requests and responses.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"


class TimeInForce(str, Enum):
    GOOD_TILL_CANCEL = "GOOD_TILL_CANCEL"
    FILL_OR_KILL = "FILL_OR_KILL"
    IMMEDIATE_OR_CANCEL = "IMMEDIATE_OR_CANCEL"


@dataclass
class Instrument:
    instrument_name: str
    base_ccy: str
    quote_ccy: str
    quote_decimals: int
    quantity_decimals: int
    max_leverage: Optional[str] = None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Instrument':
        return cls(
            instrument_name=data.get('instrument_name') or data.get('symbol'),
            base_ccy=data['base_ccy'],
            quote_ccy=data['quote_ccy'],
            quote_decimals=int(data.get('quote_decimals', 0)),
            quantity_decimals=int(data.get('quantity_decimals', 0)),
            max_leverage=data.get('max_leverage'),
        )


@dataclass
class PriceData:
    bid: float
    ask: float

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'PriceData':
        return cls(
            bid=float(data.get('bid_price') or data.get('best_bid')),  # normalize keys
            ask=float(data.get('ask_price') or data.get('best_ask')),
        )


@dataclass
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @classmethod
    def from_api(cls, arr: List[Any]) -> 'Candle':
        # Assumes [t, o, h, l, c, v]
        return cls(
            timestamp=int(arr[0]),
            open=float(arr[1]),
            high=float(arr[2]),
            low=float(arr[3]),
            close=float(arr[4]),
            volume=float(arr[5]),
        )


@dataclass
class Trade:
    trade_id: int
    price: float
    quantity: float
    side: OrderSide

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Trade':
        return cls(
            trade_id=int(data.get('trade_id', data.get('id', 0))),
            price=float(data.get('price', data.get('traded_price', 0))),
            quantity=float(data.get('quantity', data.get('traded_quantity', 0))),
            side=OrderSide(data.get('side') or data.get('taker_side') or 'BUY'),
        )


@dataclass
class AccountAsset:
    ccy: str
    available: float
    frozen: float

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'AccountAsset':
        return cls(
            ccy=data['ccy'],
            available=float(data.get('available', 0)),
            frozen=float(data.get('freeze') or data.get('frozen', 0)),
        )


@dataclass
class AccountBalance:
    assets: Dict[str, AccountAsset]

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'AccountBalance':
        accounts = data.get('accounts') or data.get('data') or []
        assets: Dict[str, AccountAsset] = {}
        for item in accounts:
            asset = AccountAsset.from_api(item)
            assets[asset.ccy] = asset
        return cls(assets=assets)
