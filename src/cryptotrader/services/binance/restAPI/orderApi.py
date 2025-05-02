"""
Binance REST API Order Operations

This module provides order management functionality for the Binance API.
It includes functions for:
- Placing new orders
- Canceling existing orders
- Checking order status
- Retrieving order history
- Getting open orders
- Managing trades
- Cancel-replace operations
- Querying self-trade prevention matches

These functions handle trading operations via the Binance API.
"""

from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.models import (
    OrderRequest,
    OrderStatusResponse,
    RateLimitType,
    OrderResponseFull,
    OrderResponseResult,
    OrderResponseAck,
    CancelReplaceResponse,
    OrderTrade,
    PreventedMatch,
    RateLimitInfo,
    OcoOrderResponse,
)
from cryptotrader.services.binance.restAPI.baseOperations import BinanceAPIRequest

logger = get_logger(__name__)


class OrderOperations:
    """
    Binance REST API order operations.

    Provides methods for managing orders via the Binance API.
    """

    def __init__(self):
        """Initialize the Order operations client."""
        pass

    def request(
        self,
        method: str,
        endpoint: str,
        limit_type: Optional[RateLimitType] = None,
        weight: int = 1,
    ) -> BinanceAPIRequest:
        """
        Create a new API request.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            limit_type: Type of rate limit for this request
            weight: Weight of this request for rate limiting

        Returns:
            BinanceAPIRequest object for building and executing the request
        """
        return BinanceAPIRequest(
            method=method, endpoint=endpoint, limit_type=limit_type, weight=weight
        )

    def placeSpotOrder(
        self, order_request: Union[OrderRequest, Dict[str, Any]]
    ) -> Optional[OrderStatusResponse]:
        """
        Place a new order.

        POST /api/v3/order
        Weight: 1

        Args:
            order_request: The order details as OrderRequest object or dictionary

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        # Convert OrderRequest to dictionary if needed
        if isinstance(order_request, OrderRequest):
            params = {
                "symbol": order_request.symbol,
                "side": order_request.side.value,
                "type": order_request.orderType.value,
                "quantity": order_request.quantity,
            }

            # Add optional parameters
            if order_request.price is not None:
                params["price"] = order_request.price

            if order_request.timeInForce is not None:
                params["timeInForce"] = order_request.timeInForce.value

            if order_request.stopPrice is not None:
                params["stopPrice"] = order_request.stopPrice

            if order_request.icebergQty is not None:
                params["icebergQty"] = order_request.icebergQty

            if order_request.newClientOrderId is not None:
                params["newClientOrderId"] = order_request.newClientOrderId

            if order_request.selfTradePreventionMode is not None:
                params["selfTradePreventionMode"] = (
                    order_request.selfTradePreventionMode
                )
        else:
            # Already a dictionary
            params = order_request

        response = (
            self.request("POST", "/api/v3/order", RateLimitType.ORDERS, 1)
            .requiresAuth(True)
            .withQueryParams(**params)
            .execute()
        )

        if response:
            return OrderStatusResponse.from_api_response(response)
        return None

    def testNewOrderRest(
        self, order_request: Union[OrderRequest, Dict[str, Any]]
    ) -> bool:
        """
        Test new order creation without actually placing an order.

        POST /api/v3/order/test
        Weight: 1

        Args:
            order_request: The order details as OrderRequest object or dictionary

        Returns:
            True if test was successful, False otherwise
        """
        # Convert OrderRequest to dictionary if needed
        if isinstance(order_request, OrderRequest):
            params = {
                "symbol": order_request.symbol,
                "side": order_request.side.value,
                "type": order_request.orderType.value,
                "quantity": order_request.quantity,
            }

            # Add optional parameters
            if order_request.price is not None:
                params["price"] = order_request.price

            if order_request.timeInForce is not None:
                params["timeInForce"] = order_request.timeInForce.value

            if order_request.stopPrice is not None:
                params["stopPrice"] = order_request.stopPrice

            if order_request.icebergQty is not None:
                params["icebergQty"] = order_request.icebergQty

            if order_request.newClientOrderId is not None:
                params["newClientOrderId"] = order_request.newClientOrderId

            if order_request.selfTradePreventionMode is not None:
                params["selfTradePreventionMode"] = (
                    order_request.selfTradePreventionMode
                )
        else:
            # Already a dictionary
            params = order_request

        response = (
            self.request("POST", "/api/v3/order/test", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(True)
            .withQueryParams(**params)
            .execute()
        )

        # Test order endpoint returns empty dict on success
        return response is not None

    def cancelOrderRest(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        client_order_id: Optional[str] = None,
        newClientOrderId: Optional[str] = None,
        cancel_restrictions: Optional[str] = None,
    ) -> Optional[OrderStatusResponse]:
        """
        Cancel an existing order.

        DELETE /api/v3/order
        Weight: 1

        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            newClientOrderId: Used to uniquely identify this cancel
            cancel_restrictions: Conditions for cancellation (ONLY_NEW, ONLY_PARTIALLY_FILLED)

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        request = (
            self.request("DELETE", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(True)
            .withQueryParams(symbol=symbol)
        )

        if order_id:
            request.withQueryParams(orderId=order_id)
        elif client_order_id:
            request.withQueryParams(origClientOrderId=client_order_id)
        else:
            logger.error(
                "Either order_id or client_order_id must be provided to cancel an order"
            )
            return None

        if newClientOrderId:
            request.withQueryParams(newClientOrderId=newClientOrderId)

        if cancel_restrictions:
            request.withQueryParams(cancelRestrictions=cancel_restrictions)

        response = request.execute()

        if response:
            return OrderStatusResponse.from_api_response(response)
        return None

    def cancel_all_orders(self, symbol: str) -> List[OrderStatusResponse]:
        """
        Cancel all active orders on a symbol.

        DELETE /api/v3/openOrders
        Weight: 1

        Args:
            symbol: The symbol to cancel all orders for (e.g. "BTCUSDT")

        Returns:
            List of OrderStatusResponse objects for each canceled order
        """
        response = (
            self.request(
                "DELETE", "/api/v3/openOrders", RateLimitType.REQUEST_WEIGHT, 1
            )
            .requiresAuth(True)
            .withQueryParams(symbol=symbol)
            .execute()
        )

        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []

    def get_order_status(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        client_order_id: Optional[str] = None,
    ) -> Optional[OrderStatusResponse]:
        """
        Get status of an existing order.

        GET /api/v3/order
        Weight: 2

        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order

        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        request = (
            self.request("GET", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 2)
            .requiresAuth(True)
            .withQueryParams(symbol=symbol)
        )

        if order_id:
            request.withQueryParams(orderId=order_id)
        elif client_order_id:
            request.withQueryParams(origClientOrderId=client_order_id)
        else:
            logger.error(
                "Either order_id or client_order_id must be provided to get order status"
            )
            return None

        response = request.execute()

        if response:
            return OrderStatusResponse.from_api_response(response)
        return None

    def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[OrderStatusResponse]:
        """
        Get all open orders on a symbol or all symbols.

        GET /api/v3/openOrders
        Weight:
        - 3 for a single symbol
        - 40 when the symbol parameter is omitted

        Args:
            symbol: Optional symbol to get open orders for (e.g. "BTCUSDT")
                  If None, gets orders for all symbols

        Returns:
            List of OrderStatusResponse objects with open order details
        """
        # Adjust weight based on parameters
        weight = 3
        if symbol is None:
            weight = 40

        request = self.request(
            "GET", "/api/v3/openOrders", RateLimitType.REQUEST_WEIGHT, weight
        ).requiresAuth(True)

        if symbol:
            request.withQueryParams(symbol=symbol)

        response = request.execute()

        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []

    def get_all_orders(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[OrderStatusResponse]:
        """
        Get all orders (active, canceled, or filled) for a specific symbol.

        GET /api/v3/allOrders
        Weight: 10

        Args:
            symbol: The symbol to get orders for (e.g. "BTCUSDT")
            order_id: If specified, gets orders >= this order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Maximum number of orders to return (default 500, max 1000)

        Returns:
            List of OrderStatusResponse objects with order details
        """
        request = (
            self.request("GET", "/api/v3/allOrders", RateLimitType.REQUEST_WEIGHT, 10)
            .requiresAuth(True)
            .withQueryParams(
                symbol=symbol,
                limit=min(limit, 1000),  # Ensure limit doesn't exceed API max
            )
        )

        if order_id:
            request.withQueryParams(orderId=order_id)

        if start_time:
            request.withQueryParams(startTime=start_time)

        if end_time:
            request.withQueryParams(endTime=end_time)

        response = request.execute()

        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []

    def getOrderRateLimitsRest(self) -> List[RateLimitInfo]:
        """
        Get the current order rate limits for all time intervals.

        GET /api/v3/rateLimit/order
        Weight: 20

        Returns:
            List of RateLimitInfo objects with rate limit details
        """
        response = (
            self.request(
                "GET", "/api/v3/rateLimit/order", RateLimitType.REQUEST_WEIGHT, 20
            )
            .requiresAuth(True)
            .execute()
        )

        if response:
            return [RateLimitInfo.from_api_response(limit) for limit in response]
        return []

    def get_my_trades(
        self,
        symbol: str,
        order_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        from_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[OrderTrade]:
        """
        Get trades for a specific symbol.

        GET /api/v3/myTrades
        Weight: 10

        Args:
            symbol: The symbol to get trades for (e.g. "BTCUSDT")
            order_id: If specified, get trades for this order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            from_id: TradeId to fetch from (gets trades >= from_id)
            limit: Maximum number of trades to return (default 500, max 1000)

        Returns:
            List of OrderTrade objects with trade details
        """
        request = (
            self.request("GET", "/api/v3/myTrades", RateLimitType.REQUEST_WEIGHT, 10)
            .requiresAuth(True)
            .withQueryParams(
                symbol=symbol,
                limit=min(limit, 1000),  # Ensure limit doesn't exceed API max
            )
        )

        if order_id:
            request.withQueryParams(orderId=order_id)

        if start_time:
            request.withQueryParams(startTime=start_time)

        if end_time:
            request.withQueryParams(endTime=end_time)

        if from_id:
            request.withQueryParams(fromId=from_id)

        response = request.execute()

        if response:
            return [OrderTrade.from_api_response(trade) for trade in response]
        return []

    def cancel_replace_order(
        self,
        symbol: str,
        cancel_replace_mode: str,
        side: str,
        type: str,
        cancel_order_id: Optional[int] = None,
        cancel_client_order_id: Optional[str] = None,
        **kwargs,
    ) -> Optional[CancelReplaceResponse]:
        """
        Cancel an existing order and place a new one.

        POST /api/v3/order/cancelReplace
        Weight: 1

        Args:
            symbol: The trading pair (e.g., "BTCUSDT")
            cancel_replace_mode: How to handle failures (STOP_ON_FAILURE or ALLOW_FAILURE)
            side: Order side (BUY or SELL)
            type: Order type (LIMIT, MARKET, etc.)
            cancel_order_id: ID of the order to cancel
            cancel_client_order_id: Client order ID of the order to cancel
            **kwargs: Additional parameters for the new order

        Returns:
            CancelReplaceResponse containing cancellation and new order status
        """
        if not cancel_order_id and not cancel_client_order_id:
            logger.error(
                "Either cancel_order_id or cancel_client_order_id must be provided"
            )
            return None

        params = {
            "symbol": symbol,
            "cancelReplaceMode": cancel_replace_mode,
            "side": side,
            "type": type,
        }

        if cancel_order_id:
            params["cancelOrderId"] = cancel_order_id
        elif cancel_client_order_id:
            params["cancelOrigClientOrderId"] = cancel_client_order_id

        # Add any other parameters
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value

        response = (
            self.request(
                "POST", "/api/v3/order/cancelReplace", RateLimitType.REQUEST_WEIGHT, 1
            )
            .requiresAuth(True)
            .withQueryParams(**params)
            .execute()
        )

        if response:
            return CancelReplaceResponse.from_api_response(response)
        return None

    def getPreventedMatchesRest(
        self,
        symbol: str,
        prevented_match_id: Optional[int] = None,
        order_id: Optional[int] = None,
        from_prevented_match_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[PreventedMatch]:
        """
        Get orders that were expired because of self-trade prevention.

        GET /api/v3/myPreventedMatches
        Weight:
        - 1 for invalid symbol
        - 1 when querying by preventedMatchId
        - 10 when querying by orderId

        Args:
            symbol: The symbol to get prevented matches for
            prevented_match_id: Specific prevented match ID to query
            order_id: Filter by order ID
            from_prevented_match_id: Get matches from this ID onwards
            limit: Maximum number of matches to return (default 500, max 1000)

        Returns:
            List of PreventedMatch objects with match details
        """
        # Default weight to 10 (worst case)
        weight = 10
        if prevented_match_id is not None:
            weight = 1

        request = (
            self.request(
                "GET",
                "/api/v3/myPreventedMatches",
                RateLimitType.REQUEST_WEIGHT,
                weight,
            )
            .requiresAuth(True)
            .withQueryParams(
                symbol=symbol,
                limit=min(limit, 1000),  # Ensure limit doesn't exceed API max
            )
        )

        if prevented_match_id:
            request.withQueryParams(preventedMatchId=prevented_match_id)

        if order_id:
            request.withQueryParams(orderId=order_id)

        if from_prevented_match_id:
            request.withQueryParams(fromPreventedMatchId=from_prevented_match_id)

        response = request.execute()

        if response:
            return [PreventedMatch.from_api_response(match) for match in response]
        return []

    def placeOcoOrder(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stopPrice: float,
        stop_limit_price: Optional[float] = None,
        stop_limit_time_in_force: Optional[str] = None,
        list_client_order_id: Optional[str] = None,
        limit_client_order_id: Optional[str] = None,
        limit_iceberg_qty: Optional[float] = None,
        trailing_delta: Optional[int] = None,
        stop_client_order_id: Optional[str] = None,
        stop_iceberg_qty: Optional[float] = None,
        new_order_resp_type: Optional[str] = None,
        selfTradePreventionMode: Optional[str] = None,
    ) -> Optional[OcoOrderResponse]:
        """
        Place a new OCO (One-Cancels-the-Other) order.

        OCO orders consist of a pair of orders: a limit maker and a stop loss/stop loss limit order.
        When one order executes, the other is automatically canceled.

        POST /api/v3/order/oco
        Weight: 1

        Args:
            symbol: Symbol to place order for (e.g. "BTCUSDT")
            side: Order side (e.g. "BUY", "SELL")
            quantity: Order quantity
            price: Limit order price
            stopPrice: Stop price
            stop_limit_price: Stop limit price, if provided stop_limit_time_in_force is required
            stop_limit_time_in_force: Time in force for stop limit price (GTC/FOK/IOC)
            list_client_order_id: A unique ID for the entire orderList
            limit_client_order_id: A unique ID for the limit order
            limit_iceberg_qty: Iceberg quantity for the limit order
            trailing_delta: Trailing delta for orders
            stop_client_order_id: A unique ID for the stop loss/stop loss limit leg
            stop_iceberg_qty: Iceberg quantity for the stop loss/stop loss limit leg
            new_order_resp_type: Set the response JSON
            selfTradePreventionMode: Self trade prevention mode (default is EXPIRE_MAKER)

        Returns:
            OcoOrderResponse object with order details, or None if failed

        Notes:
            - Price Restrictions:
            - SELL: Limit Price > Last Price > Stop Price
            - BUY: Limit Price < Last Price < Stop Price
            - Quantity Restrictions:
            - Both legs must have the same quantity
            - ICEBERG quantities however do not have to be the same
            - OCO counts as 2 orders against the order rate limit
        """
        params = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "stopPrice": stopPrice,
        }

        # Add optional parameters
        if stop_limit_price is not None:
            params["stopLimitPrice"] = stop_limit_price

        if stop_limit_time_in_force is not None:
            params["stopLimitTimeInForce"] = stop_limit_time_in_force

        if list_client_order_id is not None:
            params["listClientOrderId"] = list_client_order_id

        if limit_client_order_id is not None:
            params["limitClientOrderId"] = limit_client_order_id

        if limit_iceberg_qty is not None:
            params["limitIcebergQty"] = limit_iceberg_qty

        if trailing_delta is not None:
            params["trailingDelta"] = trailing_delta

        if stop_client_order_id is not None:
            params["stopClientOrderId"] = stop_client_order_id

        if stop_iceberg_qty is not None:
            params["stopIcebergQty"] = stop_iceberg_qty

        if new_order_resp_type is not None:
            params["newOrderRespType"] = new_order_resp_type

        if selfTradePreventionMode is not None:
            params["selfTradePreventionMode"] = selfTradePreventionMode

        response = (
            self.request("POST", "/api/v3/order/oco", RateLimitType.ORDERS, 1)
            .requiresAuth(True)
            .withQueryParams(**params)
            .execute()
        )

        if response:
            return OcoOrderResponse.from_api_response(response)
        return None

    def getOcoOrderRest(
        self,
        order_list_id: Optional[int] = None,
        orig_client_order_id: Optional[str] = None,
    ) -> Optional[OcoOrderResponse]:
        """
        Get a specific OCO order status.

        GET /api/v3/orderList
        Weight: 2

        Args:
            order_list_id: ID of the OCO order list
            orig_client_order_id: Original client order ID

        Returns:
            OcoOrderResponse object with order details, or None if not found

        Notes:
            Either order_list_id or orig_client_order_id must be provided
        """
        if not order_list_id and not orig_client_order_id:
            logger.error(
                "Either order_list_id or orig_client_order_id must be provided to get OCO order"
            )
            return None

        request = self.request(
            "GET", "/api/v3/orderList", RateLimitType.REQUEST_WEIGHT, 2
        ).requiresAuth(True)

        if order_list_id:
            request.withQueryParams(orderListId=order_list_id)
        elif orig_client_order_id:
            request.withQueryParams(origClientOrderId=orig_client_order_id)

        response = request.execute()

        if response:
            return OcoOrderResponse.from_api_response(response)
        return None

    def getAllOcoOrders(
        self,
        from_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[OcoOrderResponse]:
        """
        Get all OCO orders based on provided parameters.

        GET /api/v3/allOrderList
        Weight: 10

        Args:
            from_id: If supplied, neither start_time nor end_time can be provided
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Maximum number of orders to return (default 500, max 1000)

        Returns:
            List of OcoOrderResponse objects with order details

        Notes:
            - If from_id is supplied, neither start_time nor end_time can be provided
        """
        request = (
            self.request(
                "GET", "/api/v3/allOrderList", RateLimitType.REQUEST_WEIGHT, 10
            )
            .requiresAuth(True)
            .withQueryParams(
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
        )

        if from_id is not None:
            request.withQueryParams(fromId=from_id)
        else:
            if start_time is not None:
                request.withQueryParams(startTime=start_time)
            if end_time is not None:
                request.withQueryParams(endTime=end_time)

        response = request.execute()

        if response:
            return [OcoOrderResponse.from_api_response(order) for order in response]
        return []

    def getOpenOcoOrdersRest(self) -> List[OcoOrderResponse]:
        """
        Get all open OCO orders.

        GET /api/v3/openOrderList
        Weight: 3

        Returns:
            List of OcoOrderResponse objects with order details
        """
        response = (
            self.request(
                "GET", "/api/v3/openOrderList", RateLimitType.REQUEST_WEIGHT, 3
            )
            .requiresAuth(True)
            .execute()
        )

        if response:
            return [OcoOrderResponse.from_api_response(order) for order in response]
        return []

    def cancel_oco_order(
        self,
        symbol: str,
        order_list_id: Optional[int] = None,
        list_client_order_id: Optional[str] = None,
        newClientOrderId: Optional[str] = None,
    ) -> Optional[OcoOrderResponse]:
        """
        Cancel an entire OCO order list.

        DELETE /api/v3/orderList
        Weight: 1

        Args:
            symbol: Symbol for the orders (e.g. "BTCUSDT")
            order_list_id: ID of the OCO order list
            list_client_order_id: Original client order ID for the OCO order list
            newClientOrderId: Used to uniquely identify this cancel

        Returns:
            OcoOrderResponse object with details of the canceled orders, or None if failed

        Notes:
            - Either order_list_id or list_client_order_id must be provided
            - Canceling an individual leg will cancel the entire OCO
        """
        if not order_list_id and not list_client_order_id:
            logger.error(
                "Either order_list_id or list_client_order_id must be provided to cancel OCO order"
            )
            return None

        request = (
            self.request("DELETE", "/api/v3/orderList", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(True)
            .withQueryParams(symbol=symbol)
        )

        if order_list_id:
            request.withQueryParams(orderListId=order_list_id)
        elif list_client_order_id:
            request.withQueryParams(listClientOrderId=list_client_order_id)

        if newClientOrderId:
            request.withQueryParams(newClientOrderId=newClientOrderId)

        response = request.execute()

        if response:
            return OcoOrderResponse.from_api_response(response)
        return None
