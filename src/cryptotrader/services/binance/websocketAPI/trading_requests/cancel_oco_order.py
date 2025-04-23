"""
Binance WebSocket API Cancel OCO Order Request

This module provides functionality to cancel an active OCO order.
It follows the Binance WebSocket API specifications for the 'orderList.cancel' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import OcoOrderResponse

logger = get_logger(__name__)


async def cancel_oco_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    order_list_id: Optional[int] = None,
    list_client_order_id: Optional[str] = None,
    newClientOrderId: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Cancel an active OCO order.

    Endpoint: orderList.cancel
    Weight: 1
    Security Type: TRADE (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        order_list_id: OCO order list ID
        list_client_order_id: Original client order list ID (listClientOrderId of the OCO)
        newClientOrderId: New client order ID for the canceled OCO
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    if order_list_id is None and list_client_order_id is None:
        raise ValueError("Either orderListId or listClientOrderId must be provided")

    # Prepare request parameters
    params = {"symbol": symbol}

    if order_list_id is not None:
        params["orderListId"] = order_list_id

    if list_client_order_id is not None:
        params["listClientOrderId"] = list_client_order_id

    if newClientOrderId is not None:
        params["newClientOrderId"] = newClientOrderId

    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="orderList.cancel", params=params, security_type=SecurityType.TRADE
    )

    id_info = (
        f"orderListId={order_list_id}"
        if order_list_id
        else f"listClientOrderId={list_client_order_id}"
    )
    logger.debug(
        f"Sent cancel OCO order request for {symbol} ({id_info}) with ID: {msg_id}"
    )
    return msg_id


async def process_cancel_oco_order_response(
    response: Dict[str, Any],
) -> Optional[OcoOrderResponse]:
    """
    Process the cancel OCO order response and convert it to an OcoOrderResponse object.

    Args:
        response: WebSocket response data

    Returns:
        OcoOrderResponse object if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid cancel OCO order response: missing 'result' field")
        return None

    try:
        result = response["result"]
        return OcoOrderResponse.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing cancel OCO order response: {str(e)}")
        return None
