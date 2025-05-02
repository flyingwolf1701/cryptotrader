"""
Binance WebSocket API Aggregate Trades Request

This module provides functionality to retrieve aggregate trades for a trading symbol.
It follows the Binance WebSocket API specifications for the 'trades.aggregate' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websockets.baseOperations import (
    BinanceWebSocketConnection,
    SecurityType,
)
from cryptotrader.services.binance.models import AggTrade

logger = get_logger(__name__)


async def get_aggregate_trades_ws(
    connection: BinanceWebSocketConnection,
    symbol: str,
    from_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
    limit: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
) -> str:
    """
    Retrieve aggregate trades for a trading symbol.

    An aggregate trade represents one or more individual trades executed
    at the same time, from the same taker order, with the same price.

    Endpoint: trades.aggregate
    Weight: 1
    Security Type: NONE (Public endpoint)
    Data Source: Database

    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        from_id: Aggregate trade ID to fetch from (optional)
        start_time: Start time in milliseconds (optional)
        end_time: End time in milliseconds (optional)
        limit: Number of trades to return (default 500, max 1000)
        callback: Optional callback function for the response

    Returns:
        Message ID of the request

    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing or invalid
        ValueError: If both from_id and start_time/end_time are specified
    """
    if not symbol:
        raise ValueError("Symbol parameter is required")

    # Validate parameters
    if from_id is not None:
        if not isinstance(from_id, int) or from_id < 0:
            raise ValueError("from_id must be a non-negative integer")

        # fromId cannot be used with startTime/endTime
        if start_time is not None or end_time is not None:
            raise ValueError(
                "from_id cannot be used together with start_time and end_time"
            )

    if start_time is not None and not isinstance(start_time, int):
        raise ValueError("start_time must be an integer (milliseconds)")

    if end_time is not None and not isinstance(end_time, int):
        raise ValueError("end_time must be an integer (milliseconds)")

    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("Limit must be a positive integer")
        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

    # Prepare request parameters
    params = {"symbol": symbol}

    if from_id is not None:
        params["fromId"] = from_id

    if start_time is not None:
        params["startTime"] = start_time

    if end_time is not None:
        params["endTime"] = end_time

    if limit is not None:
        params["limit"] = limit

    # Send the request
    msg_id = await connection.send(
        method="trades.aggregate", params=params, security_type=SecurityType.NONE
    )

    logger.debug(f"Sent aggregate trades request for {symbol} with ID: {msg_id}")
    return msg_id


async def process_aggregate_trades_response(
    response: Dict[str, Any],
) -> Optional[List[AggTrade]]:
    """
    Process the aggregate trades response and convert it to a list of AggTrade objects.

    Args:
        response: WebSocket response data

    Returns:
        List of AggTrade objects if successful, None otherwise
    """
    if not response or "result" not in response:
        logger.error("Invalid aggregate trades response: missing 'result' field")
        return None

    try:
        result = response["result"]
        return [AggTrade.from_api_response(trade) for trade in result]
    except Exception as e:
        logger.error(f"Error processing aggregate trades response: {str(e)}")
        return None
