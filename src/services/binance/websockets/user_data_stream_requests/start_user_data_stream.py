"""
Binance WebSocket API Start User Data Stream Request

This module provides functionality to start a new user data stream.
It follows the Binance WebSocket API specifications for the 'userDataStream.start' endpoint.
"""

from typing import Dict, Optional, Any, Callable, Awaitable

from config import get_logger, Secrets
from services.binance.websockets.baseOperations import BinanceWebSocketConnection, SecurityType

logger = get_logger(__name__)

async def start_user_data_stream(
    connection: BinanceWebSocketConnection,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Start a new user data stream.
    
    Initiates a user data stream to receive real-time account updates.
    Note that the stream will close in 60 minutes unless ping_user_data_stream 
    requests are sent regularly.
    
    Endpoint: userDataStream.start
    Weight: 1
    Security Type: USER_STREAM (Requires API key only)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    # No additional parameters needed as the API key is added automatically
    # for USER_STREAM security type
    params = {}
    
    # Send the request with USER_STREAM security type
    # This only requires API key which will be added automatically
    msg_id = await connection.send(
        method="userDataStream.start",
        params=params,
        security_type=SecurityType.USER_STREAM
    )
    
    logger.debug(f"Sent start user data stream request with ID: {msg_id}")
    return msg_id

async def process_start_user_data_stream_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Process the start user data stream response and extract the listen key.
    
    Args:
        response: WebSocket response data
        
    Returns:
        Listen key if successful, None otherwise
    """
    if not response or 'result' not in response:
        logger.error("Invalid start user data stream response: missing 'result' field")
        return None
    
    try:
        result = response['result']
        listen_key = result.get('listenKey')
        
        if not listen_key:
            logger.error("No listenKey found in the response")
            return None
        
        logger.info(f"Successfully obtained listenKey: {listen_key[:10]}...")
        return listen_key
    except Exception as e:
        logger.error(f"Error processing start user data stream response: {str(e)}")
        return None