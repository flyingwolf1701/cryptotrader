"""
Binance WebSocket API OCO Order History Request

This module provides functionality to retrieve OCO order history via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'allOrderLists' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType
from services.binance.models.order_models import OcoOrderResponse

logger = get_logger(__name__)

async def get_oco_history(
    connection: BinanceWebSocketConnection,
    from_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: Optional[int] = None,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve historical OCO orders.
    
    Gets information about all OCO (One-Cancels-the-Other) orders, filtered 
    by time range or order list ID.
    
    Endpoint: allOrderLists
    Weight: 10
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        from_id: Order list ID to begin at (optional)
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        limit: Number of results (default 500, max 1000) (optional)
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If parameters are invalid
        
    Notes:
        - If startTime and/or endTime are specified, fromId is ignored.
        - OCOs are filtered by transactionTime of the last OCO execution status update.
        - If fromId is specified, return OCOs with order list ID >= fromId.
        - If no condition is specified, the most recent OCOs are returned.
    """
    # Validate parameters
    if from_id is not None and not isinstance(from_id, int):
        raise ValueError("from_id must be an integer")
    
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
    params = {}
    
    if from_id is not None:
        params["fromId"] = from_id
    
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
        method="allOrderLists",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent OCO order history request with ID: {msg_id}")
    return msg_id

async def process_oco_history_response(response: Dict[str, Any]) -> Optional[List[OcoOrderResponse]]:
    """
    Process the OCO order history response and convert it to a list of OcoOrderResponse objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of OcoOrderResponse objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid OCO order history response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [OcoOrderResponse.from_api_response(oco) for oco in result]
    except Exception as e:
        logger.error(f"Error processing OCO order history response: {str(e)}")
        return None
