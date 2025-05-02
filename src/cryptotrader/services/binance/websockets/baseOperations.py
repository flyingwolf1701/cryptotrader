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
- IP bans and rate limit violations handling
"""

import json
import time
import hmac
import hashlib
import asyncio
import uuid
from typing import Dict, List, Optional, Any, Union, Callable, Awaitable
from enum import Enum, auto
from urllib.parse import parse_qs, urlparse

import websockets
from websockets.exceptions import ConnectionClosed

from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.binance.restAPI.baseOperations import RateLimiter
from cryptotrader.services.binance.models import (
    RateLimit,
    RateLimitType,
    RateLimitInterval,
)

logger = get_logger(__name__)


class SecurityType(str, Enum):
    """Security types for Binance API endpoints"""

    NONE = "NONE"  # Public market data
    TRADE = "TRADE"  # Trading on the exchange (requires API key and signature)
    USER_DATA = (
        "USER_DATA"  # Private account information (requires API key and signature)
    )
    USER_STREAM = "USER_STREAM"  # Managing user data stream (requires API key only)
    MARKET_DATA = "MARKET_DATA"  # Historical market data (requires API key only)


class BinanceWebSocketConnection:
    """
    Manages a WebSocket connection to the Binance API.

    Handles connection lifecycle, authentication, message handling,
    reconnection logic, and rate limiting.
    """

    def __init__(
        self,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]],
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
        on_reconnect: Optional[Callable[[], Awaitable[None]]] = None,
        on_close: Optional[Callable[[], Awaitable[None]]] = None,
        ping_interval: int = 180,  # 3 minutes in seconds
        pong_timeout: int = 10,  # 10 seconds timeout for pong
        reconnect_attempts: int = 5,
        base_url: str = "wss://ws-api.binance.us:443",
        return_rate_limits: bool = True,
    ):
        """
        Initialize a new WebSocket connection to the Binance WebSocket API.

        The Binance WebSocket API allows for lower-latency communications compared
        to REST API endpoints. This connection handles authentication, rate limiting,
        reconnection logic, and message handling.

        Args:
            on_message: Callback function for received messages
            on_error: Callback function for errors
            on_reconnect: Callback function when reconnection happens
            on_close: Callback function when connection closes
            ping_interval: How often to send ping frames (seconds), default 180s (3 minutes)
                           Server expects pong responses within 10 minutes
            pong_timeout: How long to wait for pong response (seconds), default 10s
            reconnect_attempts: Maximum number of reconnection attempts
            base_url: Base URL for WebSocket API, default is wss://ws-api.binance.us:443
                      Alternative port 9443 is also available if needed
            return_rate_limits: Whether to return rate limits in responses, default True
        """
        self.on_message = on_message
        self.on_error = on_error
        self.on_reconnect = on_reconnect
        self.on_close = on_close
        self.ping_interval = ping_interval
        self.pong_timeout = pong_timeout
        self.reconnect_attempts = reconnect_attempts
        self.base_url = base_url
        self.return_rate_limits = return_rate_limits

        # Connection state
        self.websocket = None
        self.is_connected = False
        self.is_closing = False
        self.reconnect_count = 0
        self.last_message_time = 0
        self.connection_start_time = None

        # Tasks
        self.ping_task = None
        self.receive_task = None
        self.connection_monitoring_task = None

        # Rate limiting state
        self.rate_limiter = RateLimiter()
        self.ip_banned_until = None
        self.retry_after = None

        # Message ID counter
        self.message_id = 0

    async def connect(self) -> bool:
        """
        Establish WebSocket connection to Binance WebSocket API.

        This method connects to the Binance WebSocket API endpoint and sets up
        the necessary tasks for handling messages, ping/pong keep-alive, and
        connection monitoring. The API connection is valid for 24 hours max.

        Rate limit: 1 weight per connection
        Method: None (connection establishment)

        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            return True

        # Check if we're banned
        if self.ip_banned_until and time.time() * 1000 < self.ip_banned_until:
            ban_remaining_secs = (self.ip_banned_until - time.time() * 1000) / 1000
            logger.warning(
                f"IP banned, cannot connect for {ban_remaining_secs:.1f} more seconds"
            )
            if self.on_error:
                await self.on_error(
                    Exception(f"IP banned until {self.ip_banned_until}")
                )
            return False

        # Reset ban state if we're attempting a connection
        self.ip_banned_until = None
        self.retry_after = None

        try:
            # Build URL with rate limit parameter if needed
            url = self.base_url + "/ws-api/v3"

            # Check for returnRateLimits parameter in URL or from instance
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)

            # If there's already a query string, append our parameter
            if parsed_url.query:
                if (
                    "returnRateLimits" not in query_params
                    and not self.return_rate_limits
                ):
                    url += "&returnRateLimits=false"
            else:
                # No existing query parameters
                if not self.return_rate_limits:
                    url += "?returnRateLimits=false"

            # Create connection with ping/pong control
            self.websocket = await websockets.connect(
                url,
                ping_interval=None,  # We'll handle pings manually
                max_size=None,  # No message size limit
                close_timeout=5,  # 5 seconds to close gracefully
            )

            # Connection established
            self.is_connected = True
            self.reconnect_count = 0
            self.last_message_time = time.time()
            self.connection_start_time = time.time()  # Track connection start time

            # Start tasks
            self.ping_task = asyncio.create_task(self._pingLoop())
            self.receive_task = asyncio.create_task(self._receiveLoop())
            self.connection_monitoring_task = asyncio.create_task(
                self._monitorConnectionAge()
            )

            logger.info(f"WebSocket connection established to {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            if self.on_error:
                await self.on_error(e)
            return False

    async def _pingLoop(self):
        """Send periodic pings to keep connection alive."""
        while self.is_connected and not self.is_closing:
            try:
                # Wait for ping interval
                await asyncio.sleep(self.ping_interval)

                # Send ping message
                if self.is_connected:
                    ping_id = str(uuid.uuid4())
                    ping_message = {"id": ping_id, "method": "ping"}
                    await self.websocket.send(json.dumps(ping_message))
                    logger.debug(f"Sent ping message with ID: {ping_id}")

                    # Wait for pong response (handled in _receiveLoop)
                    # If no activity for pong_timeout, we'll reconnect
                    wait_until = time.time() + self.pong_timeout
                    while (
                        time.time() < wait_until
                        and time.time() - self.last_message_time > self.pong_timeout
                    ):
                        if not self.is_connected:
                            break
                        await asyncio.sleep(0.5)

                    # Check if we've received any message (including pong)
                    if (
                        self.is_connected
                        and time.time() - self.last_message_time > self.pong_timeout
                    ):
                        logger.warning("No pong response received, reconnecting...")
                        await self._reconnect()

            except Exception as e:
                logger.error(f"Error in ping loop: {str(e)}")
                if not self.is_closing:
                    await self._reconnect()

    async def _monitorConnectionAge(self):
        """Monitor connection age and reconnect before 24-hour limit."""
        while self.is_connected and not self.is_closing:
            try:
                # Check if connection is approaching 24 hours (e.g., 23.5 hours)
                if (
                    self.connection_start_time
                    and time.time() - self.connection_start_time > 23.5 * 60 * 60
                ):
                    logger.info(
                        "Connection approaching 24-hour limit, initiating reconnection"
                    )
                    await self._reconnect()
                    return

                # Check every minute
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in connection monitoring: {str(e)}")

    async def _receiveLoop(self):
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
                    if "rateLimits" in parsed_message:
                        self._update_rate_limits(parsed_message["rateLimits"])

                    # Check for errors
                    if "error" in parsed_message:
                        await self._handle_error(parsed_message)

                    # Process the message with the callback
                    if self.on_message:
                        # FIX: Await the coroutine instead of just calling it
                        await self.on_message(parsed_message)

            except websockets.exceptions.ConnectionClosed as e:
                if not self.is_closing:
                    logger.warning(
                        f"WebSocket connection closed unexpectedly: {str(e)}"
                    )
                    await self._reconnect()
                break

            except Exception as e:
                logger.error(f"Error processing WebSocket message: {str(e)}")
                if self.on_error:
                    await self.on_error(e)
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

        if self.connection_monitoring_task:
            self.connection_monitoring_task.cancel()
            self.connection_monitoring_task = None

        # Close existing connection if any
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
            self.websocket = None

        # Check if we've exceeded reconnection attempts
        if self.reconnect_count >= self.reconnect_attempts:
            logger.error(
                f"Failed to reconnect after {self.reconnect_attempts} attempts"
            )
            if self.on_close:
                await self.on_close()
            return

        # Check if we're IP banned
        if self.ip_banned_until and time.time() * 1000 < self.ip_banned_until:
            ban_remaining_secs = (self.ip_banned_until - time.time() * 1000) / 1000
            logger.warning(
                f"IP banned, delaying reconnection for {ban_remaining_secs:.1f} seconds"
            )

            # Wait until the ban expires
            wait_time = max(0, ban_remaining_secs)
            await asyncio.sleep(wait_time)

            # Reset ban state
            self.ip_banned_until = None

        # Check if we're rate limited
        elif self.retry_after and time.time() * 1000 < self.retry_after:
            retry_secs = (self.retry_after - time.time() * 1000) / 1000
            logger.warning(
                f"Rate limited, delaying reconnection for {retry_secs:.1f} seconds"
            )

            # Wait until retry after time
            wait_time = max(0, retry_secs)
            await asyncio.sleep(wait_time)

            # Reset retry state
            self.retry_after = None

        else:
            # Standard exponential backoff
            self.reconnect_count += 1
            wait_time = min(30, 0.5 * (2**self.reconnect_count))
            logger.warning(
                f"Reconnecting in {wait_time:.2f} seconds (attempt {self.reconnect_count}/{self.reconnect_attempts})"
            )
            await asyncio.sleep(wait_time)

        # Attempt to reconnect
        success = await self.connect()

        if success and self.on_reconnect:
            await self.on_reconnect()

    def _update_rate_limits(self, rate_limits: List[Dict[str, Any]]):
        """
        Update rate limit counters from WebSocket response.

        Args:
            rate_limits: Rate limit information from response
        """
        for limit in rate_limits:
            limit_type = limit.get("rateLimitType")
            interval = limit.get("interval")
            intervalNum = limit.get("intervalNum")
            count = limit.get("count")

            if (
                limit_type
                and interval
                and intervalNum is not None
                and count is not None
            ):
                key = f"{limit_type}_{interval}_{intervalNum}"
                self.rate_limiter.usage[key] = count

    async def _handle_error(self, message: Dict[str, Any]):
        """
        Handle error responses from WebSocket API.

        Processes error messages and handles specific status codes according to
        Binance WebSocket API documentation:
        - 400: Invalid request, issue is on client side
        - 403: Blocked by Web Application Firewall
        - 409: Request partially failed but also partially succeeded
        - 418: Auto-banned for repeated rate limit violations
        - 429: Rate limit exceeded, needs to back off
        - 5xx: Internal server errors, issue is on Binance side

        Args:
            message: Error message from WebSocket
        """
        if "error" in message:
            error = message["error"]
            code = error.get("code", 0)
            msg = error.get("msg", "Unknown error")
            status = message.get("status", 0)

            # Handle rate limit data if present
            if "data" in error:
                data = error["data"]
                if "retryAfter" in data:
                    self.retry_after = data["retryAfter"]
                if "serverTime" in data:
                    server_time = data["serverTime"]

            # Handle specific status codes based on Binance documentation
            if status == 400:
                logger.error(f"WebSocket error: Bad request - {msg}")
            elif status == 403:
                logger.error("WebSocket error: Blocked by Web Application Firewall")
            elif status == 409:
                # Handle partial success case
                logger.warning(f"WebSocket error: Request partially succeeded - {msg}")
                # Additional logic for handling partial success could be added here
                # For example, examine the result part of the response if present
                if "result" in message:
                    logger.info(f"Partial success result: {message['result']}")
            elif status == 418:
                # IP ban
                logger.error("WebSocket error: Auto-banned for rate limit violations")
                if self.retry_after:
                    self.ip_banned_until = self.retry_after
                    ban_duration_mins = (self.retry_after - time.time() * 1000) / (
                        60 * 1000
                    )
                    logger.error(
                        f"IP banned until {self.retry_after} (approximately {ban_duration_mins:.1f} minutes)"
                    )
            elif status == 429:
                # Rate limit exceeded
                logger.warning("WebSocket error: Rate limit exceeded")
                if self.retry_after:
                    retry_seconds = (self.retry_after - time.time() * 1000) / 1000
                    logger.warning(
                        f"Rate limit exceeded, retry after: {self.retry_after} (in {retry_seconds:.1f} seconds)"
                    )
            elif status >= 500:
                logger.error(
                    f"WebSocket error: Internal server error (status {status})"
                )
                # For 5xx errors, request status is unknown
                # Consider checking request status separately via REST API if critical
                logger.warning(
                    "For 5xx errors, request execution status is unknown; consider checking status separately"
                )

            logger.error(f"WebSocket error (code {code}, status {status}): {msg}")

            # Notify error callback
            if self.on_error:
                await self.on_error(Exception(f"WebSocket error (code {code}): {msg}"))

    async def send(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        security_type: SecurityType = SecurityType.NONE,
        return_rate_limits: Optional[bool] = None,
    ) -> str:
        """
        Send a message to the Binance WebSocket API server.

        This method builds and sends a WebSocket request to call any of the Binance
        WebSocket API methods. It handles security requirements based on the endpoint
        type, and manages rate limit tracking.

        Common API methods:
        - "ping": Test connectivity (weight 1)
        - "time": Get server time (weight 1)
        - "exchangeInfo": Get exchange information (weight 10)
        - "ticker.price": Get latest price for a symbol (weight 1-2)
        - "ticker.24hr": Get 24hr ticker price change statistics (weight 1-40)
        - "depth": Get order book (weight 1-10)
        - "trades.recent": Get recent trades (weight 1)
        - "trades.historical": Get historical trades (weight 5)
        - "trades.aggregate": Get aggregate trades (weight 1)
        - "klines": Get kline/candlestick data (weight 1-2)
        - "order.place": Place new order (weight 1, requires TRADE permission)
        - "order.test": Test new order (weight 1, requires TRADE permission)
        - "order.status": Check order status (weight 2, requires USER_DATA permission)
        - "order.cancel": Cancel order (weight 1, requires TRADE permission)
        - "order.cancelReplace": Cancel and replace order (weight 1, requires TRADE permission)
        - "account.status": Get account status (weight 10, requires USER_DATA permission)

        Args:
            method: API method to call
            params: Parameters for the method
            security_type: Type of security required for this request
            return_rate_limits: Override default setting for returning rate limits

        Returns:
            Message ID that can be used to match the response

        Raises:
            ConnectionError: If WebSocket is not connected
            Exception: If IP banned or rate limited
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")

        # Check for IP ban
        if self.ip_banned_until and time.time() * 1000 < self.ip_banned_until:
            ban_remaining_secs = (self.ip_banned_until - time.time() * 1000) / 1000
            raise Exception(
                f"IP banned, cannot send request for {ban_remaining_secs:.1f} more seconds"
            )

        # Check for rate limit retry-after
        if self.retry_after and time.time() * 1000 < self.retry_after:
            retry_remaining_secs = (self.retry_after - time.time() * 1000) / 1000
            raise Exception(
                f"Rate limited, retry after {retry_remaining_secs:.1f} more seconds"
            )

        # Handle security requirements
        if security_type in (SecurityType.TRADE, SecurityType.USER_DATA):
            return await self.send_signed(method, params, return_rate_limits)
        elif security_type in (SecurityType.USER_STREAM, SecurityType.MARKET_DATA):
            # Add API key to params
            if params is None:
                params = {}
            else:
                # Make a copy to avoid modifying the original
                params = params.copy()
            params["apiKey"] = Secrets.BINANCE_API_KEY

        # Generate message ID
        msg_id = str(self.message_id)
        self.message_id += 1

        # Create message
        message = {"id": msg_id, "method": method}

        # Add parameters if any
        if params:
            # Make a copy of params to avoid modifying the original
            msg_params = params.copy() if params else {}

            # Handle rate limits return preference if specified
            if return_rate_limits is not None:
                msg_params["returnRateLimits"] = return_rate_limits

            message["params"] = msg_params

        # Send the message
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Sent WebSocket request: method={method}, id={msg_id}")
        return msg_id

    async def send_signed(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        return_rate_limits: Optional[bool] = None,
    ) -> str:
        """
        Send a signed message to the Binance WebSocket API server.

        This method is used for authenticated requests that require signing with the API secret.
        It automatically adds the required timestamp and signature to the request parameters.

        Signed endpoints require both an API key and a signature. The signature is computed using
        HMAC-SHA256 on a sorted query string of all parameters.

        Args:
            method: API method to call (e.g., "order.place", "account.status")
            params: Parameters for the method
            return_rate_limits: Override default setting for returning rate limits

        Returns:
            Message ID that can be used to match the response

        Raises:
            ConnectionError: If WebSocket is not connected
            Exception: If IP banned or rate limited
        """
        if not self.is_connected:
            raise ConnectionError("WebSocket is not connected")

        # Check for IP ban
        if self.ip_banned_until and time.time() * 1000 < self.ip_banned_until:
            ban_remaining_secs = (self.ip_banned_until - time.time() * 1000) / 1000
            raise Exception(
                f"IP banned, cannot send request for {ban_remaining_secs:.1f} more seconds"
            )

        # Check for rate limit retry-after
        if self.retry_after and time.time() * 1000 < self.retry_after:
            retry_remaining_secs = (self.retry_after - time.time() * 1000) / 1000
            raise Exception(
                f"Rate limited, retry after {retry_remaining_secs:.1f} more seconds"
            )

        # Generate message ID
        msg_id = str(self.message_id)
        self.message_id += 1

        # Create params if not provided
        if params is None:
            params = {}
        else:
            # Make a copy to avoid modifying the original
            params = params.copy()

        # Add timestamp and API key
        params["timestamp"] = int(time.time() * 1000)
        params["apiKey"] = Secrets.BINANCE_API_KEY

        # Handle rate limits return preference if specified
        if return_rate_limits is not None:
            params["returnRateLimits"] = return_rate_limits

        # Generate signature
        # Sort parameters alphabetically as required by Binance
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            Secrets.BINANCE_API_SECRET.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Add signature to params
        params["signature"] = signature

        # Create message
        message = {"id": msg_id, "method": method, "params": params}

        # Send the message
        await self.websocket.send(json.dumps(message))
        logger.debug(f"Sent signed WebSocket request: method={method}, id={msg_id}")
        return msg_id

    async def close(self):
        """
        Close the WebSocket connection.

        This method gracefully closes the WebSocket connection, cancels all
        associated tasks, and notifies via the on_close callback if provided.
        """
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

        if self.connection_monitoring_task:
            self.connection_monitoring_task.cancel()
            self.connection_monitoring_task = None

        # Close WebSocket
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

        # Notify closure
        if self.on_close:
            await self.on_close()

        logger.info("WebSocket connection closed")


class BinanceWebSocketClient:
    """
    Base class for Binance WebSocket API clients.

    Provides common functionality for specific WebSocket client implementations.
    This serves as a foundation for market, user, and trading stream clients.
    """

    def __init__(self):
        """Initialize the WebSocket client."""
        self.connections = {}
        self.callbacks = {}
        self.response_handlers = {}

    async def _create_connection(
        self,
        on_message: Callable[[Dict[str, Any]], Awaitable[None]],
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
        on_reconnect: Optional[Callable[[], Awaitable[None]]] = None,
        on_close: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> BinanceWebSocketConnection:
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
            on_close=on_close,
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
        msg_id = message.get("id")

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
