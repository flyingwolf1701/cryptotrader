"""
Binance WebSocket API Current Average Price Request

This module provides functionality to retrieve the current average price for a trading symbol.
It follows the Binance WebSocket API specifications for the 'avgPrice' endpoint.
"""

from typing import Dict, Optional, Any, Callable, Awaitable

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import AvgPrice

logger = get_logger(__name__)

async def get_avg_price(
    connection: BinanceWebSocketConnection,
    symbol: str,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve current average price for a trading symbol.
    
    Gets the current average price for the specified symbol.
    
    Endpoint: avgPrice
    Weight: 1
    Security Type: NONE (Public endpoint)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Prepare request parameters
    params = {"symbol": symbol}
    
    # Send the request
    msg_id = await connection.send(
        method="avgPrice",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent average price request for {symbol} with ID: {msg_id}")
    return msg_id

async def process_avg_price_response(response: Dict[str, Any]) -> Optional[AvgPrice]:
    """
    Process the average price response and convert it to an AvgPrice object.
    
    Args:
        response: WebSocket response data
        
    Returns:
        AvgPrice object if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid average price response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return AvgPrice.from_api_response(result)
    except Exception as e:
        logger.error(f"Error processing average price response: {str(e)}")
        return None