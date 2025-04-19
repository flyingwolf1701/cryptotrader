#!/usr/bin/env python3
"""
Binance Order Book WebSocket Request Diagnostic Script
------------------------------------------------------
Tests the Binance Order Book WebSocket request to verify functionality.

This script focuses on testing the order_book.py implementation, which provides
functionality to retrieve order book (market depth) data for a trading symbol
using the Binance WebSocket API.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/order_book_diagnostic.py
"""

import sys
import asyncio
import json
import time
import signal
from pathlib import Path
import traceback
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from cryptotrader.config import get_logger
    from cryptotrader.services.binance.websocketAPI.base_operations import (
        BinanceWebSocketConnection,
        SecurityType
    )
    from cryptotrader.services.binance.websocketAPI.market_data_requests.order_book import (
        get_order_book,
        process_order_book_response
    )
except ImportError as e:
    print(f"{Fore.RED}Import error: {str(e)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Make sure you're running this script from the project root directory{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Current sys.path: {sys.path}{Style.RESET_ALL}")
    sys.exit(1)

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing
TEST_INTERVAL = 30  # How long to run the test for in seconds

def print_test_header(test_name):
    """Print a test header in cyan color"""
    print(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")
    logger.info(f"Starting test: {test_name}")

def print_test_result(success, message=None):
    """Print a test result in green (success) or red (failure)"""
    if success:
        print(f"{Fore.GREEN}✓ Test passed{Style.RESET_ALL}")
        if message:
            print(f"  {message}")
        logger.info(f"Test passed: {message if message else ''}")
    else:
        print(f"{Fore.RED}✗ Test failed{Style.RESET_ALL}")
        if message:
            print(f"  {message}")
        logger.error(f"Test failed: {message if message else ''}")

class OrderBookTester:
    """Tests the Order Book WebSocket request functionality"""
    
    def __init__(self):
        """Initialize the Order Book tester"""
        self.connection = None
        self.messages_received = 0
        self.errors_received = 0
        self.test_results = {}
        self.last_message = None
        self.response_received = False
        self.running = True
        
    async def on_message(self, message):
        """Handle received messages"""
        self.messages_received += 1
        self.last_message = message
        self.response_received = True
        
        # Pretty print the message
        pretty_json = json.dumps(message, indent=2)
        logger.debug(f"Received message: {pretty_json}")
        print(f"{Fore.YELLOW}Received:{Style.RESET_ALL}")
        print(f"{pretty_json[:500]}...") if len(pretty_json) > 500 else print(pretty_json)
        
        # Check for errors
        if 'error' in message:
            self.errors_received += 1
            error = message['error']
            error_msg = f"Error received: {error.get('code', 'N/A')} - {error.get('msg', 'Unknown error')}"
            logger.error(error_msg)
            print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
    
    async def on_error(self, error):
        """Handle WebSocket errors"""
        self.errors_received += 1
        error_msg = f"WebSocket error: {str(error)}"
        logger.error(error_msg)
        print(f"{Fore.RED}{error_msg}{Style.RESET_ALL}")
        
    async def on_reconnect(self):
        """Handle WebSocket reconnection"""
        logger.info("WebSocket reconnected")
        print(f"{Fore.YELLOW}WebSocket reconnected{Style.RESET_ALL}")
        
    async def on_close(self):
        """Handle WebSocket closure"""
        logger.info("WebSocket closed")
        print(f"{Fore.YELLOW}WebSocket closed{Style.RESET_ALL}")
        
    async def setup(self):
        """Set up the WebSocket connection"""
        print_test_header("Setting up WebSocket connection")
        
        try:
            logger.info("Creating WebSocket connection")
            self.connection = BinanceWebSocketConnection(
                on_message=self.on_message,
                on_error=self.on_error,
                on_reconnect=self.on_reconnect,
                on_close=self.on_close,
                ping_interval=30,  # Use a shorter interval for testing
                pong_timeout=5     # Shorter timeout for testing
            )
            
            logger.info("Connecting to WebSocket...")
            success = await self.connection.connect()
            self.test_results["connection_setup"] = success
            print_test_result(success, "WebSocket connection established" if success else "Failed to establish connection")
            return success
        except Exception as e:
            error_msg = f"Error setting up connection: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["connection_setup"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_order_book_default(self):
        """Test order book with default parameters"""
        print_test_header("Testing order book with default parameters")
        
        try:
            # Reset response flag
            self.response_received = False
            
            logger.info(f"Getting order book for {TEST_SYMBOL} with default parameters")
            msg_id = await get_order_book(
                connection=self.connection,
                symbol=TEST_SYMBOL
            )
            logger.info(f"Sent order book request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.response_received and self.errors_received == 0
            self.test_results["order_book_default"] = success
            
            # Process response if received
            if self.last_message and 'result' in self.last_message:
                order_book = await process_order_book_response(self.last_message)
                if order_book:
                    print(f"  Received order book with {len(order_book.bids)} bids and {len(order_book.asks)} asks")
                    print(f"  Last update ID: {order_book.last_update_id}")
                    if order_book.bids and order_book.asks:
                        print(f"  Top bid: {order_book.bids[0].price} (qty: {order_book.bids[0].quantity})")
                        print(f"  Top ask: {order_book.asks[0].price} (qty: {order_book.asks[0].quantity})")
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return success
        except Exception as e:
            error_msg = f"Error testing order book with default parameters: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["order_book_default"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_order_book_with_limit(self):
        """Test order book with custom limit parameter"""
        print_test_header("Testing order book with custom limit")
        
        try:
            # Reset response flag
            self.response_received = False
            
            limit = 10  # Use a small limit for testing
            logger.info(f"Getting order book for {TEST_SYMBOL} with limit {limit}")
            msg_id = await get_order_book(
                connection=self.connection,
                symbol=TEST_SYMBOL,
                limit=limit
            )
            logger.info(f"Sent order book request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.response_received and self.errors_received == 0
            self.test_results["order_book_with_limit"] = success
            
            # Process response if received
            if self.last_message and 'result' in self.last_message:
                order_book = await process_order_book_response(self.last_message)
                if order_book:
                    # Verify the limit was applied
                    limit_correct = len(order_book.bids) <= limit and len(order_book.asks) <= limit
                    print(f"  Received order book with {len(order_book.bids)} bids and {len(order_book.asks)} asks")
                    print(f"  Limit of {limit} respected: {limit_correct}")
                    if order_book.bids and order_book.asks:
                        print(f"  Top bid: {order_book.bids[0].price} (qty: {order_book.bids[0].quantity})")
                        print(f"  Top ask: {order_book.asks[0].price} (qty: {order_book.asks[0].quantity})")
                    
                    # Update success based on limit check
                    success = success and limit_correct
                    self.test_results["order_book_with_limit"] = success
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return success
        except Exception as e:
            error_msg = f"Error testing order book with custom limit: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["order_book_with_limit"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_order_book_invalid_symbol(self):
        """Test order book with invalid symbol"""
        print_test_header("Testing order book with invalid symbol")
        
        try:
            # Reset response flag
            self.response_received = False
            
            invalid_symbol = "INVALID123"
            logger.info(f"Getting order book for invalid symbol {invalid_symbol}")
            msg_id = await get_order_book(
                connection=self.connection,
                symbol=invalid_symbol
            )
            logger.info(f"Sent order book request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            # We expect an error for invalid symbol
            received_error = 'error' in self.last_message if self.last_message else False
            self.test_results["order_book_invalid_symbol"] = self.response_received and received_error
            
            print_test_result(
                self.response_received and received_error,
                "Successfully received error response for invalid symbol" if received_error else "Did not receive expected error"
            )
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return self.response_received and received_error
        except Exception as e:
            error_msg = f"Error testing order book with invalid symbol: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["order_book_invalid_symbol"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_order_book_parameter_validation(self):
        """Test order book parameter validation"""
        print_test_header("Testing order book parameter validation")
        
        try:
            # Test with invalid limit (too high)
            invalid_limit = 10000  # Maximum allowed is 5000
            
            validation_error_caught = False
            try:
                await get_order_book(
                    connection=self.connection,
                    symbol=TEST_SYMBOL,
                    limit=invalid_limit
                )
            except ValueError as e:
                validation_error_caught = True
                print(f"  Correctly caught validation error: {str(e)}")
            
            # Test with empty symbol
            empty_symbol_error_caught = False
            try:
                await get_order_book(
                    connection=self.connection,
                    symbol=""
                )
            except ValueError as e:
                empty_symbol_error_caught = True
                print(f"  Correctly caught empty symbol error: {str(e)}")
            
            # Test with negative limit
            negative_limit_error_caught = False
            try:
                await get_order_book(
                    connection=self.connection,
                    symbol=TEST_SYMBOL,
                    limit=-10
                )
            except ValueError as e:
                negative_limit_error_caught = True
                print(f"  Correctly caught negative limit error: {str(e)}")
            
            success = validation_error_caught and empty_symbol_error_caught and negative_limit_error_caught
            self.test_results["order_book_parameter_validation"] = success
            
            print_test_result(success, "Parameter validation is working correctly")
            return success
        except Exception as e:
            error_msg = f"Error testing order book parameter validation: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["order_book_parameter_validation"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.connection:
            logger.info("Closing WebSocket connection")
            try:
                await self.connection.close()
                logger.info("WebSocket connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebSocket connection: {str(e)}")
                logger.error(traceback.format_exc())
    
    async def run_all_tests(self):
        """Run all order book tests sequentially"""
        try:
            if not await self.setup():
                logger.error("Setup failed, aborting tests")
                return
            
            await self.test_order_book_default()
            await self.test_order_book_with_limit()
            await self.test_order_book_invalid_symbol()
            await self.test_order_book_parameter_validation()
            
            # Print summary
            print("\n")
            print(f"{Fore.CYAN}Test Summary:{Style.RESET_ALL}")
            print("─" * 40)
            
            for test_name, result in self.test_results.items():
                test_desc = test_name.replace("_", " ").title()
                if result is True:
                    print(f"{Fore.GREEN}✓ {test_desc}: Passed{Style.RESET_ALL}")
                elif result is False:
                    print(f"{Fore.RED}✗ {test_desc}: Failed{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}○ {test_desc}: Skipped{Style.RESET_ALL}")
                    
            print("─" * 40)
            
            # Summary statistics
            total_tests = len(self.test_results)
            passed_tests = sum(1 for result in self.test_results.values() if result is True)
            failed_tests = sum(1 for result in self.test_results.values() if result is False)
            skipped_tests = sum(1 for result in self.test_results.values() if result is None)
            
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
            print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
            print(f"Skipped: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)")
            
            # Close the connection
            await self.close()
            
        except KeyboardInterrupt:
            logger.info("Tests interrupted by user")
            await self.close()
        except Exception as e:
            logger.error(f"Error during tests: {str(e)}")
            logger.error(traceback.format_exc())
            await self.close()

async def main():
    """Run the order book diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance Order Book WebSocket Request Diagnostic ===={Style.RESET_ALL}")
    print(f"Current date/time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print()
    
    try:
        # Create and run the tester
        tester = OrderBookTester()
        
        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(tester.close()))
            except NotImplementedError:
                # Windows doesn't support add_signal_handler
                pass
        
        await tester.run_all_tests()
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\n{Fore.RED}Error in diagnostic: {str(e)}{Style.RESET_ALL}")
        print(f"\n{Fore.RED}Traceback:{Style.RESET_ALL}")
        print(traceback.format_exc())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Diagnostic interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error in diagnostic: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()