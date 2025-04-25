"""
Binance Rolling Window Price Diagnostic Script
---------------------------------------------
Tests the Binance Rolling Window Price WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/rolling_window_price_diagnostic.py
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
from config import get_logger
from services.binance.websockets.market_data_requests.rolling_window_price import (
    get_rolling_window_stats,
    process_rolling_window_response,
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
TEST_SYMBOLS = ["BTCUSDT", "ETHUSDT"]  # Multiple symbols for testing
TEST_WINDOW_SIZES = ["1h", "4h", "1d"]  # Window sizes to test


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


def print_test_result(success, message=None):
    """Print a test result in green (success) or red (failure)"""
    if success:
        logger.info(f"{Fore.GREEN}✓ Test passed{Style.RESET_ALL}")
        if message:
            logger.info(f"  {message}")
    else:
        logger.error(f"{Fore.RED}✗ Test failed{Style.RESET_ALL}")
        if message:
            logger.error(f"  {message}")


async def main():
    """Run the rolling window price diagnostic test"""
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
        from services.binance.websockets.base_operations import (
            BinanceWebSocketConnection,
        )

        connection = BinanceWebSocketConnection(
            on_message=on_message, on_error=on_error
        )

        await connection.connect()
        logger.info("WebSocket connection established")

        # Test different window sizes
        for window_size in TEST_WINDOW_SIZES:
            print_test_header(
                f"Getting {window_size} rolling window stats for {TEST_SYMBOL}"
            )
            response_received = False

            # Send request
            msg_id = await get_rolling_window_stats(
                connection=connection, symbol=TEST_SYMBOL, window_size=window_size
            )

            logger.info(f"Request sent with ID: {msg_id}")

            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if response_received:
                    break
                await asyncio.sleep(0.5)

            # Process response
            if response_received:
                stats = await process_rolling_window_response(response_data)
                if stats:
                    print_test_result(
                        True,
                        f"Successfully retrieved {window_size} rolling window stats",
                    )
                    logger.info(f"  Symbol: {stats.symbol}")
                    logger.info(
                        f"  Window: {datetime.fromtimestamp(stats.openTime / 1000)} to {datetime.fromtimestamp(stats.closeTime / 1000)}"
                    )
                    logger.info(
                        f"  Price Change: {stats.priceChange} ({stats.priceChangePercent}%)"
                    )
                    logger.info(f"  High: {stats.highPrice}, Low: {stats.lowPrice}")
                    logger.info(f"  Volume: {stats.volume}")
                else:
                    print_test_result(
                        False,
                        f"Failed to process {window_size} rolling window response",
                    )
            else:
                print_test_result(False, "No response received")

        # Test multiple symbols
        window_size = "1d"  # Use 1 day window for multiple symbols
        print_test_header(
            f"Getting {window_size} rolling window stats for multiple symbols: {TEST_SYMBOLS}"
        )
        response_received = False

        # Send request
        msg_id = await get_rolling_window_stats(
            connection=connection, symbols=TEST_SYMBOLS, window_size=window_size
        )

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            stats_list = await process_rolling_window_response(response_data)
            if stats_list and isinstance(stats_list, list):
                print_test_result(
                    True,
                    f"Successfully retrieved {window_size} rolling window stats for {len(stats_list)} symbols",
                )

                # Display summary of all stats
                logger.info(f"Summary of retrieved stats:")
                for stats in stats_list:
                    logger.info(
                        f"  {stats.symbol}: Change: {stats.priceChange} ({stats.priceChangePercent}%), Volume: {stats.volume}"
                    )
            else:
                print_test_result(False, "Failed to process multiple symbols response")
        else:
            print_test_result(False, "No response received")

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
