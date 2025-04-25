"""
Binance WebSocket API Query Order Request

This module provides functionality to check execution status of an order.
It follows the Binance WebSocket API specifications for the 'order.status' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from services.binance.models import OrderStatusResponse

logger = get_logger(__name__)

async def query_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    order_id: Optional[int] = None,
    orig_client_order_id: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Check execution status of an order.
    
    Endpoint: order.status
    Weight: 2
    Security Type: USER_DATA (Requires API key and signature)
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        order_id: Order ID (required if orig_client_order_id is not provided)
        orig_client_order_id: Original client order ID (required if order_id is not provided)
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
    
    # Prepare request parameters
    params = {"symbol": symbol}
    
    if order_id is not None:
        params["orderId"] = order_id
    
    if orig_client_order_id is not None:
        params["origClientOrderId"] = orig_client_order_id
    
    # Send the request with USER_DATA security type (requires API key and signature)
    msg_id = await connection.send(
        method="order.status",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent query order request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_query_order_response(response: Dict[str, Any]) -> Optional[OrderStatusResponse]:
    """
    Process the query order response and convert it to an OrderStatusResponse object.
    
    Args:
        response: WebSocket response data
        
    Returns:
        OrderStatusResponse object if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid query order response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return OrderStatusResponse.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing query order response: {str(e)}")
        return None