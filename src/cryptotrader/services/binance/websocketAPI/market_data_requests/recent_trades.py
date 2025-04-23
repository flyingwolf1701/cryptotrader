"""
Binance WebSocket API Recent Trades Request

This module provides functionality to retrieve recent trades for a trading symbol.
It follows the Binance WebSocket API specifications for the 'trades.recent' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import Trade

logger = get_logger(__name__)

async def get_recent_trades_ws(
    connection: BinanceWebSocketConnection,
    symbol: str,
    limit: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve recent trades for a trading symbol.
    
    Gets a list of recent trades for the specified symbol. For real-time 
    trading activity, consider using WebSocket Streams instead.
    
    Endpoint: trades.recent
    Weight: 1
    Security Type: NONE (Public endpoint)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        limit: Number of trades to return (default 500, max 1000)
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
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")
    
    # Prepare request parameters
    params = {"symbol": symbol}
    if limit is not None:
        params["limit"] = limit
    
    # Send the request
    msg_id = await connection.send(
        method="trades.recent",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent recent trades request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_recent_trades_response(response: Dict[str, Any]) -> Optional[List[Trade]]:
    """
    Process the recent trades response and convert it to a list of Trade objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of Trade objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid recent trades response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [Trade.from_api_response(trade) for trade in result]
    except Exception as e:
        logger.error(f"Error processing recent trades response: {str(e)}")
        return None