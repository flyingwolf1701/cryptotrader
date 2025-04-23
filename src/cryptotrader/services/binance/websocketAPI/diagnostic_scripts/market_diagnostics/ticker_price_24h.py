"""
Binance 24hr Ticker Price Diagnostic Script
------------------------------------------
Tests the Binance 24hr Ticker Price WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/ticker_price_24h_diagnostic.py
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
from cryptotrader.services.binance.websocketAPI.market_data_requests.ticker_price_24h import (
    get_24h_ticker,
    process_24h_ticker_response,
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
TEST_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]  # Multiple symbols for testing


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
    """Run the 24hr ticker price diagnostic test"""
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
        from cryptotrader.services.binance.websocketAPI.base_operations import (
            BinanceWebSocketConnection,
        )

        connection = BinanceWebSocketConnection(
            on_message=on_message, on_error=on_error
        )

        await connection.connect()
        logger.info("WebSocket connection established")

        # Test 1: Single symbol FULL type
        print_test_header(f"Getting 24hr ticker (FULL) for {TEST_SYMBOL}")
        response_received = False

        # Send request
        msg_id = await get_24h_ticker(
            connection=connection, symbol=TEST_SYMBOL, ticker_type="FULL"
        )

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            ticker = await process_24h_ticker_response(
                response_data, ticker_type="FULL"
            )
            if ticker:
                print_test_result(
                    True, f"Successfully retrieved 24hr ticker (FULL) for {TEST_SYMBOL}"
                )
                logger.info(f"  Symbol: {ticker.symbol}")
                logger.info(f"  Last Price: {ticker.lastPrice}")
                logger.info(
                    f"  Price Change: {ticker.priceChange} ({ticker.priceChangePercent}%)"
                )
                logger.info(f"  24h High: {ticker.highPrice}")
                logger.info(f"  24h Low: {ticker.lowPrice}")
                logger.info(f"  24h Volume: {ticker.volume}")
            else:
                print_test_result(False, "Failed to process 24hr ticker response")
        else:
            print_test_result(False, "No response received")

        # Test 2: Single symbol MINI type
        print_test_header(f"Getting 24hr ticker (MINI) for {TEST_SYMBOL}")
        response_received = False

        # Send request
        msg_id = await get_24h_ticker(
            connection=connection, symbol=TEST_SYMBOL, ticker_type="MINI"
        )

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            ticker = await process_24h_ticker_response(
                response_data, ticker_type="MINI"
            )
            if ticker:
                print_test_result(
                    True, f"Successfully retrieved 24hr ticker (MINI) for {TEST_SYMBOL}"
                )
                logger.info(f"  Symbol: {ticker.symbol}")
                logger.info(f"  Last Price: {ticker.lastPrice}")
                logger.info(f"  24h High: {ticker.highPrice}")
                logger.info(f"  24h Low: {ticker.lowPrice}")
                logger.info(f"  24h Volume: {ticker.volume}")
            else:
                print_test_result(False, "Failed to process 24hr ticker response")
        else:
            print_test_result(False, "No response received")

        # Test 3: Multiple symbols
        print_test_header(f"Getting 24hr ticker for multiple symbols: {TEST_SYMBOLS}")
        response_received = False

        # Send request
        msg
        # Test 3: Multiple symbols
        print_test_header(f"Getting 24hr ticker for multiple symbols: {TEST_SYMBOLS}")
        response_received = False

        # Send request
        msg_id = await get_24h_ticker(connection=connection, symbols=TEST_SYMBOLS)

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            tickers = await process_24h_ticker_response(response_data)
            if tickers and isinstance(tickers, list):
                print_test_result(
                    True,
                    f"Successfully retrieved 24hr tickers for {len(tickers)} symbols",
                )

                # Display summary of all tickers
                logger.info(f"Summary of retrieved tickers:")
                for ticker in tickers:
                    logger.info(
                        f"  {ticker.symbol}: Last Price: {ticker.lastPrice}, Change: {ticker.priceChange} ({ticker.priceChangePercent}%)"
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
