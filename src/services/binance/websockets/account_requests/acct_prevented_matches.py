"""
Binance WebSocket API Prevented Matches Request

This module provides functionality to retrieve self-trade prevention matches via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'myPreventedMatches' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from services.binance.models.order_models import PreventedMatch

logger = get_logger(__name__)

async def get_prevented_matches(
    connection: BinanceWebSocketConnection,
    symbol: str,
    prevented_match_id: Optional[int] = None,
    order_id: Optional[int] = None,
    from_prevented_match_id: Optional[int] = None,
    limit: Optional[int] = None,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve self-trade prevention matches for a trading symbol.
    
    Gets information about orders that were expired due to self-trade prevention (STP).
    These are orders that would have matched against the user's own orders.
    
    Endpoint: myPreventedMatches
    Weight: 1-10 (depends on query type)
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        prevented_match_id: Filter by specific prevented match ID (optional)
        order_id: Filter by order ID (optional)
        from_prevented_match_id: Prevented match ID to fetch from (optional)
        limit: Number of results (default 500, max 1000) (optional)
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
        
    Notes:
        - Supported combinations:
          - symbol + preventedMatchId
          - symbol + orderId
          - symbol + orderId + fromPreventedMatchId (limit defaults to 500)
          - symbol + orderId + fromPreventedMatchId + limit
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Check for valid parameter combinations
    if prevented_match_id is not None and order_id is not None:
        raise ValueError("Cannot specify both prevented_match_id and order_id")
    
    if from_prevented_match_id is not None and prevented_match_id is not None:
        raise ValueError("Cannot specify both from_prevented_match_id and prevented_match_id")
    
    if from_prevented_match_id is not None and order_id is None:
        raise ValueError("When using from_prevented_match_id, order_id must be specified")
    
    # Validate parameters
    if prevented_match_id is not None and not isinstance(prevented_match_id, int):
        raise ValueError("prevented_match_id must be an integer")
    
    if order_id is not None and not isinstance(order_id, int):
        raise ValueError("order_id must be an integer")
    
    if from_prevented_match_id is not None and not isinstance(from_prevented_match_id, int):
        raise ValueError("from_prevented_match_id must be an integer")
    
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
    
    if prevented_match_id is not None:
        params["preventedMatchId"] = prevented_match_id
    
    if order_id is not None:
        params["orderId"] = order_id
    
    if from_prevented_match_id is not None:
        params["fromPreventedMatchId"] = from_prevented_match_id
    
    if limit is not None:
        params["limit"] = limit
    
    if recv_window is not None:
        params["recvWindow"] = recv_window
    
    # Send the request with USER_DATA security type
    # This requires API key and signature which will be added automatically
    msg_id = await connection.send(
        method="myPreventedMatches",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent prevented matches request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_prevented_matches_response(response: Dict[str, Any]) -> Optional[List[PreventedMatch]]:
    """
    Process the prevented matches response and convert it to a list of PreventedMatch objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of PreventedMatch objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid prevented matches response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [PreventedMatch.from_api_response(match) for match in result]
    except Exception as e:
        logger.error(f"Error processing prevented matches response: {str(e)}")
        return None