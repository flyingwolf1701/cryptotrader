"""
Binance WebSocket API Get OCO Order Request

This module provides functionality to check execution status of an OCO order.
It follows the Binance WebSocket API specifications for the 'orderList.status' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websockets.baseOperations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import OcoOrderResponse

logger = get_logger(__name__)


async def getOcoOrderWS(
    connection: BinanceWebSocketConnection,
    order_list_id: Optional[int] = None,
    orig_client_order_id: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Check execution status of an OCO order.

    Endpoint: orderList.status
    Weight: 2
    Security Type: USER_DATA (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        order_list_id: OCO order list ID
        orig_client_order_id: Original client order list ID (listClientOrderId of the OCO)
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if order_list_id is None and orig_client_order_id is None:
        raise ValueError("Either orderListId or origClientOrderId must be provided")

    # Prepare request parameters
    params = {}

    if order_list_id is not None:
        params["orderListId"] = order_list_id

    if orig_client_order_id is not None:
        params["origClientOrderId"] = orig_client_order_id

    # Send the request with USER_DATA security type (requires API key and signature)
    msg_id = await connection.send(
        method="orderList.status", params=params, security_type=SecurityType.USER_DATA
    )

    id_info = (
        f"orderListId={order_list_id}"
        if order_list_id
        else f"origClientOrderId={orig_client_order_id}"
    )
    logger.debug(f"Sent get OCO order request ({id_info}) with ID: {msg_id}")
    return msg_id


async def process_get_oco_order_response(
    response: Dict[str, Any],
) -> Optional[OcoOrderResponse]:
    """
    Process the get OCO order response and convert it to an OcoOrderResponse object.

    Args:
        response: WebSocket response data

    Returns:
        OcoOrderResponse object if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid get OCO order response: missing 'result' field")
        return None

    try:
        result = response["result"]
        return OcoOrderResponse.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing get OCO order response: {str(e)}")
        return None
