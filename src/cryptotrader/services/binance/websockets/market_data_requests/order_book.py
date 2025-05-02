"""
Binance WebSocket API Order Book Request

This module provides functionality to retrieve order book data for a trading symbol.
It follows the Binance WebSocket API specifications for the 'depth' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType
from services.binance.models import OrderBook

logger = get_logger(__name__)

async def get_order_book_ws(
    connection: BinanceWebSocketConnection,
    symbol: str,
    limit: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve order book data for a trading symbol.
    
    Gets the current order book (market depth) for the specified symbol.
    Note that this request returns limited market depth and should not
    be used for maintaining a full order book. For continuous updates,
    consider using WebSocket Streams instead.
    
    Endpoint: depth
    Weight: Adjusted based on limit:
            1-100: 1
            101-500: 5
            501-1000: 10
            1001-5000: 50
    Security Type: NONE (Public endpoint)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        limit: Number of price levels to return (default 100, max 5000)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Validate limit parameter
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        if limit > 5000:
            raise ValueError("Limit cannot exceed 5000")
    
    # Prepare request parameters
    params = {"symbol": symbol}
    if limit is not None:
        params["limit"] = limit
    
    # Send the request
    msg_id = await connection.send(
        method="depth",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent order book request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_order_book_response(response: Dict[str, Any]) -> Optional[OrderBook]:
    """
    Process the order book response and convert it to an OrderBook object.
    
    Args:
        response: WebSocket response data
        
    Returns:
        OrderBook object if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid order book response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return OrderBook.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing order book response: {str(e)}")
        return None
