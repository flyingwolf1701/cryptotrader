# File: src/gui/unified_clients/binanceRestUnifiedClient.py
"""
Binance REST API Unified Client

This module provides a unified client for interacting with the Binance REST API.
It combines the functionality from:
- Market data operations
- Order operations
- Wallet operations
- User account operations
- System-wide information

The client automatically handles authentication and rate limiting through
the underlying implementation in base_operations.
"""

from typing import Optional, List, Union

from config import get_logger
from services.binance.restAPI.system_api import SystemOperations
from services.binance.restAPI.order_api import OrderOperations
from services.binance.models import (
    PlaceOrderRequest, # does not exist halucination
    CancelReplaceRequest, # does not exist halucination
    OrderResult, # does not exist halucination
    CancelResult, # does not exist halucination
    OrderStatus,
    OrderSummary, # does not exist halucination
    TradeRecord, # does not exist halucination
    ExchangeInfo
)

logger = get_logger(__name__)


class BinanceRestUnifiedClient:
    """
    Unified client for accessing major Binance REST functionalities.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = SystemOperations()
        self.orders = OrderOperations()

    def get_exchange_info_public(self) -> ExchangeInfo:
        """
        Fetch public exchange information (symbols, trading rules, etc.).
        """
        return self.system.get_exchange_info()

    def get_24h_ticker_price(self, symbol: Optional[str] = None) -> Union[List[dict], dict]:
        """
        Fetch 24-hour ticker price change statistics for a symbol or all symbols.
        """
        if symbol:
            response = self.system.request(
                method="GET",
                endpoint="/api/v3/ticker/24hr",
            ).with_query_params(symbol=symbol).requires_auth(False).execute()
            return response
        else:
            response = self.system.request(
                method="GET",
                endpoint="/api/v3/ticker/24hr",
            ).requires_auth(False).execute()
            return response

    def place_order(self, request: PlaceOrderRequest) -> OrderResult:
        """
        Place a new spot order.
        """
        return self.orders.place_order(request)

    def cancel_order(self, order_id: str, symbol: str) -> CancelResult:
        """
        Cancel an existing spot order by order ID and symbol.
        """
        return self.orders.cancel_order(order_id, symbol)

    def get_order_status(self, order_id: str, symbol: str) -> OrderStatus:
        """
        Retrieve the current status of a specific spot order.
        """
        return self.orders.get_order_status(order_id, symbol)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderSummary]:
        """
        Retrieve all open spot orders, optionally filtered by symbol.
        """
        return self.orders.get_open_orders(symbol)

    def get_my_trades(self, symbol: str) -> List[TradeRecord]:
        """
        Retrieve past trades for a given symbol.
        """
        return self.orders.get_my_trades(symbol)

    def cancel_replace_order(self, request: CancelReplaceRequest) -> OrderResult:
        """
        Cancel an existing order and place a new one atomically.
        """
        return self.orders.cancel_replace_order(request)
