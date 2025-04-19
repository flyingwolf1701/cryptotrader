"""
Binance Order Book Diagnostic Script
-----------------------------------
Tests the Binance Order Book WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/order_book_diagnostic.py
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
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.market_data_requests.order_book import (
    get_order_book,
    process_order_book_response
)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
LIMIT = 10  # Number of order book levels to fetch

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

async def main():
    """Run the order book diagnostic test"""
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
        # The get_order_book function will use this connection
        from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection
        connection = BinanceWebSocketConnection(
            on_message=on_message,
            on_error=on_error
        )
        
        await connection.connect()
        logger.info("WebSocket connection established")
        
        # Test order book
        print_test_header(f"Getting order book for {TEST_SYMBOL} with {LIMIT} levels")
        
        # Send request
        msg_id = await get_order_book(
            connection=connection,
            symbol=TEST_SYMBOL,
            limit=LIMIT
        )
        
        logger.info(f"Request sent with ID: {msg_id}")
        
        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)
        
        # Process response
        if response_received:
            order_book = await process_order_book_response(response_data)
            if order_book:
                logger.info(f"✓ Successfully retrieved order book")
                logger.info(f"  Last update ID: {order_book.last_update_id}")
                
                # Display bid/ask information
                if order_book.bids:
                    logger.info(f"  Bids: {len(order_book.bids)} levels")
                    logger.info(f"  Top bid: {order_book.bids[0].price} (quantity: {order_book.bids[0].quantity})")
                    
                if order_book.asks:
                    logger.info(f"  Asks: {len(order_book.asks)} levels")
                    logger.info(f"  Top ask: {order_book.asks[0].price} (quantity: {order_book.asks[0].quantity})")
                
                # Calculate bid-ask spread
                if order_book.bids and order_book.asks:
                    spread = order_book.asks[0].price - order_book.bids[0].price
                    spread_pct = (spread / order_book.bids[0].price) * 100
                    logger.info(f"  Bid-Ask Spread: {spread} ({spread_pct:.4f}%)")
                
                # Calculate cumulative volumes
                bid_volume = sum(bid.quantity for bid in order_book.bids)
                ask_volume = sum(ask.quantity for ask in order_book.asks)
                logger.info(f"  Cumulative bid volume: {bid_volume}")
                logger.info(f"  Cumulative ask volume: {ask_volume}")
                logger.info(f"  Bid/Ask volume ratio: {bid_volume/ask_volume if ask_volume else 'N/A'}")
            else:
                logger.error("✗ Failed to process order book response")
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