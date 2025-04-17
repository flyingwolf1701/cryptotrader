"""
Binance WebSocket Base Operations

This module provides the foundational infrastructure for WebSocket connections to Binance.
It handles:
- WebSocket connection establishment and management
- Message serialization and deserialization
- Authentication and signature generation
- Ping/pong keep-alive mechanism
- Reconnection logic and error handling
- Rate limiting (shared with REST API)
"""

import json
import time
import hmac
import hashlib
import asyncio
import uuid
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable

import websockets
from websockets.exceptions import ConnectionClosed

from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.binance.restAPI.base_operations import RateLimiter
from cryptotrader.services.binance.models.base_models import (
    RateLimit, RateLimitType, RateLimitInterval
)

logger = get_logger(__name__)

class BinanceWebSocketConnection:
    """
    Manages a WebSocket connection to the Binance API.
    
    Handles connection lifecycle, authentication, message handling,
    and reconnection logic.
    """
    
    def __init__(self, 
                on_message: Callable[[Dict[str, Any]], None],
                on_error: Optional[Callable[[Exception], None]] = None,
                on_reconnect: Optional[Callable[[], None]] = None,
                on_close: Optional[Callable[[], None]] = None,
                ping_interval: int = 180,  # 3 minutes in seconds
                pong_timeout: int = 10,    # 10 seconds timeout for pong
                reconnect_attempts: int = 5,
                base_url: str = "wss://ws-api.binance.us:443"):
        """
        Initialize a new WebSocket connection.
        
        Args:
            on_message: Callback function for received messages
            on_error: Callback function for errors
            on_reconnect: Callback function when reconnection happens
            on_close: Callback function when connection closes
            ping_interval: How often to send ping frames (seconds)
            pong_timeout: How long to wait for pong response (seconds)
            reconnect_attempts: Maximum number of reconnection attempts
            base_url: Base URL for WebSocket API
        """
        self.on_message = on_message
        self.on_error = on_error
        self.on_reconnect = on_reconnect
        self.on_close = on_close
        self.ping_interval = ping_interval
        self.pong_timeout = pong_timeout
        self.reconnect_attempts = reconnect_attempts
        self.base_url = base_url
        
        # Connection state
        self.websocket = None
        self.is_connected = False
        self.is_closing = False
        self.reconnect_count = 0
        self.last_message_time = 0
        
        # Tasks
        self.ping_task = None
        self.receive_task = None
        
        # Rate limiter (shared with REST API)
        self.rate_limiter = RateLimiter()
        
        # Message ID counter
        self.message_id = 0
    
    async def connect(self) -> bool:
        """
        Establish WebSocket connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            return True
            
        try:
            # Create connection with ping/pong control
            self.websocket = await websockets.connect(
                self.base_url + "/ws-api/v3",
                ping_interval=None,  # We'll handle pings manually
                max_size=None,       # No message size limit
                close_timeout=5,     # 5 seconds to close gracefully
                extra_headers=None   # No extra headers needed for initial connection
            )
            
            # Connection established
            self.is_connected = True
            self.reconnect_count = 0
            self.last_message_time = time.time()
            
            # Start tasks
            self.ping_task = asyncio.create_task(self._ping_loop())
            self.receive_task = asyncio.create_task(self._receive_loop())
            
            logger.info("WebSocket connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            if self.on_error:
                self.on_error(e)
            return False
    
    async def _ping_loop(self):
        """Send periodic pings to keep connection alive."""
        while self.is_connected and not self.is_closing:
            try:
                # Wait for ping interval
                await asyncio.sleep(self.ping_interval)
                
                # Send ping message
                if self.is_connected:
                    ping_id = str(uuid.uuid4())
                    ping_message = {
                        "id": ping_id,
                        "method": "ping"
                    }
                    await self.websocket.send(json.dumps(ping_message))
                    logger.debug(f"Sent ping message with ID: {ping_id}")
                    
                    # Wait for pong response (handled in _receive_loop)
                    # If no activity for pong_timeout, we'll reconnect
                    wait_until = time.time() + self.pong_timeout
                    while time.time() < wait_until and time.time() - self.last_message_time > self.pong_timeout:
                        if not self.is_connected:
                            break
                        await asyncio.sleep(0.5)
                        
                    # Check if we've received any message (including pong)
                    if self.is_connected and time.time() - self.last_message_time > self.pong_timeout:
                        logger.warning("No pong response received, reconnecting...")
                        await self._reconnect()
                        
            except Exception as e:
                logger.error(f"Error in ping loop: {str(e)}")
                if not self.is_closing:
                    await self._reconnect()
    
    async def _receive_loop(self):
        """Receive and process incoming WebSocket messages."""
        while self.is_connected and not self.is_closing:
            try:
                # Wait for a message
                message = await self.websocket.recv()
                self.last_message_time = time.time()
                
                # Parse the message
                if message:
                    parsed_message = json.loads(message)
                    
                    # Update rate limits if included
                    if 'rateLimits' in parsed_message:
                        self._update_rate_limits(parsed_message['rateLimits'])
                    
                    # Check for errors
                    if 'error' in parsed_message:
                        self._handle_error(parsed_message)
                    
                    # Process the message with the callback
                    if self.on_message:
                        self.on_message(parsed_message)
                        
            except websockets.exceptions.ConnectionClosed as e:
                if not self.is_closing:
                    logger.warning(f"WebSocket connection closed unexpectedly: {str(e)}")
                    await self._reconnect()
                break
                
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                if self.on_error:
                    self.on_error(e)
                if not self.is_closing:
                    await self._reconnect()
    
    async def _reconnect(self):
        """Handle reconnection after connection loss."""
        if self.is_closing or not self.is_connected:
            return
            
        # Mark as disconnected
        self.is_connected = False
        
        # Cancel existing tasks
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None
            
        if self.receive_task:
            self.receive_task.cancel()
            self.receive_task = None
        
        # Close existing connection if any
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
            self.websocket = None
        
        # Check if we've exceeded reconnection attempts
        if self.reconnect_count >= self.reconnect_attempts:
            logger.error(f"Failed to reconnect after {self.reconnect_attempts} attempts")
            if self.on_close:
                self.on_close()
            return
            
        # Increment reconnection counter
        self.reconnect_count += 1
        
        # Exponential backoff
        wait_time = min(30, 0.5 * (2 ** self.reconnect_count))
        logger.warning(f"Reconnecting in {wait_time:.2f} seconds (attempt {self.reconnect_count}/{self.reconnect_attempts})")
        
        # Wait before reconnecting
        await asyncio.sleep(wait_time)
        
        # Attempt to reconnect
        success = await self.connect()
        
        if success and self.on_reconnect:
            self.on_reconnect()
    
    def _update_rate_limits(self, rate_limits: List[Dict[str, Any]]):
        """
        Update rate limit counters from WebSocket response.
        
        Args:
            rate_limits: Rate limit information from response
        """
        for limit in rate_limits:
            limit_type = limit.get('rateLimitType')
            interval = limit.get('interval')
            interval_num = limit.get('intervalNum')
            count = limit.get('count')
            
            if limit_type and interval and interval_num is not None and count is not None:
                key = f"{limit_type}_{interval}_{interval_num}"
                self.rate_limiter.usage[key] = count
    
    def _handle_error(self, message: Dict[str, Any]):
        """
        Handle error responses from WebSocket.
        
        Args:
            message: Error message from WebSocket
        """
        if 'error' in message:
            error = message['error']
            code = error.get('code', 0)
            msg = error.get('msg', 'Unknown error')
            
            logger.error(f"WebSocket error (code {code}): {msg}")
            
            # Handle specific error codes
            if code == -1003:  # Rate limit exceeded
                if 'data' in error and 'retryAfter' in error['data']:
                    retry_after = error['data']['retryAfter']
                    logger.warning(f"Rate limit exceeded, retry after: {retry_after}")
            
            # Notify error callback
            if self.on_error:
                self.on_error(Exception(f"WebSocket error (code {code}): {msg}"))
    
    async def send(self, method: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a message to the WebSocket server.
        
        Args:
            method: API method to call
            params: Parameters for the method
            
        Returns:
            Message ID that can be used to match the response
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")
            
        # Generate message ID
        msg_id = str(self.message_id)
        self.message_id += 1
        
        # Create message
        message = {
            "id": msg_id,
            "method": method
        }
        
        if params:
            message["params"] = params
            
        # Send the message
        await self.websocket.send(json.dumps(message))
        return msg_id
    
    async def send_signed(self, method: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Send a signed message to the WebSocket server.
        
        Args:
            method: API method to call
            params: Parameters for the method
            
        Returns:
            Message ID that can be used to match the response
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")
            
        # Generate message ID
        msg_id = str(self.message_id)
        self.message_id += 1
        
        # Create params if not provided
        if params is None:
            params = {}
            
        # Add timestamp and API key
        params['timestamp'] = int(time.time() * 1000)
        params['apiKey'] = Secrets.BINANCE_API_KEY
        
        # Generate signature
        query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            Secrets.BINANCE_API_SECRET.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Add signature to params
        params['signature'] = signature
        
        # Create message
        message = {
            "id": msg_id,
            "method": method,
            "params": params
        }
            
        # Send the message
        await self.websocket.send(json.dumps(message))
        return msg_id
    
    async def close(self):
        """Close the WebSocket connection."""
        if not self.is_connected:
            return
            
        self.is_closing = True
        self.is_connected = False
        
        # Cancel tasks
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None
            
        if self.receive_task:
            self.receive_task.cancel()
            self.receive_task = None
        
        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            
        # Notify closure
        if self.on_close:
            self.on_close()
            
        logger.info("WebSocket connection closed")


class BinanceWebSocketClient:
    """
    Base class for Binance WebSocket API clients.
    
    Provides common functionality for specific WebSocket client implementations.
    """
    
    def __init__(self):
        """Initialize the WebSocket client."""
        self.connections = {}
        self.callbacks = {}
        self.response_handlers = {}
    
    async def _create_connection(self, 
                               on_message: Callable[[Dict[str, Any]], None],
                               on_error: Optional[Callable[[Exception], None]] = None,
                               on_reconnect: Optional[Callable[[], None]] = None,
                               on_close: Optional[Callable[[], None]] = None) -> BinanceWebSocketConnection:
        """
        Create a new WebSocket connection.
        
        Args:
            on_message: Callback for handling messages
            on_error: Callback for handling errors
            on_reconnect: Callback for handling reconnection
            on_close: Callback for handling connection closure
            
        Returns:
            BinanceWebSocketConnection instance
        """
        connection = BinanceWebSocketConnection(
            on_message=on_message,
            on_error=on_error,
            on_reconnect=on_reconnect,
            on_close=on_close
        )
        
        await connection.connect()
        return connection
    
    async def _handle_message(self, connection_id: str, message: Dict[str, Any]):
        """
        Handle received WebSocket message.
        
        Args:
            connection_id: ID of the connection
            message: Received message
        """
        # Check for message ID
        msg_id = message.get('id')
        
        # If we have a handler for this message ID, call it
        if msg_id and msg_id in self.response_handlers:
            handler = self.response_handlers[msg_id]
            handler(message)
            # One-time handler, remove after use
            del self.response_handlers[msg_id]
            return
            
        # Otherwise, pass to the general callback for this connection
        if connection_id in self.callbacks:
            callback = self.callbacks[connection_id]
            callback(message)
    
    async def _handle_error(self, connection_id: str, error: Exception):
        """
        Handle WebSocket error.
        
        Args:
            connection_id: ID of the connection
            error: Exception that occurred
        """
        logger.error(f"WebSocket error on connection {connection_id}: {str(error)}")
    
    async def _handle_reconnect(self, connection_id: str):
        """
        Handle WebSocket reconnection.
        
        Args:
            connection_id: ID of the connection
        """
        logger.info(f"WebSocket connection {connection_id} reconnected")
    
    async def _handle_close(self, connection_id: str):
        """
        Handle WebSocket closure.
        
        Args:
            connection_id: ID of the connection
        """
        logger.info(f"WebSocket connection {connection_id} closed")
        
        # Remove the connection and its callback
        if connection_id in self.connections:
            del self.connections[connection_id]
            
        if connection_id in self.callbacks:
            del self.callbacks[connection_id]
    
    async def close_all_connections(self):
        """Close all active WebSocket connections."""
        for connection_id, connection in list(self.connections.items()):
            await connection.close()
            
        self.connections = {}
        self.callbacks = {}
        self.response_handlers = {}