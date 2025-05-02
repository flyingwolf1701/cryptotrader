# File: src/gui/unified_clients/binanceRestUnifiedClient.py

from typing import Optional, List, Set, Union

from config import get_logger
from services.binance.restAPI.systemApi import SystemOperations
from services.binance.restAPI.orderApi import OrderOperations

# Import only the real classes that actually exist:
from services.binance.models.base_models import OrderRequest, OrderStatus, ExchangeInfo  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
from services.binance.models.order_models import (
    OrderResponseFull,
    OrderResponseResult,
    OrderResponseAck,
    CancelReplaceResponse,
    OrderTrade,
)  # :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}


logger = get_logger(__name__)


class BinanceRestUnifiedClient:
    """
    Unified client for accessing major Binance REST functionalities.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = SystemOperations()
        self.orders = OrderOperations()
    
    def get_binance_symbols(self, only_trading: bool = True) -> Set[str]:
        """
        Return the current set of Binance symbols (defaults to only those in TRADING status).
        """
        return self.system.get_binance_symbols(only_trading)

    def get_24h_ticker_price(
        self, symbol: Optional[str] = None
    ) -> Union[List[dict], dict]:
        """
        Fetch 24-hour ticker price change statistics for a symbol or all symbols.
        """
        req = self.system.request(
            method="GET",
            endpoint="/api/v3/ticker/24hr",
        ).requiresAuth(False)

        if symbol:
            req = req.withQueryParams(symbol=symbol)
        return req.execute()

    def place_order(self, request: OrderRequest) -> OrderResponseFull:
        """
        Place a new spot order.
        """
        return self.orders.place_order(request)

    def cancel_order(self, order_id: str, symbol: str) -> OrderResponseAck:
        """
        Cancel an existing spot order by order ID and symbol.
        """
        return self.orders.cancelOrderRest(order_id, symbol)

    def get_order_status(self, order_id: str, symbol: str) -> OrderStatus:
        """
        Retrieve the current status of a specific spot order.
        """
        return self.orders.get_order_status(order_id, symbol)

    def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderResponseResult]:
        """
        Retrieve all open spot orders, optionally filtered by symbol.
        """
        return self.orders.get_open_orders(symbol)

    def get_my_trades(self, symbol: str) -> List[OrderTrade]:
        """
        Retrieve past trades for a given symbol.
        """
        return self.orders.get_my_trades(symbol)

    def cancel_replace_order(self, params: dict) -> CancelReplaceResponse:
        """
        Cancel an existing order and place a new one atomically.
        `params` should include the fields required by your
        `OrderOperations.cancel_replace_order` implementation.
        """
        return self.orders.cancel_replace_order(params)
