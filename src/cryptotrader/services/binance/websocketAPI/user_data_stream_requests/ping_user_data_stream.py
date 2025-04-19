"""
Binance WebSocket API Ping User Data Stream Request

This module provides functionality to ping a user data stream to keep it alive.
It follows the Binance WebSocket API specifications for the 'userDataStream.ping' endpoint.
"""

from typing import Dict, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType

logger = get_logger(__name__)

async def ping_user_data_stream(
    connection: BinanceWebSocketConnection,
    listen_key: str,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Ping a user data stream to keep it alive.
    
    User data streams close automatically after 60 minutes, even if you're 
    listening to them on WebSocket Streams. In order to keep the stream open, 
    you have to regularly send pings using this request.
    
    It is recommended to send a ping once every 30 minutes.
    
    Endpoint: userDataStream.ping
    Weight: 1
    Security Type: USER_STREAM (Requires API key only)
    Data Source: Memory
    
    Args:
        connection: Active WebSocket connection
        listen_key: Listen key for the user data stream to ping
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    if not listen_key:
        raise ValueError("listen_key parameter is required")
    
    # Prepare request parameters
    params = {
        "listenKey": listen_key
    }
    
    # Send the request with USER_STREAM security type
    # This only requires API key which will be added automatically
    msg_id = await connection.send(
        method="userDataStream.ping",
        params=params,
        security_type=SecurityType.USER_STREAM
    )
    
    logger.debug(f"Sent ping user data stream request for listen key {listen_key[:10]}... with ID: {msg_id}")
    return msg_id

async def process_ping_user_data_stream_response(response: Dict[str, Any]) -> bool:
    """
    Process the ping user data stream response.
    
    Args:
        response: WebSocket response data
        
    Returns:
        True if successful, False otherwise
    """
    if not response:
        logger.error("Invalid ping user data stream response: empty response")
        return False
    
    try:
        # Check if this is a success response (status 200)
        if 'status' in response and response['status'] == 200:
            logger.debug("Successfully pinged user data stream")
            return True
        
        # Check if this is an error response
        if 'error' in response:
            error = response.get('error', {})
            error_code = error.get('code', 0)
            error_msg = error.get('msg', 'Unknown error')
            logger.error(f"Ping user data stream failed with code {error_code}: {error_msg}")
        
        return False
    except Exception as e:
        logger.error(f"Error processing ping user data stream response: {str(e)}")
        return False