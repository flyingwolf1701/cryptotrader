"""
Binance WebSocket API Rolling Window Price Request

This module provides functionality to retrieve rolling window price change statistics.
It follows the Binance WebSocket API specifications for the 'ticker' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

from config import get_logger
from services.binance.websockets.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import RollingWindowStats, RollingWindowStatsMini

logger = get_logger(__name__)

async def get_rolling_window_stats(
    connection: BinanceWebSocketConnection,
    symbol: Optional[str] = None,
    symbols: Optional[List[str]] = None,
    window_size: Optional[str] = "1d",
    ticker_type: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve rolling window price change statistics.
    
    Gets price statistics for a custom rolling window. Similar to 24hr ticker,
    but statistics are computed on demand using an arbitrary window.
    
    Endpoint: ticker
    Weight: Adjusted based on parameters:
            1-50 symbols: 2 per symbol
            51-100 symbols: 100
    Security Type: NONE (Public endpoint)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT') (required if symbols not provided)
        symbols: List of symbols (required if symbol not provided)
        window_size: Window size (default '1d')
                     Options: minutes (1m-59m), hours (1h-23h), days (1d-7d)
        ticker_type: Ticker type: 'FULL' (default) or 'MINI'
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If parameters are invalid or neither symbol nor symbols is provided
    """
    # Validate parameters
    if not symbol and not symbols:
        raise ValueError("Either 'symbol' or 'symbols' parameter must be provided")
    
    if symbol and symbols:
        raise ValueError("Cannot use both 'symbol' and 'symbols' parameters together")
    
    if symbols and len(symbols) > 100:
        raise ValueError("Maximum number of symbols is 100")
    
    if ticker_type and ticker_type not in ['FULL', 'MINI']:
        raise ValueError("ticker_type must be either 'FULL' or 'MINI'")
    
    # Validate window_size format
    valid_window_sizes = (
        # Minutes
        [f"{i}m" for i in range(1, 60)] + 
        # Hours
        [f"{i}h" for i in range(1, 24)] + 
        # Days
        [f"{i}d" for i in range(1, 8)]
    )
    
    if window_size not in valid_window_sizes:
        raise ValueError(
            f"Invalid window_size: {window_size}. Must be one of: "
            "1m-59m (minutes), 1h-23h (hours), 1d-7d (days)"
        )
    
    # Prepare request parameters
    params = {"windowSize": window_size}
    
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
        method="ticker",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent rolling window ticker request with window {window_size}, ID: {msg_id}")
    return msg_id

async def process_rolling_window_response(
    response: Dict[str, Any], 
    ticker_type: Optional[str] = 'FULL'
) -> Optional[Union[RollingWindowStats, RollingWindowStatsMini, List[Union[RollingWindowStats, RollingWindowStatsMini]]]]:
    """
    Process the rolling window response and convert it to appropriate objects.
    
    Args:
        response: WebSocket response data
        ticker_type: Ticker type: 'FULL' (default) or 'MINI'
        
    Returns:
        Single or list of RollingWindowStats/RollingWindowStatsMini objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid rolling window response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        
        # Handle single result
        if isinstance(result, dict):
            if ticker_type == 'MINI' or ('priceChangePercent' not in result):
                return RollingWindowStatsMini.from_api_response(result)
            else:
                return RollingWindowStats.from_api_response(result)
        
        # Handle list of results
        elif isinstance(result, list):
            ticker_list = []
            for item in result:
                if ticker_type == 'MINI' or ('priceChangePercent' not in item):
                    ticker_list.append(RollingWindowStatsMini.from_api_response(item))
                else:
                    ticker_list.append(RollingWindowStats.from_api_response(item))
            return ticker_list
        
        else:
            logger.error(f"Unexpected response format: {type(result)}")
            return None
        
    except Exception as e:
        logger.error(f"Error processing rolling window response: {str(e)}")
        return None