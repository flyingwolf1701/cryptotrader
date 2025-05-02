"""
Binance WebSocket API Cancel Open Orders Request

This module provides functionality to cancel all open orders on a symbol.
It follows the Binance WebSocket API specifications for the 'openOrders.cancelAll' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websockets.baseOperations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import OrderStatusResponse, OcoOrderResponse

logger = get_logger(__name__)


async def cancel_open_orders(
    connection: BinanceWebSocketConnection,
    symbol: str,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Cancel all open orders on a symbol, including OCO orders.

    Endpoint: openOrders.cancelAll
    Weight: 1
    Security Type: TRADE (Requires API key and signature)

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    # Prepare request parameters
    params = {"symbol": symbol}

    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="openOrders.cancelAll", params=params, security_type=SecurityType.TRADE
    )

    logger.debug(f"Sent cancel all open orders request for {symbol} with ID: {msg_id}")
    return msg_id


async def process_cancel_open_orders_response(
    response: Dict[str, Any],
) -> Optional[List[Union[OrderStatusResponse, Dict[str, Any]]]]:
    """
    Process the cancel open orders response.

    The response can contain both individual order cancellations and OCO cancellations.

    Args:
        response: WebSocket response data

    Returns:
        List of OrderStatusResponse objects and OCO cancellation data if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid cancel open orders response: missing 'result' field")
        return None

    try:
        result = response["result"]
        canceled_items = []

        for item in result:
            # Check if this is an OCO order (has orderListId and contingencyType fields)
            if "orderListId" in item and "contingencyType" in item:
                # This is an OCO order cancellation
                canceled_items.append(item)
            else:
                # This is a regular order cancellation
                canceled_items.append(OrderStatusResponse.from_api_response(item))

        return canceled_items
    except Exception as e:
        logger.error(f"Error processing cancel open orders response: {str(e)}")
        return None
