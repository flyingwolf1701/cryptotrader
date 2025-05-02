"""
Binance Current Average Price Diagnostic Script
----------------------------------------------
Tests the Binance Current Average Price WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/current_average_price_diagnostic.py
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
from cryptotrader.services.binance.websockets.market_data_requests.current_average_price import (
    getAvgPriceWS,
    process_avg_price_response,
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


async def main():
    """Run the current average price diagnostic test"""
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
        from cryptotrader.services.binance.websockets.baseOperations import (
            BinanceWebSocketConnection,
        )

        connection = BinanceWebSocketConnection(
            on_message=on_message, on_error=on_error
        )

        await connection.connect()
        logger.info("WebSocket connection established")

        # Test current average price
        print_test_header(f"Getting current average price for {TEST_SYMBOL}")

        # Send request
        msg_id = await getAvgPriceWS(connection=connection, symbol=TEST_SYMBOL)

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            avg_price = await process_avg_price_response(response_data)
            if avg_price:
                logger.info(f"✓ Successfully retrieved average price")
                logger.info(
                    f"  Average price over {avg_price.mins} minutes: {avg_price.price}"
                )
            else:
                logger.error("✗ Failed to process average price response")
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
