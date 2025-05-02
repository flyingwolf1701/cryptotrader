"""
Binance WebSocket API Symbol Order Book Ticker Request

This module provides functionality to retrieve the current best price and quantity on the order book.
It follows the Binance WebSocket API specifications for the 'ticker.book' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable, Union
from dataclasses import dataclass

from config import get_logger
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType

logger = get_logger(__name__)

@dataclass
class BookTicker:
    """Data structure for order book ticker"""
    symbol: str
    bidPrice: float
    bidQty: float
    askPrice: float
    askQty: float
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> 'BookTicker':
        return cls(
            symbol=response['symbol'],
            bidPrice=float(response['bidPrice']),
            bidQty=float(response['bidQty']),
            askPrice=float(response['askPrice']),
            askQty=float(response['askQty'])
        )

async def get_book_ticker(
    connection: BinanceWebSocketConnection,
    symbol: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve the current best price and quantity on the order book.
    
    Gets the current best bid and ask price and quantity for the specified symbol(s).
    For real-time order book ticker updates, consider using WebSocket Streams instead.
    
    Endpoint: ticker.book
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
        method="ticker.book",
        params=params,
        security_type=SecurityType.NONE
    )
    
    symbol_info = symbol or (f"{len(symbols)} symbols" if symbols else "all symbols")
    logger.debug(f"Sent order book ticker request for {symbol_info} with ID: {msg_id}")
    return msg_id

async def process_book_ticker_response(
    response: Dict[str, Any]
) -> Optional[Union[BookTicker, List[BookTicker]]]:
    """
    Process the order book ticker response and convert it to appropriate objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        Single or list of BookTicker objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid order book ticker response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        
        # Handle single result
        if isinstance(result, dict):
            return BookTicker.from_api_response(result)
        
        # Handle list of results
        elif isinstance(result, list):
            return [BookTicker.from_api_response(item) for item in result]
        
        else:
            logger.error(f"Unexpected response format: {type(result)}")
            return None
        
    except Exception as e:
        logger.error(f"Error processing order book ticker response: {str(e)}")
        return None
