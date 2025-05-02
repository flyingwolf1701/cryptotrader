"""
Binance Klines Diagnostic Script
-------------------------------
Tests the Binance Klines (Candlestick) WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/klines_diagnostic.py
"""

import sys
import asyncio
import traceback
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(
    __file__
).parent.parent.parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.websockets.market_data_requests.klines import (
    get_klines_ws,
    process_klines_response,
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
INTERVAL = "1h"  # 1-hour interval
LIMIT = 5  # Number of candles to fetch


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


async def main():
    """Run the klines diagnostic test"""
    logger.info(f"Added {project_root} to Python path")

    print_test_header("Setting up WebSocket connection")

    # Setup message handler
    response_received = False
    response_data = None
    connection = None

    async def on_message(message):
        nonlocal response_received, response_data
        response_received = True
        response_data = message
        logger.debug(f"Received message: {message}")

    async def on_error(error):
        logger.error(f"WebSocket error: {str(error)}")

    try:
        # Create a simple WebSocket connection
        # The get_klines_ws function will use this connection
        from cryptotrader.services.binance.websockets.baseOperations import (
            BinanceWebSocketConnection,
        )

        connection = BinanceWebSocketConnection(
            on_message=on_message, on_error=on_error
        )

        await connection.connect()
        logger.info("WebSocket connection established")

        # Test klines
        print_test_header(f"Getting {INTERVAL} klines for {TEST_SYMBOL}")

        # Send request
        msg_id = await get_klines_ws(
            connection=connection, symbol=TEST_SYMBOL, interval=INTERVAL, limit=LIMIT
        )

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            candles = await process_klines_response(response_data)
            if candles and len(candles) > 0:
                logger.info(
                    f"✓ Successfully retrieved {len(candles)} {INTERVAL} candlesticks"
                )

                # Display first candle info
                first_candle = candles[0]
                logger.info(f"First candle details:")
                logger.info(
                    f"  Timestamp: {datetime.fromtimestamp(first_candle.timestamp / 1000)}"
                )
                logger.info(f"  Open: {first_candle.openPrice}")
                logger.info(f"  High: {first_candle.highPrice}")
                logger.info(f"  Low: {first_candle.lowPrice}")
                logger.info(f"  Close: {first_candle.closePrice}")
                logger.info(f"  Volume: {first_candle.volume}")

                # Price range analysis
                high_prices = [c.highPrice for c in candles]
                low_prices = [c.lowPrice for c in candles]
                max_price = max(high_prices)
                min_price = min(low_prices)
                price_range = max_price - min_price
                logger.info(
                    f"Price range in sample: {price_range} ({min_price} to {max_price})"
                )
            else:
                logger.error("✗ No candles returned in the response")
        else:
            logger.error("✗ No response received")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        logger.error(traceback.format_exc())

    finally:
        # Close connection
        if connection:
            await connection.close()
            logger.info("WebSocket connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Diagnostic interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in diagnostic: {str(e)}")
        logger.error(traceback.format_exc())
