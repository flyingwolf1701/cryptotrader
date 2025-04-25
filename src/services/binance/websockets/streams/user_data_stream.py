"""
Binance User Data Stream

This module provides functionality for managing user data streams via the Binance API.
It handles obtaining, extending, and closing listenKeys, as well as connecting to
and processing messages from user data streams.
"""

import json
import time
import hmac
import hashlib
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable, Union

import httpx
import websockets
from websockets.exceptions import ConnectionClosed

from config import get_logger, Secrets
from .services.binance.websocketAPI.websocket_stream_manager import BinanceStreamManager

logger = get_logger(__name__)


class UserDataStream:
    """
    Manages the Binance User Data Stream for account updates.

    This class handles:
    - Obtaining a listenKey via REST API
    - Periodically extending the listenKey validity
    - Connecting to the WebSocket stream
    - Processing account update messages
    """

    def __init__(
        self,
        on_account_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_order_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_oco_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_balance_update: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None,
        on_error: Optional[Callable[[Exception], Awaitable[None]]] = None,
        ping_interval: int = 30 * 60,  # 30 minutes in seconds
        use_combined_stream: bool = False,
    ):
        """
        Initialize the user data stream manager.

        Args:
            on_account_update: Callback for outboundAccountPosition events
            on_order_update: Callback for executionReport events
            on_oco_update: Callback for listStatus events
            on_balance_update: Callback for balanceUpdate events
            on_error: Callback for errors
            ping_interval: How often to ping (extend listenKey validity) in seconds
            use_combined_stream: Whether to use the combined stream endpoint
        """
        self.on_account_update = on_account_update
        self.on_order_update = on_order_update
        self.on_oco_update = on_oco_update
        self.on_balance_update = on_balance_update
        self.on_error = on_error
        self.ping_interval = ping_interval
        self.use_combined_stream = use_combined_stream

        # Stream state
        self.listen_key = None
        self.stream_manager = None
        self.ping_task = None
        self.is_active = False

        # REST API endpoints
        self.base_api_url = "https://api.binance.us"
        self.listen_key_endpoint = "/api/v3/userDataStream"

    async def start(self) -> bool:
        """
        Start the user data stream.

        This method:
        1. Obtains a listenKey from the REST API
        2. Establishes a WebSocket connection using the listenKey
        3. Starts periodic pinging to keep the stream alive

        Returns:
            True if successful, False otherwise
        """
        if self.is_active:
            return True

        # Get a new listenKey
        success = await self._create_listen_key()
        if not success:
            return False

        # Create stream manager with message handler
        async def on_message(stream_name: str, data: Dict[str, Any]):
            await self._process_user_data_message(data)

        async def on_error(error: Exception):
            logger.error(f"Stream error: {str(error)}")
            if self.on_error:
                await self.on_error(error)

        async def on_close():
            logger.info("User data stream closed")
            self.is_active = False

        self.stream_manager = BinanceStreamManager(
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            use_combined_stream=self.use_combined_stream,
        )

        # Connect and subscribe
        await self.stream_manager.connect()

        if self.use_combined_stream:
            await self.stream_manager.subscribe(self.listen_key)
        else:
            # For raw stream, the listen_key is part of the URL and not a subscription
            pass

        # Start ping task to keep listenKey alive
        self.ping_task = asyncio.create_task(self._ping_loop())

        self.is_active = True
        logger.info(
            f"User data stream started with listenKey: {self.listen_key[:10]}..."
        )
        return True

    async def stop(self) -> bool:
        """
        Stop the user data stream.

        This method:
        1. Stops the periodic ping task
        2. Closes the WebSocket connection
        3. Invalidates the listenKey via the REST API

        Returns:
            True if successful, False otherwise
        """
        if not self.is_active:
            return True

        # Cancel ping task
        if self.ping_task:
            self.ping_task.cancel()
            self.ping_task = None

        # Close WebSocket connection
        if self.stream_manager:
            await self.stream_manager.close()
            self.stream_manager = None

        # Delete listenKey
        if self.listen_key:
            success = await self._close_listen_key()
            self.listen_key = None

        self.is_active = False
        logger.info("User data stream stopped")
        return True

    async def _create_listen_key(self) -> bool:
        """
        Obtain a new listenKey from the REST API.

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_api_url}{self.listen_key_endpoint}"
        headers = {"X-MBX-APIKEY": Secrets.BINANCE_API_KEY}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "listenKey" in data:
                    self.listen_key = data["listenKey"]
                    logger.info(f"Obtained listenKey: {self.listen_key[:10]}...")
                    return True
                else:
                    logger.error(f"Failed to get listenKey: {data}")
                    return False

        except Exception as e:
            logger.error(f"Error creating listenKey: {str(e)}")
            if self.on_error:
                await self.on_error(e)
            return False

    async def _extend_listen_key(self) -> bool:
        """
        Extend the validity of the current listenKey.

        Returns:
            True if successful, False otherwise
        """
        if not self.listen_key:
            return False

        url = f"{self.base_api_url}{self.listen_key_endpoint}"
        headers = {"X-MBX-APIKEY": Secrets.BINANCE_API_KEY}
        params = {"listenKey": self.listen_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(url, headers=headers, params=params)
                response.raise_for_status()

                # Empty response is expected
                logger.debug(f"Extended listenKey validity: {self.listen_key[:10]}...")
                return True

        except Exception as e:
            logger.error(f"Error extending listenKey validity: {str(e)}")
            if self.on_error:
                await self.on_error(e)
            return False

    async def _close_listen_key(self) -> bool:
        """
        Invalidate the current listenKey.

        Returns:
            True if successful, False otherwise
        """
        if not self.listen_key:
            return True

        url = f"{self.base_api_url}{self.listen_key_endpoint}"
        headers = {"X-MBX-APIKEY": Secrets.BINANCE_API_KEY}
        params = {"listenKey": self.listen_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, headers=headers, params=params)
                response.raise_for_status()

                # Empty response is expected
                logger.debug(f"Closed listenKey: {self.listen_key[:10]}...")
                return True

        except Exception as e:
            logger.error(f"Error closing listenKey: {str(e)}")
            if self.on_error:
                await self.on_error(e)
            return False

    async def _ping_loop(self):
        """
        Periodically extend the listenKey validity to keep the stream alive.

        The listenKey is valid for 60 minutes, but we ping every 30 minutes
        as recommended by Binance.
        """
        while self.is_active and self.listen_key:
            try:
                # Wait for ping interval
                await asyncio.sleep(self.ping_interval)

                # Check if still active
                if not self.is_active or not self.listen_key:
                    break

                # Extend listenKey validity
                success = await self._extend_listen_key()
                if not success and self.is_active:
                    # If extension fails, try to restart the stream
                    logger.warning("Failed to extend listenKey, restarting stream")
                    await self.stop()
                    await self.start()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in ping loop: {str(e)}")
                if self.on_error:
                    await self.on_error(e)

    async def _process_user_data_message(self, data: Dict[str, Any]):
        """
        Process a user data message and route it to the appropriate callback.

        Args:
            data: WebSocket message data
        """
        if not data or "e" not in data:
            logger.warning(f"Received invalid user data message: {data}")
            return

        event_type = data["e"]

        try:
            if event_type == "outboundAccountPosition" and self.on_account_update:
                await self.on_account_update(data)
            elif event_type == "executionReport" and self.on_order_update:
                await self.on_order_update(data)
            elif event_type == "listStatus" and self.on_oco_update:
                await self.on_oco_update(data)
            elif event_type == "balanceUpdate" and self.on_balance_update:
                await self.on_balance_update(data)
            else:
                logger.debug(f"Unhandled user data event type: {event_type}")

        except Exception as e:
            logger.error(f"Error processing user data message: {str(e)}")
            if self.on_error:
                await self.on_error(e)
