"""
Binance WebSocket API Current Open Orders Request

This module provides functionality to query execution status of all open orders.
It follows the Binance WebSocket API specifications for the 'openOrders.status' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType
from services.binance.models import OrderStatusResponse

logger = get_logger(__name__)

async def get_current_open_orders(
    connection: BinanceWebSocketConnection,
    symbol: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Query execution status of all open orders.
    
    Endpoint: openOrders.status
    Weight: 
        - With symbol: 3
        - Without symbol: 40
    Security Type: USER_DATA (Requires API key and signature)
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT') (optional)
                If omitted, open orders for all symbols are returned
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
    """
    # Prepare request parameters
    params = {}
    
    if symbol:
        params["symbol"] = symbol
    
    # Send the request with USER_DATA security type (requires API key and signature)
    msg_id = await connection.send(
        method="openOrders.status",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    symbol_info = f"for {symbol}" if symbol else "for all symbols"
    logger.debug(f"Sent current open orders request {symbol_info} with ID: {msg_id}")
    return msg_id

async def process_open_orders_response(response: Dict[str, Any]) -> Optional[List[OrderStatusResponse]]:
    """
    Process the open orders response and convert it to a list of OrderStatusResponse objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of OrderStatusResponse objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid open orders response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [OrderStatusResponse.from_api_response(order) for order in result]
    except Exception as e:
        logger.error(f"Error processing open orders response: {str(e)}")
        return None
