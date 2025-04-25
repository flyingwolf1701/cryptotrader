"""
Binance WebSocket API Historical Trades Request

This module provides functionality to retrieve historical trades for a trading symbol.
It follows the Binance WebSocket API specifications for the 'trades.historical' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from services.binance.models import Trade

logger = get_logger(__name__)

async def get_historical_trades_ws(
    connection: BinanceWebSocketConnection,
    symbol: str,
    from_id: Optional[int] = None,
    limit: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve historical trades for a trading symbol.
    
    Gets older historical trades for the specified symbol. This endpoint
    requires an API key and has database access, resulting in higher weight.
    
    Endpoint: trades.historical
    Weight: 5
    Security Type: MARKET_DATA (Requires API key)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        from_id: Trade ID to fetch from (optional)
        limit: Number of trades to return (default 500, max 1000)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
    Notes:
        - If from_id is not specified, the most recent trades are returned
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Validate parameters
    if from_id is not None and (not isinstance(from_id, int) or from_id < 0):
        raise ValueError("from_id must be a non-negative integer")
    
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")
    
    # Prepare request parameters
    params = {"symbol": symbol}
    
    if from_id is not None:
        params["fromId"] = from_id
    
    if limit is not None:
        params["limit"] = limit
    
    # Send the request with MARKET_DATA security type
    # This requires the API key which will be added automatically
    msg_id = await connection.send(
        method="trades.historical",
        params=params,
        security_type=SecurityType.MARKET_DATA
    )
    
    logger.debug(f"Sent historical trades request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_historical_trades_response(response: Dict[str, Any]) -> Optional[List[Trade]]:
    """
    Process the historical trades response and convert it to a list of Trade objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of Trade objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid historical trades response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [Trade.from_api_response(trade) for trade in result]
    except Exception as e:
        logger.error(f"Error processing historical trades response: {str(e)}")
        return None