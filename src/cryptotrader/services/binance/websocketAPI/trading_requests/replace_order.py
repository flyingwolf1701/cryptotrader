"""
Binance WebSocket API Replace Order Request

This module provides functionality to cancel an existing order and immediately place a new one.
It follows the Binance WebSocket API specifications for the 'order.cancelReplace' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum

from config import get_logger
from services.binance.websockets import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import (
    OrderSide,
    OrderType,
    TimeInForce,
    CancelReplaceResponse,
    NewOrderResponseType,
    CancelReplaceMode,
)

logger = get_logger(__name__)


async def replace_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    cancel_replace_mode: CancelReplaceMode,
    side: OrderSide,
    orderType: OrderType,
    cancel_order_id: Optional[int] = None,
    cancel_orig_client_order_id: Optional[str] = None,
    cancel_new_client_order_id: Optional[str] = None,
    quantity: Optional[float] = None,
    quote_order_qty: Optional[float] = None,
    price: Optional[float] = None,
    timeInForce: Optional[TimeInForce] = None,
    stopPrice: Optional[float] = None,
    trailing_delta: Optional[int] = None,
    icebergQty: Optional[float] = None,
    newClientOrderId: Optional[str] = None,
    new_order_resp_type: Optional[NewOrderResponseType] = None,
    cancel_restrictions: Optional[str] = None,
    selfTradePreventionMode: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Cancel an existing order and immediately place a new order instead of the canceled one.

    Endpoint: order.cancelReplace
    Weight: 1
    Security Type: TRADE (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        cancel_replace_mode: STOP_ON_FAILURE or ALLOW_FAILURE
        side: Order side (BUY or SELL)
        orderType: Order type (LIMIT, MARKET, STOP_LOSS, etc.)
        cancel_order_id: ID of the order to cancel
        cancel_orig_client_order_id: Original client order ID of the order to cancel
        cancel_new_client_order_id: New client order ID for the canceled order
        quantity: Order quantity (required for most order types)
        quote_order_qty: Quote order quantity (required for MARKET orders using quote quantity)
        price: Order price (required for LIMIT and LIMIT_MAKER orders)
        timeInForce: Time in force (GTC, IOC, FOK) (required for LIMIT orders)
        stopPrice: Stop price (required for STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT)
        trailing_delta: Trailing delta for trailing stop orders
        icebergQty: Iceberg quantity for iceberg orders
        newClientOrderId: Client order ID for the new order
        new_order_resp_type: Response type (ACK, RESULT, FULL)
        cancel_restrictions: Cancel restrictions (ONLY_NEW or ONLY_PARTIALLY_FILLED)
        selfTradePreventionMode: Self trade prevention mode
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    if not isinstance(cancel_replace_mode, CancelReplaceMode):
        raise ValueError(f"cancelReplaceMode must be a valid CancelReplaceMode value")

    if not isinstance(side, OrderSide):
        raise ValueError(f"Side must be a valid OrderSide value (BUY or SELL)")

    if not isinstance(orderType, OrderType):
        raise ValueError(f"Order type must be a valid OrderType value")

    if cancel_order_id is None and cancel_orig_client_order_id is None:
        raise ValueError(
            "Either cancelOrderId or cancelOrigClientOrderId must be provided"
        )

    # Validate parameters based on order type
    if orderType == OrderType.LIMIT:
        if price is None:
            raise ValueError("Price is required for LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for LIMIT orders")
        if timeInForce is None:
            raise ValueError("Time in force is required for LIMIT orders")

    elif orderType == OrderType.LIMIT_MAKER:
        if price is None:
            raise ValueError("Price is required for LIMIT_MAKER orders")
        if quantity is None:
            raise ValueError("Quantity is required for LIMIT_MAKER orders")

    elif orderType == OrderType.MARKET:
        if quantity is None and quote_order_qty is None:
            raise ValueError(
                "Either quantity or quoteOrderQty must be provided for MARKET orders"
            )

    elif orderType == OrderType.STOP_LOSS:
        if quantity is None:
            raise ValueError("Quantity is required for STOP_LOSS orders")
        if stopPrice is None and trailing_delta is None:
            raise ValueError(
                "Either stopPrice or trailingDelta must be provided for STOP_LOSS orders"
            )

    elif orderType == OrderType.STOP_LOSS_LIMIT:
        if price is None:
            raise ValueError("Price is required for STOP_LOSS_LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for STOP_LOSS_LIMIT orders")
        if timeInForce is None:
            raise ValueError("Time in force is required for STOP_LOSS_LIMIT orders")
        if stopPrice is None and trailing_delta is None:
            raise ValueError(
                "Either stopPrice or trailingDelta must be provided for STOP_LOSS_LIMIT orders"
            )

    elif orderType == OrderType.TAKE_PROFIT:
        if quantity is None:
            raise ValueError("Quantity is required for TAKE_PROFIT orders")
        if stopPrice is None and trailing_delta is None:
            raise ValueError(
                "Either stopPrice or trailingDelta must be provided for TAKE_PROFIT orders"
            )

    elif orderType == OrderType.TAKE_PROFIT_LIMIT:
        if price is None:
            raise ValueError("Price is required for TAKE_PROFIT_LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for TAKE_PROFIT_LIMIT orders")
        if timeInForce is None:
            raise ValueError("Time in force is required for TAKE_PROFIT_LIMIT orders")
        if stopPrice is None and trailing_delta is None:
            raise ValueError(
                "Either stopPrice or trailingDelta must be provided for TAKE_PROFIT_LIMIT orders"
            )

    # Validate iceberg orders
    if icebergQty is not None and timeInForce != TimeInForce.GTC:
        raise ValueError("Iceberg orders must have timeInForce set to GTC")

    # Validate cancel restrictions if provided
    if cancel_restrictions is not None and cancel_restrictions not in [
        "ONLY_NEW",
        "ONLY_PARTIALLY_FILLED",
    ]:
        raise ValueError(
            "Invalid cancelRestrictions. Must be ONLY_NEW or ONLY_PARTIALLY_FILLED"
        )

    # Prepare request parameters
    params = {
        "symbol": symbol,
        "cancelReplaceMode": cancel_replace_mode.value,
        "side": side.value,
        "type": orderType.value,
    }

    # Add cancel parameters
    if cancel_order_id is not None:
        params["cancelOrderId"] = cancel_order_id

    if cancel_orig_client_order_id is not None:
        params["cancelOrigClientOrderId"] = cancel_orig_client_order_id

    if cancel_new_client_order_id is not None:
        params["cancelNewClientOrderId"] = cancel_new_client_order_id

    # Add new order parameters
    if quantity is not None:
        params["quantity"] = quantity

    if quote_order_qty is not None:
        params["quoteOrderQty"] = quote_order_qty

    if price is not None:
        params["price"] = price

    if timeInForce is not None:
        params["timeInForce"] = timeInForce.value

    if stopPrice is not None:
        params["stopPrice"] = stopPrice

    if trailing_delta is not None:
        params["trailingDelta"] = trailing_delta

    if icebergQty is not None:
        params["icebergQty"] = icebergQty

    if newClientOrderId is not None:
        params["newClientOrderId"] = newClientOrderId

    if new_order_resp_type is not None:
        params["newOrderRespType"] = new_order_resp_type.value

    if cancel_restrictions is not None:
        params["cancelRestrictions"] = cancel_restrictions

    if selfTradePreventionMode is not None:
        params["selfTradePreventionMode"] = selfTradePreventionMode

    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="order.cancelReplace", params=params, security_type=SecurityType.TRADE
    )

    logger.debug(
        f"Sent replace order request for {symbol} {side.value} {orderType.value} with ID: {msg_id}"
    )
    return msg_id


async def process_replace_order_response(
    response: Dict[str, Any],
) -> Optional[CancelReplaceResponse]:
    """
    Process the replace order response and convert it to a CancelReplaceResponse object.

    Args:
        response: WebSocket response data

    Returns:
        CancelReplaceResponse object if successful, None otherwise
    """
    if not response:
        logger.error("Invalid replace order response: empty response")
        return None

    try:
        # Check if this is a success response (status 200)
        if "status" in response and response["status"] == 200 and "result" in response:
            result = response["result"]
            return CancelReplaceResponse.from_api_response(result)

        # Check if this is an error response
        if "error" in response and "data" in response["error"]:
            error_data = response["error"]["data"]
            return CancelReplaceResponse.from_api_response(error_data)

        logger.error(f"Unexpected response format: {response}")
        return None
    except Exception as e:
        logger.error(f"Error processing replace order response: {str(e)}")
        return None
