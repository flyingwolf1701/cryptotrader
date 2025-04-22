"""
Binance Historical Trades Diagnostic Script
------------------------------------------
Tests the Binance Historical Trades WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/historical_trades_diagnostic.py
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
from cryptotrader.services.binance.websocketAPI.market_data_requests.historical_trades import (
    get_historical_trades_ws,
    process_historical_trades_response,
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
LIMIT = 5  # Number of trades to fetch


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


async def main():
    """Run the historical trades diagnostic test"""
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
        # The get_historical_trades_ws function will use this connection
        from cryptotrader.services.binance.websocketAPI.base_operations import (
            BinanceWebSocketConnection,
        )

        connection = BinanceWebSocketConnection(
            on_message=on_message, on_error=on_error
        )

        await connection.connect()
        logger.info("WebSocket connection established")

        # Test historical trades
        print_test_header(f"Getting historical trades for {TEST_SYMBOL}")

        # Send request
        msg_id = await get_historical_trades_ws(
            connection=connection, symbol=TEST_SYMBOL, limit=LIMIT
        )

        logger.info(f"Request sent with ID: {msg_id}")

        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)

        # Process response
        if response_received:
            trades = await process_historical_trades_response(response_data)
            if trades and len(trades) > 0:
                logger.info(f"✓ Successfully retrieved {len(trades)} historical trades")

                # Display first trade info
                first_trade = trades[0]
                logger.info(f"First trade details:")
                logger.info(f"  ID: {first_trade.id}")
                logger.info(f"  Price: {first_trade.price}")
                logger.info(f"  Quantity: {first_trade.quantity}")
                logger.info(
                    f"  Time: {datetime.fromtimestamp(first_trade.time / 1000)}"
                )
                logger.info(f"  Buyer Maker: {first_trade.isBuyerMaker}")
            else:
                logger.error("✗ No trades returned in the response")
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
