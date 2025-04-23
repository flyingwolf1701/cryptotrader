"""
Binance Symbol Order Book Ticker Diagnostic Script
------------------------------------------------
Tests the Binance Symbol Order Book Ticker WebSocket API functionality to verify proper operation.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/symbol_order_book_ticker_diagnostic.py
"""

import sys
import asyncio
import traceback
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from config import get_logger
from cryptotrader.services.binance.websocketAPI.market_data_requests.symbol_order_book_ticker import (
    get_book_ticker,
    process_book_ticker_response
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
    """Run the symbol order book ticker diagnostic test"""
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
        from services.binance.websockets.base_operations import BinanceWebSocketConnection
        connection = BinanceWebSocketConnection(
            on_message=on_message,
            on_error=on_error
        )
        
        await connection.connect()
        logger.info("WebSocket connection established")
        
        # Test 1: Single symbol order book ticker
        print_test_header(f"Getting order book ticker for {TEST_SYMBOL}")
        response_received = False
        
        # Send request
        msg_id = await get_book_ticker(
            connection=connection,
            symbol=TEST_SYMBOL
        )
        
        logger.info(f"Request sent with ID: {msg_id}")
        
        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)
        
        # Process response
        if response_received:
            ticker = await process_book_ticker_response(response_data)
            if ticker:
                print_test_result(True, f"Successfully retrieved order book ticker for {TEST_SYMBOL}")
                logger.info(f"  Symbol: {ticker.symbol}")
                logger.info(f"  Bid Price: {ticker.bidPrice} (Qty: {ticker.bidQty})")
                logger.info(f"  Ask Price: {ticker.askPrice} (Qty: {ticker.askQty})")
                
                # Calculate and display the spread
                spread = ticker.askPrice - ticker.bidPrice
                spread_pct = (spread / ticker.bidPrice) * 100
                logger.info(f"  Spread: {spread} ({spread_pct:.4f}%)")
            else:
                print_test_result(False, "Failed to process order book ticker response")
        else:
            print_test_result(False, "No response received")
        
        # Test 2: Multiple symbols order book tickers
        print_test_header(f"Getting order book tickers for multiple symbols: {TEST_SYMBOLS}")
        response_received = False
        
        # Send request
        msg_id = await get_book_ticker(
            connection=connection,
            symbols=TEST_SYMBOLS
        )
        
        logger.info(f"Request sent with ID: {msg_id}")
        
        # Wait for response
        for _ in range(10):  # Wait up to 5 seconds
            if response_received:
                break
            await asyncio.sleep(0.5)
        
        # Process response
        if response_received:
            tickers = await process_book_ticker_response(response_data)
            if tickers and isinstance(tickers, list):
                print_test_result(True, f"Successfully retrieved order book tickers for {len(tickers)} symbols")
                
                # Display all tickers in a table format
                logger.info(f"Current order book top:")
                logger.info(f"  {'SYMBOL':<10}  {'BID PRICE':>12}  {'BID QTY':>10}  {'ASK PRICE':>12}  {'ASK QTY':>10}  {'SPREAD %':>10}")
                logger.info(f"  {'-' * 10}  {'-' * 12}  {'-' * 10}  {'-' * 12}  {'-' * 10}  {'-' * 10}")
                
                for ticker in tickers:
                    spread = ticker.askPrice - ticker.bidPrice
                    spread_pct = (spread / ticker.bidPrice) * 100 if ticker.bidPrice > 0 else 0
                    logger.info(f"  {ticker.symbol:<10}  {ticker.bidPrice:>12}  {ticker.bidQty:>10.4f}  "
                               f"{ticker.askPrice:>12}  {ticker.askQty:>10.4f}  {spread_pct:>10.4f}%")
                
                # Analyze the data
                spread_percentages = [(t.askPrice - t.bidPrice) / t.bidPrice * 100 for t in tickers]
                avg_spread = sum(spread_percentages) / len(spread_percentages)
                min_spread = min(spread_percentages)
                max_spread = max(spread_percentages)
                
                logger.info(f"\nSpread Analysis:")
                logger.info(f"  Average Spread: {avg_spread:.4f}%")
                logger.info(f"  Minimum Spread: {min_spread:.4f}%")
                logger.info(f"  Maximum Spread: {max_spread:.4f}%")
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