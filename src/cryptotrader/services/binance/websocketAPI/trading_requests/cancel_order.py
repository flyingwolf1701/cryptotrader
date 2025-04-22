"""
Binance WebSocket API Cancel Order Request

This module provides functionality to cancel an active order.
It follows the Binance WebSocket API specifications for the 'order.cancel' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import OrderStatusResponse

logger = get_logger(__name__)


async def cancel_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    order_id: Optional[int] = None,
    orig_client_order_id: Optional[str] = None,
    newClientOrderId: Optional[str] = None,
    cancel_restrictions: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Cancel an active order.

    Endpoint: order.cancel
    Weight: 1
    Security Type: TRADE (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        order_id: Order ID (required if orig_client_order_id is not provided)
        orig_client_order_id: Original client order ID (required if order_id is not provided)
        newClientOrderId: New client order ID for the canceled order (optional)
        cancel_restrictions: Cancel restrictions (ONLY_NEW or ONLY_PARTIALLY_FILLED)
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    if order_id is None and orig_client_order_id is None:
        raise ValueError("Either orderId or origClientOrderId must be provided")

    # Validate cancel restrictions if provided
    if cancel_restrictions is not None and cancel_restrictions not in [
        "ONLY_NEW",
        "ONLY_PARTIALLY_FILLED",
    ]:
        raise ValueError(
            "Invalid cancelRestrictions. Must be ONLY_NEW or ONLY_PARTIALLY_FILLED"
        )

    # Prepare request parameters
    params = {"symbol": symbol}

    if order_id is not None:
        params["orderId"] = order_id

    if orig_client_order_id is not None:
        params["origClientOrderId"] = orig_client_order_id

    if newClientOrderId is not None:
        params["newClientOrderId"] = newClientOrderId

    if cancel_restrictions is not None:
        params["cancelRestrictions"] = cancel_restrictions

    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="order.cancel", params=params, security_type=SecurityType.TRADE
    )

    logger.debug(f"Sent cancel order request for {symbol} with ID: {msg_id}")
    return msg_id


async def process_cancel_order_response(
    response: Dict[str, Any],
) -> Optional[OrderStatusResponse]:
    """
    Process the cancel order response and convert it to an OrderStatusResponse object.

    Args:
        response: WebSocket response data

    Returns:
        OrderStatusResponse object if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid cancel order response: missing 'result' field")
        return None

    try:
        result = response["result"]
        return OrderStatusResponse.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing cancel order response: {str(e)}")
        return None
