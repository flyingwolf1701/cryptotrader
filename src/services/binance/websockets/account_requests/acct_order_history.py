"""
Binance WebSocket API Order History Request

This module provides functionality to retrieve order history via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'allOrders' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType
from services.binance.models import OrderStatusResponse

logger = get_logger(__name__)

async def get_order_history(
    connection: BinanceWebSocketConnection,
    symbol: str,
    order_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: Optional[int] = None,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve historical orders for a trading symbol.
    
    Gets information about all orders (active, canceled, filled) for a specific 
    symbol, filtered by time range or order ID.
    
    Endpoint: allOrders
    Weight: 10
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        order_id: Order ID to begin at (optional)
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        limit: Number of results (default 500, max 1000) (optional)
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
        
    Notes:
        - If startTime and/or endTime are specified, orderId is ignored.
        - Orders are filtered by time of the last execution status update.
        - If orderId is specified, return orders with order ID >= orderId.
        - If no condition is specified, the most recent orders are returned.
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Validate parameters
    if order_id is not None and not isinstance(order_id, int):
        raise ValueError("order_id must be an integer")
    
    if start_time is not None and not isinstance(start_time, int):
        raise ValueError("start_time must be an integer timestamp in milliseconds")
    
    if end_time is not None and not isinstance(end_time, int):
        raise ValueError("end_time must be an integer timestamp in milliseconds")
    
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if limit > 1000:
            raise ValueError("limit cannot exceed 1000")
    
    if recv_window is not None:
        if not isinstance(recv_window, int) or recv_window <= 0:
            raise ValueError("recv_window must be a positive integer")
        if recv_window > 60000:
            raise ValueError("recv_window cannot exceed 60000")
    
    # Prepare request parameters
    params = {"symbol": symbol}
    
    if order_id is not None:
        params["orderId"] = order_id
    
    if start_time is not None:
        params["startTime"] = start_time
    
    if end_time is not None:
        params["endTime"] = end_time
    
    if limit is not None:
        params["limit"] = limit
        
    if recv_window is not None:
        params["recvWindow"] = recv_window
    
    # Send the request with USER_DATA security type
    # This requires API key and signature which will be added automatically
    msg_id = await connection.send(
        method="allOrders",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent order history request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_order_history_response(response: Dict[str, Any]) -> Optional[List[OrderStatusResponse]]:
    """
    Process the order history response and convert it to a list of OrderStatusResponse objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of OrderStatusResponse objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid order history response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [OrderStatusResponse.from_api_response(order) for order in result]
    except Exception as e:
        logger.error(f"Error processing order history response: {str(e)}")
        return None