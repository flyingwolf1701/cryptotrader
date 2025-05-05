"""
Binance WebSocket Stream Manager

This module provides functionality for managing WebSocket stream subscriptions.
It handles subscribing, unsubscribing, and processing messages from Binance WebSocket streams.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

import websockets
from websockets.exceptions import ConnectionClosed

from cryptotrader.config import get_logger, Secrets

logger = get_logger(__name__)


class BinanceStreamManager:
    """
    Manages WebSocket streams for real-time data from Binance.

    This class handles connections to Binance WebSocket streams, including:
    - Subscribing/unsubscribing to streams
    - Processing messages from streams
    - Connection management and reconnection
    - Combined stream support

    The Binance WebSocket stream endpoints are:
    - Single streams: wss://stream.binance.us:9443/ws/<streamName>
    - Combined streams: wss://stream.binance.us:9443/stream?streams=<streamName1>/<streamName2>
    """

    def __init__(
        self,
        on_message: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None,
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
        on_close: Optional[Callable[[], Awaitable[None]]] = None,
        ping_interval: int = 180,  # 3 minutes in seconds
        pong_timeout: int = 10,  # 10 seconds timeout for pong
        reconnect_attempts: int = 5,
        use_combined_stream: bool = True,
    ):
        """
        Initialize the WebSocket stream manager.

        Args:
            on_message: Callback for messages, with stream_name and data parameters
            on_error: Callback for errors
            on_close: Callback for when connection closes
            ping_interval: How often to ping (seconds), default 180s (3 minutes)
            pong_timeout: How long to wait for pong (seconds), default 10s
            reconnect_attempts: Maximum number of reconnection attempts
            use_combined_stream: Whether to use the combined stream endpoint
        """
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.ping_interval = ping_interval
        self.pong_timeout = pong_timeout
        self.reconnect_attempts = reconnect_attempts
        self.use_combined_stream = use_combined_stream

        # Connection state
        self.websocket = None
        self.is_connected = False
        self.is_closing = False
        self.reconnect_count = 0
        self.last_message_time = 0
        self.connection_start_time = None

        # Stream state
        self.subscribed_streams = set()
        self.message_id = 1
        self.message_callbacks = {}

        # Tasks
        self.ping_task = None
        self.receive_task = None
        self.connection_monitoring_task = None

        # Base endpoints
        self.base_endpoint = "wss://stream.binance.us:9443"
        self.combined_endpoint = f"{self.base_endpoint}/stream"
        self.single_endpoint = f"{self.base_endpoint}/ws"

    async def connect(self) -> bool:
        """
        Establish a WebSocket connection to Binance stream API.

        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            return True

        try:
            # Determine URL based on current subscriptions and settings
            if self.use_combined_stream:
                if self.subscribed_streams:
                    streams_param = "/".join(self.subscribed_streams)
                    url = f"{self.combined_endpoint}?streams={streams_param}"
                else:
                    # No streams yet, use a placeholder that we'll subscribe to later
                    url = f"{self.combined_endpoint}"
            else:
                if len(self.subscribed_streams) == 1:
                    stream_name = next(iter(self.subscribed_streams))
                    url = f"{self.single_endpoint}/{stream_name}"
                elif not self.subscribed_streams:
                    # No streams yet, connect to base endpoint
                    url = f"{self.single_endpoint}"
                else:
                    # Multiple streams but not using combined mode - not allowed
                    raise ValueError("Multiple streams require combined stream mode")

            # Create connection with no ping/pong control (we'll handle it)
            self.websocket = await websockets.connect(
                url,
                ping_interval=None,  # We'll handle pings manually
                max_size=None,  # No message size limit
                close_timeout=5,  # 5 seconds to close gracefully
            )

            # Connection established
            self.is_connected = True
            self.reconnect_count = 0
            self.last_message_time = asyncio.get_event_loop().time()
            self.connection_start_time = asyncio.get_event_loop().time()

            # Start tasks
            self.ping_task = asyncio.create_task(self._pingLoop())
            self.receive_task = asyncio.create_task(self._receiveLoop())
            self.connection_monitoring_task = asyncio.create_task(
                self._monitorConnectionAge()
            )

            logger.info(f"WebSocket connection established to {url}")

            # If we have streams and connected to a base endpoint, subscribe now
            if self.subscribed_streams and (
                (self.use_combined_stream and "streams" not in url)
                or (not self.use_combined_stream and "stream_name" not in url)
            ):
                await self._send_subscription_request(
                    list(self.subscribed_streams), True
                )

            return True

        except Exception as e:
            logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            if self.on_error:
                await self.on_error(e)
            return False

    async def subscribe(self, streams: Union[str, List[str]]) -> bool:
        """
        Subscribe to one or more streams.

        Args:
            streams: Stream name or list of stream names
                    (e.g., "btcusdt@aggTrade" or ["btcusdt@aggTrade", "btcusdt@depth"])

        Returns:
            True if successful, False otherwise
        """
        if isinstance(streams, str):
            streams = [streams]

        # Check if already subscribed
        new_streams = [s for s in streams if s not in self.subscribed_streams]
        if not new_streams:
            return True

        # If we're using single stream mode and already have a stream, we need to reconnect
        if not self.use_combined_stream and self.subscribed_streams:
            # Add to our tracking set
            self.subscribed_streams.update(new_streams)

            # We need to disconnect and reconnect with combined mode
            await self.close()
            self.use_combined_stream = True
            return await self.connect()

        # For combined stream or no current streams, we can subscribe via message
        if self.is_connected:
            success = await self._send_subscription_request(new_streams, True)
            if success:
                self.subscribed_streams.update(new_streams)
            return success
        else:
            # Not connected yet, just update our tracking
            self.subscribed_streams.update(new_streams)
            return True

    async def unsubscribe(self, streams: Union[str, List[str]]) -> bool:
        """
        Unsubscribe from one or more streams.

        Args:
            streams: Stream name or list of stream names
                    (e.g., "btcusdt@aggTrade" or ["btcusdt@aggTrade", "btcusdt@depth"])

        Returns:
            True if successful, False otherwise
        """
        if isinstance(streams, str):
            streams = [streams]

        # Check if actually subscribed
        existing_streams = [s for s in streams if s in self.subscribed_streams]
        if not existing_streams:
            return True

        # If we're using single stream mode, we need to reconnect
        if not self.use_combined_stream:
            # Update our tracking set
            self.subscribed_streams.difference_update(existing_streams)

            # We need to disconnect and reconnect
            await self.close()
            return await self.connect()

        # For combined stream, we can unsubscribe via message
        if self.is_connected:
            success = await self._send_subscription_request(existing_streams, False)
            if success:
                self.subscribed_streams.difference_update(existing_streams)
            return success
        else:
            # Not connected yet, just update our tracking
            self.subscribed_streams.difference_update(existing_streams)
            return True

    async def list_subscriptions(self) -> List[str]:
        """
        List all current subscriptions.

        Returns:
            List of stream names currently subscribed to
        """
        if self.is_connected and self.use_combined_stream:
            # We can query the server for current subscriptions
            msg_id = self.message_id
            self.message_id += 1

            # Create a future to wait for the response
            future = asyncio.get_running_loop().create_future()
            self.message_callbacks[str(msg_id)] = lambda data: future.set_result(data)

            # Send the request
            request = {"method": "LIST_SUBSCRIPTIONS", "id": msg_id}
            await self.websocket.send(json.dumps(request))

            try:
                # Wait for the response with a timeout
                response = await asyncio.wait_for(future, timeout=5.0)

                if "result" in response and isinstance(response["result"], list):
                    # Update our local tracking to match server state
                    self.subscribed_streams = set(response["result"])
                    return response["result"]
                else:
                    logger.warning(
                        f"Unexpected LIST_SUBSCRIPTIONS response: {response}"
                    )
                    return list(self.subscribed_streams)

            except asyncio.TimeoutError:
                logger.error("Timeout waiting for LIST_SUBSCRIPTIONS response")
                return list(self.subscribed_streams)
            except Exception as e:
                logger.error(f"Error listing subscriptions: {str(e)}")
                return list(self.subscribed_streams)
        else:
            # Just return what we're tracking locally
            return list(self.subscribed_streams)

    async def set_property(self, property_name: str, property_value: Any) -> bool:
        """
        Set a property for the WebSocket connection.

        Currently, the only supported property is 'combined' (boolean).

        Args:
            property_name: Name of the property to set
            property_value: Value to set

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.use_combined_stream:
            return False

        if property_name not in ["combined"]:
            logger.error(f"Unsupported property: {property_name}")
            return False

        msg_id = self.message_id
        self.message_id += 1

        # Create a future to wait for the response
        future = asyncio.get_running_loop().create_future()
        self.message_callbacks[str(msg_id)] = lambda data: future.set_result(data)

        # Send the request
        request = {
            "method": "SET_PROPERTY",
            "params": [property_name, property_value],
            "id": msg_id,
        }
        await self.websocket.send(json.dumps(request))

        try:
            # Wait for the response with a timeout
            response = await asyncio.wait_for(future, timeout=5.0)

            if "result" in response and response["result"] is None:
                return True
            else:
                logger.warning(f"Unexpected SET_PROPERTY response: {response}")
                return False

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for SET_PROPERTY response")
            return False
        except Exception as e:
            logger.error(f"Error setting property: {str(e)}")
            return False

    async def get_property(self, property_name: str) -> Any:
        """
        Get a property value from the WebSocket connection.

        Currently, the only supported property is 'combined' (boolean).

        Args:
            property_name: Name of the property to get

        Returns:
            Property value if successful, None otherwise
        """
        if not self.is_connected or not self.use_combined_stream:
            return None

        if property_name not in ["combined"]:
            logger.error(f"Unsupported property: {property_name}")
            return None

        msg_id = self.message_id
        self.message_id += 1

        # Create a future to wait for the response
        future = asyncio.get_running_loop().create_future()
        self.message_callbacks[str(msg_id)] = lambda data: future.set_result(data)

        # Send the request
        request = {"method": "GET_PROPERTY", "params": [property_name], "id": msg_id}
        await self.websocket.send(json.dumps(request))

        try:
            # Wait for the response with a timeout
            response = await asyncio.wait_for(future, timeout=5.0)

            if "result" in response:
                return response["result"]
            else:
                logger.warning(f"Unexpected GET_PROPERTY response: {response}")
                return None

        except asyncio.TimeoutError:
            logger.error("Timeout waiting for GET_PROPERTY response")
            return None
        except Exception as e:
            logger.error(f"Error getting property: {str(e)}")
            return None

    async def close(self):
        """
        Close the WebSocket connection and clean up resources.
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

        logger.info("WebSocket stream connection closed")

    async def _send_subscription_request(
        self, streams: List[str], subscribe: bool
    ) -> bool:
        """
        Send a subscription/unsubscription request to the server.

        Args:
            streams: List of stream names
            subscribe: True to subscribe, False to unsubscribe

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected or not self.websocket:
            return False

        method = "SUBSCRIBE" if subscribe else "UNSUBSCRIBE"
        msg_id = self.message_id
        self.message_id += 1

        # Create a future to wait for the response
        future = asyncio.get_running_loop().create_future()
        self.message_callbacks[str(msg_id)] = lambda data: future.set_result(data)

        # Send the request
        request = {"method": method, "params": streams, "id": msg_id}
        await self.websocket.send(json.dumps(request))

        try:
            # Wait for the response with a timeout
            response = await asyncio.wait_for(future, timeout=5.0)

            if "result" in response and response["result"] is None:
                return True
            else:
                error_msg = response.get("error", {}).get("msg", "Unknown error")
                logger.error(f"{method} request failed: {error_msg}")
                return False

        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for {method} response")
            return False
        except Exception as e:
            logger.error(f"Error in {method} request: {str(e)}")
            return False

    async def _pingLoop(self):
        """Send periodic pings to keep connection alive."""
        while self.is_connected and not self.is_closing:
            try:
                # Wait for ping interval
                await asyncio.sleep(self.ping_interval)

                # Check if connection is still active
                if not self.is_connected or self.is_closing:
                    break

                # Send ping frame
                if self.websocket:
                    await self.websocket.ping()
                    logger.debug("Sent ping frame")

                    # Check for pong response
                    current_time = asyncio.get_running_loop().time()
                    pong_wait_until = current_time + self.pong_timeout

                    while asyncio.get_running_loop().time() < pong_wait_until:
                        if (
                            asyncio.get_running_loop().time() - self.last_message_time
                            < self.pong_timeout
                            or not self.is_connected
                        ):
                            break
                        await asyncio.sleep(0.5)

                    # If no pong received within timeout, reconnect
                    if (
                        self.is_connected
                        and asyncio.get_running_loop().time() - self.last_message_time
                        > self.pong_timeout
                    ):
                        logger.warning("No pong response received, reconnecting...")
                        await self._reconnect()

            except Exception as e:
                logger.error(f"Error in ping loop: {str(e)}")
                if not self.is_closing:
                    await self._reconnect()

    async def _receiveLoop(self):
        """Receive and process incoming WebSocket messages."""
        while self.is_connected and not self.is_closing:
            try:
                # Wait for a message
                message = await self.websocket.recv()
                self.last_message_time = asyncio.get_running_loop().time()

                # Parse and process the message
                if message:
                    try:
                        data = json.loads(message)

                        # Handle response messages (with ID)
                        if "id" in data:
                            msg_id = str(data["id"])
                            if msg_id in self.message_callbacks:
                                callback = self.message_callbacks.pop(msg_id)
                                callback(data)

                        # Handle stream data messages
                        elif self.on_message:
                            if (
                                self.use_combined_stream
                                and "stream" in data
                                and "data" in data
                            ):
                                # Combined stream format
                                stream_name = data["stream"]
                                payload = data["data"]
                                await self.on_message(stream_name, payload)
                            else:
                                # Single stream format - use the first subscription as the name
                                if self.subscribed_streams:
                                    stream_name = next(iter(self.subscribed_streams))
                                    await self.on_message(stream_name, data)
                                else:
                                    logger.warning(
                                        "Received data but no subscribed streams"
                                    )

                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse WebSocket message: {message}")

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

    async def _monitorConnectionAge(self):
        """Monitor connection age and reconnect before 24-hour limit."""
        while self.is_connected and not self.is_closing:
            try:
                # Check if connection is approaching 24 hours (e.g., 23.5 hours)
                current_time = asyncio.get_running_loop().time()
                if (
                    self.connection_start_time
                    and current_time - self.connection_start_time > 23.5 * 60 * 60
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
            self.is_closing = True
            if self.on_close:
                await self.on_close()
            return

        # Standard exponential backoff
        self.reconnect_count += 1
        wait_time = min(30, 0.5 * (2**self.reconnect_count))
        logger.warning(
            f"Reconnecting in {wait_time:.2f} seconds (attempt {self.reconnect_count}/{self.reconnect_attempts})"
        )
        await asyncio.sleep(wait_time)

        # Attempt to reconnect
        success = await self.connect()

        # If reconnected successfully, resubscribe to streams
        if success and self.subscribed_streams:
            await self._send_subscription_request(list(self.subscribed_streams), True)


async def createMarketStream(
    symbols: List[str],
    channels: List[str],
    on_message: Callable[[str, Dict[str, Any]], Awaitable[None]],
    use_combined_stream: bool = True,
) -> BinanceStreamManager:
    """
    Create a WebSocket stream manager for market data streams.

    This is a helper function that creates streams based on symbols and channels.

    Args:
        symbols: List of trading symbols (e.g., ["btcusdt", "ethusdt"])
        channels: List of channels (e.g., ["aggTrade", "depth", "kline_1m"])
        on_message: Callback for processing messages
        use_combined_stream: Whether to use combined streams

    Returns:
        BinanceStreamManager instance
    """
    # Convert symbols to lowercase
    symbols = [s.lower() for s in symbols]

    # Create stream manager
    manager = BinanceStreamManager(
        on_message=on_message, use_combined_stream=use_combined_stream
    )

    # Connect
    await manager.connect()

    # Create stream names (symbol@channel)
    streams = []
    for symbol in symbols:
        for channel in channels:
            streams.append(f"{symbol}@{channel}")

    # Subscribe
    await manager.subscribe(streams)

    return manager
