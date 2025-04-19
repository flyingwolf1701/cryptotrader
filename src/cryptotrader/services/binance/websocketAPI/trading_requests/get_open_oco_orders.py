"""
Binance WebSocket API Get Open OCO Orders Request

This module provides functionality to query execution status of all open OCO orders.
It follows the Binance WebSocket API specifications for the 'openOrderLists.status' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import OcoOrderResponse

logger = get_logger(__name__)

async def get_open_oco_orders(
    connection: BinanceWebSocketConnection,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Query execution status of all open OCO orders.
    
    Endpoint: openOrderLists.status
    Weight: 3
    Security Type: USER_DATA (Requires API key and signature)
    
    Args:
        connection: Active WebSocket connection
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
    """
    # Prepare request parameters
    params = {}
    
    # Send the request with USER_DATA security type (requires API key and signature)
    msg_id = await connection.send(
        method="openOrderLists.status",
        params=params,
        security_type=SecurityType.USER_DATA
    )
    
    logger.debug(f"Sent get open OCO orders request with ID: {msg_id}")
    return msg_id

async def process_open_oco_orders_response(response: Dict[str, Any]) -> Optional[List[OcoOrderResponse]]:
    """
    Process the open OCO orders response and convert it to a list of OcoOrderResponse objects.
    
    Args:
        response: WebSocket response data
        
    Returns:
        List of OcoOrderResponse objects if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid open OCO orders response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        return [OcoOrderResponse.from_api_response(oco) for oco in result]
    except Exception as e:
        logger.error(f"Error processing open OCO orders response: {str(e)}")
        return None