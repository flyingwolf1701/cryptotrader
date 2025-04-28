"""
Binance WebSocket API Trade History Request

This module provides functionality to retrieve trade history via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'myTrades' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType
from services.binance.models.order_models import OrderTrade

logger = get_logger(__name__)

async def get_trade_history(
    connection: BinanceWebSocketConnection,
    symbol: str,
    order_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    from_id: Optional[int] = None,
    limit: Optional[int] = None,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve trade history for a trading symbol.
    
    Gets information about all trades for a specific symbol, filtered by 
    time range, order ID, or trade ID.
    
    Endpoint: myTrades
    Weight: 10
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Memory => Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        order_id: Filter by order ID (optional)
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        from_id: Trade ID to fetch from (optional)
        limit: Number of results (default 500, max 1000) (optional)
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
        
    Notes:
        - If fromId is specified, return trades with trade ID >= fromId.
        - If startTime and/or endTime are specified, trades are filtered by execution time (time).
        - fromId cannot be used together with startTime and endTime.
        - If orderId is specified, only trades related to that order are returned.
        - startTime and endTime cannot be used together with orderId.
        - If no condition is specified, the most recent trades are returned.
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
    
    if from_id is not None:
        if not isinstance(from_id, int):
            raise ValueError("from_id must be an integer")
        # fromId cannot be used with startTime and endTime
        if start_time is not None or end_time is not None:
            raise ValueError("from_id cannot be used together with start_time and end_time")
    
    if order_id is not None and (start_time is not None or end_time is not None):
        raise ValueError("startTime and endTime cannot be used together with orderId")
    
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
    
    if from_id is not None:
        params["fromId"] = from_id
    
    if limit is not None:
        params["limit"] = limit
        
    if recv_window is not None:
        params["recvWindow"] = recv_window
    
    # Send the request with USER_DATA security type
    # This requires API key and signature which will be added automatically
    msg_id = await connection.send(
        method="myTrades",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent trade history request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_trade_history_response(response: Dict[str, Any]) -> Optional[List[OrderTrade]]:
    """
    Process the trade history response and convert it to a list of OrderTrade objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of OrderTrade objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid trade history response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [OrderTrade.from_api_response(trade) for trade in result]
    except Exception as e:
        logger.error(f"Error processing trade history response: {str(e)}")
        return None