"""
Binance WebSocket API Create New OCO Order Request

This module provides functionality to place a new one-cancels-the-other (OCO) order pair.
It follows the Binance WebSocket API specifications for the 'orderList.place' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import (
    OrderSide,
    TimeInForce,
    NewOrderResponseType,
    OcoOrderResponse,
)

logger = get_logger(__name__)


async def create_new_oco_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    side: OrderSide,
    quantity: float,
    price: float,
    stopPrice: Optional[float] = None,
    trailing_delta: Optional[int] = None,
    stop_limit_price: Optional[float] = None,
    stop_limit_time_in_force: Optional[TimeInForce] = None,
    list_client_order_id: Optional[str] = None,
    limit_client_order_id: Optional[str] = None,
    stop_client_order_id: Optional[str] = None,
    limit_iceberg_qty: Optional[float] = None,
    stop_iceberg_qty: Optional[float] = None,
    new_order_resp_type: Optional[NewOrderResponseType] = None,
    selfTradePreventionMode: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Create a new one-cancels-the-other (OCO) order pair.

    Endpoint: orderList.place
    Weight: 1
    Security Type: TRADE (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        side: Order side (BUY or SELL)
        quantity: Order quantity
        price: Price for the limit order
        stopPrice: Stop price for the stop order
        trailing_delta: Trailing delta for trailing stop orders
        stop_limit_price: Stop limit price (required for STOP_LOSS_LIMIT leg)
        stop_limit_time_in_force: Time in force for stop limit order
        list_client_order_id: Client order ID for the OCO as a whole
        limit_client_order_id: Client order ID for the limit leg
        stop_client_order_id: Client order ID for the stop leg
        limit_iceberg_qty: Iceberg quantity for limit leg
        stop_iceberg_qty: Iceberg quantity for stop leg
        new_order_resp_type: Response type (ACK, RESULT, FULL)
        selfTradePreventionMode: Self trade prevention mode
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    if not isinstance(side, OrderSide):
        raise ValueError(f"Side must be a valid OrderSide value (BUY or SELL)")

    if not price:
        raise ValueError("Price is required for OCO orders")

    if not quantity:
        raise ValueError("Quantity is required for OCO orders")

    if stopPrice is None and trailing_delta is None:
        raise ValueError(
            "Either stopPrice or trailingDelta must be provided for OCO orders"
        )

    # Validate stop limit order parameters
    if stop_limit_price is not None and stop_limit_time_in_force is None:
        raise ValueError(
            "stopLimitTimeInForce is required when stopLimitPrice is provided"
        )

    # Validate iceberg parameters
    if stop_iceberg_qty is not None and stop_limit_time_in_force != TimeInForce.GTC:
        raise ValueError("If stopIcebergQty is used, stopLimitTimeInForce must be GTC")

    # Prepare request parameters
    params = {
        "symbol": symbol,
        "side": side.value,
        "quantity": quantity,
        "price": price,
    }

    # Add optional parameters
    if stopPrice is not None:
        params["stopPrice"] = stopPrice

    if trailing_delta is not None:
        params["trailingDelta"] = trailing_delta

    if stop_limit_price is not None:
        params["stopLimitPrice"] = stop_limit_price

    if stop_limit_time_in_force is not None:
        params["stopLimitTimeInForce"] = stop_limit_time_in_force.value

    if list_client_order_id is not None:
        params["listClientOrderId"] = list_client_order_id

    if limit_client_order_id is not None:
        params["limitClientOrderId"] = limit_client_order_id

    if stop_client_order_id is not None:
        params["stopClientOrderId"] = stop_client_order_id

    if limit_iceberg_qty is not None:
        params["limitIcebergQty"] = limit_iceberg_qty

    if stop_iceberg_qty is not None:
        params["stopIcebergQty"] = stop_iceberg_qty

    if new_order_resp_type is not None:
        params["newOrderRespType"] = new_order_resp_type.value

    if selfTradePreventionMode is not None:
        params["selfTradePreventionMode"] = selfTradePreventionMode

    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="orderList.place", params=params, security_type=SecurityType.TRADE
    )

    logger.debug(
        f"Sent create OCO order request for {symbol} {side.value} with ID: {msg_id}"
    )
    return msg_id


async def process_create_oco_order_response(
    response: Dict[str, Any],
) -> Optional[OcoOrderResponse]:
    """
    Process the create OCO order response and convert it to an OcoOrderResponse object.

    Args:
        response: WebSocket response data

    Returns:
        OcoOrderResponse object if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid create OCO order response: missing 'result' field")
        return None

    try:
        result = response["result"]
        return OcoOrderResponse.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing create OCO order response: {str(e)}")
        return None
