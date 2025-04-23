"""
Binance WebSocket API 24hr Ticker Price Request

This module provides functionality to retrieve 24-hour price change statistics for a trading symbol.
It follows the Binance WebSocket API specifications for the 'ticker.24hr' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import PriceStats, PriceStatsMini

logger = get_logger(__name__)

async def get_24h_ticker(
    connection: BinanceWebSocketConnection,
    symbol: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    ticker_type: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve 24-hour price change statistics.
    
    Gets 24-hour rolling window price change statistics for a symbol or symbols.
    For real-time continuous ticker updates, consider using WebSocket Streams instead.
    
    Endpoint: ticker.24hr
    Weight: Adjusted based on parameters:
            1-20 symbols: 1
            21-100 symbols: 20
            101 or more symbols: 40
            all symbols: 40
    Security Type: NONE (Public endpoint)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT') (optional)
        symbols: List of symbols (optional)
        ticker_type: Ticker type: 'FULL' (default) or 'MINI'
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
    
    if ticker_type and ticker_type not in ['FULL', 'MINI']:
        raise ValueError("ticker_type must be either 'FULL' or 'MINI'")
    
    # Prepare request parameters
    params = {}
    
    if symbol:
        params["symbol"] = symbol
    
    if symbols:
        if not isinstance(symbols, list):
            raise ValueError("symbols must be a list of strings")
        params["symbols"] = symbols
    
    if ticker_type:
        params["type"] = ticker_type
    
    # Send the request
    msg_id = await connection.send(
        method="ticker.24hr",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent 24h ticker request with ID: {msg_id}")
    return msg_id

async def process_24h_ticker_response(
    response: Dict[str, Any], 
    ticker_type: Optional[str] = 'FULL'
) -> Optional[Union[PriceStats, PriceStatsMini, List[Union[PriceStats, PriceStatsMini]]]]:
    """
    Process the 24h ticker response and convert it to appropriate objects.
    
    Args:
        response: WebSocket response data
        ticker_type: Ticker type: 'FULL' (default) or 'MINI'
        
    Returns:
        Single or list of PriceStats/PriceStatsMini objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid 24h ticker response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        
        # Handle single result
        if isinstance(result, dict):
            if ticker_type == 'MINI' or ('priceChangePercent' not in result):
                return PriceStatsMini.from_api_response(result)
            else:
                return PriceStats.from_api_response(result)
        
        # Handle list of results
        elif isinstance(result, list):
            ticker_list = []
            for item in result:
                if ticker_type == 'MINI' or ('priceChangePercent' not in item):
                    ticker_list.append(PriceStatsMini.from_api_response(item))
                else:
                    ticker_list.append(PriceStats.from_api_response(item))
            return ticker_list
        
        else:
            logger.error(f"Unexpected response format: {type(result)}")
            return None
        
    except Exception as e:
        logger.error(f"Error processing 24h ticker response: {str(e)}")
        return None