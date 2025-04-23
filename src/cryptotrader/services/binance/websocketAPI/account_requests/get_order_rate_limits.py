"""
Binance WebSocket API Order Rate Limits Request

This module provides functionality to retrieve order rate limits via the Binance WebSocket API.
It follows the Binance WebSocket API specifications for the 'account.rateLimits.orders' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models.order_models import RateLimitInfo

logger = get_logger(__name__)

async def get_order_rate_limits(
    connection: BinanceWebSocketConnection,
    recv_window: Optional[int] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Retrieve current order rate limits.
    
    Gets the current order rate limits for all time intervals.
    
    Endpoint: account.rateLimits.orders
    Weight: 20
    Security Type: USER_DATA (Requires API key and signature)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        recv_window: Maximum time in milliseconds request is valid for (optional)
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If recv_window exceeds 60000
    """
    # Validate parameters
    if recv_window is not None:
        if not isinstance(recv_window, int) or recv_window <= 0:
            raise ValueError("recv_window must be a positive integer")
        if recv_window > 60000:
            raise ValueError("recv_window cannot exceed 60000")
    
    # Prepare request parameters
    params = {}
    if recv_window is not None:
        params["recvWindow"] = recv_window
    
    # Send the request with USER_DATA security type
    # This requires API key and signature which will be added automatically
    msg_id = await connection.send(
        method="account.rateLimits.orders",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent order rate limits request with ID: {msg_id}")
    return msg_id

async def process_order_rate_limits_response(response: Dict[str, Any]) -> Optional[List[RateLimitInfo]]:
    """
    Process the order rate limits response.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of RateLimitInfo objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid order rate limits response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [RateLimitInfo.from_api_response(limit) for limit in result]
    except Exception as e:
        logger.error(f"Error processing order rate limits response: {str(e)}")
        return None