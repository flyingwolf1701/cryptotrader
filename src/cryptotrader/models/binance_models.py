from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union

@dataclass
class PriceData:
    bid: float
    ask: float

@dataclass
class BinanceEndpoints:
    base_url: str = "https://fapi.binance.com"
    wss_url: str = "wss://fstream.binance.com/ws"

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