"""
Binance WebSocket API Symbol Price Ticker Request

This module provides functionality to retrieve the latest market price for a trading symbol.
It follows the Binance WebSocket API specifications for the 'ticker.price' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from services.binance.models import TickerPrice

logger = get_logger(__name__)

async def get_price_ticker(
    connection: BinanceWebSocketConnection,
    symbol: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve the latest market price for a symbol or symbols.
    
    Gets the latest price for the specified symbol(s). For real-time
    price updates, consider using WebSocket Streams instead.
    
    Endpoint: ticker.price
    Weight: Adjusted based on parameters:
            symbol: 1
            symbols: 2
            none: 2
    Security Type: NONE (Public endpoint)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT') (optional)
        symbols: List of symbols (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If parameters are invalid or both symbol and symbols are provided
    """
    # Validate parameters
    if symbol and symbols:
        raise ValueError("Cannot use both 'symbol' and 'symbols' parameters together")
    
    # Prepare request parameters
    params = {}
    
    if symbol:
        params["symbol"] = symbol
    
    if symbols:
        if not isinstance(symbols, list):
            raise ValueError("symbols must be a list of strings")
        params["symbols"] = symbols
    
    # Send the request
    msg_id = await connection.send(
        method="ticker.price",
        params=params,
        security_type=SecurityType.NONE
    )
    
    symbol_info = symbol or (f"{len(symbols)} symbols" if symbols else "all symbols")
    logger.debug(f"Sent price ticker request for {symbol_info} with ID: {msg_id}")
    return msg_id

async def process_price_ticker_response(
    response: Dict[str, Any]
) -> Optional[Union[TickerPrice, List[TickerPrice]]]:
    """
    Process the price ticker response and convert it to appropriate objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        Single or list of TickerPrice objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid price ticker response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        
        # Handle single result
        if isinstance(result, dict):
            return TickerPrice.from_api_response(result)
        
        # Handle list of results
        elif isinstance(result, list):
            return [TickerPrice.from_api_response(item) for item in result]
        
        else:
            logger.error(f"Unexpected response format: {type(result)}")
            return None
        
    except Exception as e:
        logger.error(f"Error processing price ticker response: {str(e)}")
        return None