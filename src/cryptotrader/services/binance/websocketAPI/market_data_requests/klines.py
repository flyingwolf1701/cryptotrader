"""
Binance WebSocket API Klines Request

This module provides functionality to retrieve kline/candlestick data for a trading symbol.
It follows the Binance WebSocket API specifications for the 'klines' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import Candle, KlineInterval

logger = get_logger(__name__)

async def get_klines(
    connection: BinanceWebSocketConnection,
    symbol: str,
    interval: str,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve kline/candlestick data for a trading symbol.
    
    Gets candlestick bars for the specified symbol. Klines are uniquely 
    identified by their open and close time. For real-time kline updates,
    consider using WebSocket Streams instead.
    
    Endpoint: klines
    Weight: 1
    Security Type: NONE (Public endpoint)
    Data Source: Database
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        interval: Kline interval (e.g., '1m', '1h', '1d')
                  Options: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        limit: Number of candles to return (default 500, max 1000)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
        
    Notes:
        - If start_time and end_time are not specified, the most recent klines are returned
        - Interval is case-sensitive
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    # Validate interval parameter
    try:
        # Verify interval is a valid KlineInterval value
        valid_interval = False
        for interval_enum in KlineInterval:
            if interval == interval_enum.value:
                valid_interval = True
                break
        
        if not valid_interval:
            raise ValueError(f"Invalid interval: {interval}. Must be one of: " + 
                            ", ".join([i.value for i in KlineInterval]))
    except Exception as e:
        raise ValueError(f"Invalid interval parameter: {str(e)}")
    
    # Validate optional parameters
    if start_time is not None and not isinstance(start_time, int):
        raise ValueError("start_time must be an integer timestamp in milliseconds")
    
    if end_time is not None and not isinstance(end_time, int):
        raise ValueError("end_time must be an integer timestamp in milliseconds")
    
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer")
        if limit > 1000:
            raise ValueError("limit cannot exceed 1000")
    
    # Prepare request parameters
    params = {
        "symbol": symbol,
        "interval": interval
    }
    
    if start_time is not None:
        params["startTime"] = start_time
    
    if end_time is not None:
        params["endTime"] = end_time
    
    if limit is not None:
        params["limit"] = limit
    
    # Send the request
    msg_id = await connection.send(
        method="klines",
        params=params,
        security_type=SecurityType.NONE
    )
    
    logger.debug(f"Sent klines request for {symbol} with interval {interval}, ID: {msg_id}")
    return msg_id

async def process_klines_response(response: Dict[str, Any]) -> Optional[List[Candle]]:
    """
    Process the klines response and convert it to a list of Candle objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of Candle objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid klines response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        candles = []
        
        for kline_data in result:
            if len(kline_data) < 12:
                logger.warning(f"Skipping incomplete kline data: {kline_data}")
                continue
                
            candle = Candle(
                timestamp=kline_data[0],          # Open time
                open_price=float(kline_data[1]),  # Open price
                high_price=float(kline_data[2]),  # High price
                low_price=float(kline_data[3]),   # Low price
                close_price=float(kline_data[4]), # Close price
                volume=float(kline_data[5]),      # Volume
                quote_volume=float(kline_data[7]) # Quote asset volume
            )
            candles.append(candle)
            
        return candles
    except Exception as e:
        logger.error(f"Error processing klines response: {str(e)}")
        return None