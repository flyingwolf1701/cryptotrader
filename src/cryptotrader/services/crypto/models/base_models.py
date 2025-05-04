"""Crypto.com dataclass stubs paralleling Binance models.
Only what current app needs (Instrument, AccountBalance, Trade).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Instrument:
    instrument_name: str
    quote_currency: str
    base_currency: str
    price_decimals: int
    quantity_decimals: int

@dataclass
class AccountBalance:
    currency: str
    total: float
    available: float

@dataclass
class Trade:
    trade_id: str
    instrument_name: str
    side: str  # BUY / SELL
    price: float
    quantity: float
    fee: float
    fee_currency: str
    timestamp: datetime