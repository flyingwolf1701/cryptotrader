#!/usr/bin/env python3
"""
Binance Historical Trades WebSocket Request Diagnostic Script
------------------------------------------------------------
Tests the Binance Historical Trades WebSocket request to verify functionality.

This script focuses on testing the historical_trades.py implementation, which provides
functionality to retrieve historical trades data for a trading symbol
using the Binance WebSocket API.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/historical_trades_diagnostic.py
"""

import sys
import asyncio
import json
import time
import signal
from pathlib import Path
import traceback
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from cryptotrader.config import get_logger, Secrets
    from cryptotrader.services.binance.websocketAPI.base_operations import (
        BinanceWebSocketConnection,
        SecurityType
    )
    from cryptotrader.services.binance.websocketAPI.market_data_requests.historical_trades import (
        get_historical_trades,
        process_historical_trades_response
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

class HistoricalTradesTester:
    """Tests the Historical Trades WebSocket request functionality"""
    
    def __init__(self):
        """Initialize the Historical Trades tester"""
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
    
    async def test_api_key_availability(self):
        """Test if API key is available for authentication"""
        print_test_header("Testing API key availability")
        
        # Historical trades requires API key (MARKET_DATA security type)
        has_api_key = hasattr(Secrets, 'BINANCE_API_KEY') and bool(getattr(Secrets, 'BINANCE_API_KEY', None))
        
        if not has_api_key:
            logger.warning("No API key available, historical trades test will likely fail")
            print(f"{Fore.YELLOW}Warning: No API key available. Historical trades endpoint requires authentication.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Make sure BINANCE_API_KEY is set in your Secrets configuration.{Style.RESET_ALL}")
            
        self.test_results["api_key_availability"] = has_api_key
        print_test_result(has_api_key, "API key is available" if has_api_key else "API key is not available")
        return has_api_key
    
    async def test_historical_trades_default(self):
        """Test historical trades with default parameters"""
        print_test_header("Testing historical trades with default parameters")
        
        try:
            # Reset response flag
            self.response_received = False
            
            logger.info(f"Getting historical trades for {TEST_SYMBOL} with default parameters")
            msg_id = await get_historical_trades(
                connection=self.connection,
                symbol=TEST_SYMBOL
            )
            logger.info(f"Sent historical trades request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.response_received and self.errors_received == 0
            self.test_results["historical_trades_default"] = success
            
            # Process response if received
            if success and self.last_message and 'result' in self.last_message:
                trades = await process_historical_trades_response(self.last_message)
                if trades:
                    print(f"  Received {len(trades)} historical trades")
                    if trades:
                        # Display information about the first few trades
                        sample_size = min(3, len(trades))
                        for i in range(sample_size):
                            trade = trades[i]
                            print(f"  Trade {i+1}: ID={trade.id}, Price={trade.price}, Quantity={trade.quantity}, Time={datetime.fromtimestamp(trade.time/1000)}")
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return success
        except Exception as e:
            error_msg = f"Error testing historical trades with default parameters: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["historical_trades_default"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_historical_trades_with_limit(self):
        """Test historical trades with custom limit parameter"""
        print_test_header("Testing historical trades with custom limit")
        
        try:
            # Reset response flag
            self.response_received = False
            
            limit = 5  # Use a small limit for testing
            logger.info(f"Getting historical trades for {TEST_SYMBOL} with limit {limit}")
            msg_id = await get_historical_trades(
                connection=self.connection,
                symbol=TEST_SYMBOL,
                limit=limit
            )
            logger.info(f"Sent historical trades request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.response_received and self.errors_received == 0
            self.test_results["historical_trades_with_limit"] = success
            
            # Process response if received
            if success and self.last_message and 'result' in self.last_message:
                trades = await process_historical_trades_response(self.last_message)
                if trades:
                    # Verify the limit was applied
                    limit_correct = len(trades) <= limit
                    print(f"  Received {len(trades)} historical trades")
                    print(f"  Limit of {limit} respected: {limit_correct}")
                    
                    if trades:
                        # Display information about all trades (since limit is small)
                        for i, trade in enumerate(trades):
                            print(f"  Trade {i+1}: ID={trade.id}, Price={trade.price}, Quantity={trade.quantity}, Time={datetime.fromtimestamp(trade.time/1000)}")
                    
                    # Update success based on limit check
                    success = success and limit_correct
                    self.test_results["historical_trades_with_limit"] = success
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return success
        except Exception as e:
            error_msg = f"Error testing historical trades with custom limit: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["historical_trades_with_limit"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_historical_trades_with_from_id(self):
        """Test historical trades with from_id parameter"""
        print_test_header("Testing historical trades with from_id parameter")
        
        try:
            # First, get some trades to find a valid trade ID
            self.response_received = False
            logger.info(f"Getting initial historical trades to find a valid trade ID")
            await get_historical_trades(
                connection=self.connection,
                symbol=TEST_SYMBOL,
                limit=10
            )
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
            
            if not self.response_received or 'result' not in self.last_message:
                logger.warning("Could not get initial trades to find a valid trade ID")
                self.test_results["historical_trades_with_from_id"] = False
                print_test_result(False, "Could not get initial trades to find a valid trade ID")
                return False
            
            # Process the response to get a valid trade ID
            initial_trades = await process_historical_trades_response(self.last_message)
            if not initial_trades:
                logger.warning("No trades found in initial response")
                self.test_results["historical_trades_with_from_id"] = False
                print_test_result(False, "No trades found in initial response")
                return False
            
            # Use the first trade ID as from_id
            from_id = initial_trades[0].id
            logger.info(f"Using trade ID {from_id} as from_id parameter")
            
            # Reset for the actual test
            self.response_received = False
            self.last_message = None
            
            # Now test with from_id
            logger.info(f"Getting historical trades for {TEST_SYMBOL} with from_id {from_id}")
            msg_id = await get_historical_trades(
                connection=self.connection,
                symbol=TEST_SYMBOL,
                from_id=from_id,
                limit=5
            )
            logger.info(f"Sent historical trades request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.response_received and self.errors_received == 0
            self.test_results["historical_trades_with_from_id"] = success
            
            # Process response if received
            if success and self.last_message and 'result' in self.last_message:
                trades = await process_historical_trades_response(self.last_message)
                if trades:
                    print(f"  Received {len(trades)} historical trades starting from ID {from_id}")
                    
                    # Verify the from_id was respected
                    from_id_correct = all(trade.id >= from_id for trade in trades)
                    print(f"  from_id of {from_id} respected: {from_id_correct}")
                    
                    if trades:
                        # Display information about the first few trades
                        sample_size = min(3, len(trades))
                        for i in range(sample_size):
                            trade = trades[i]
                            print(f"  Trade {i+1}: ID={trade.id}, Price={trade.price}, Quantity={trade.quantity}, Time={datetime.fromtimestamp(trade.time/1000)}")
                    
                    # Update success based on from_id check
                    success = success and from_id_correct
                    self.test_results["historical_trades_with_from_id"] = success
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            self.response_received = False
            
            return success
        except Exception as e:
            error_msg = f"Error testing historical trades with from_id: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["historical_trades_with_from_id"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_historical_trades_invalid_symbol(self):
        """Test historical trades with invalid symbol"""
        print_test_header("Testing historical trades with invalid symbol")
        
        try:
            # Reset response flag
            self.response_received = False
            
            invalid_symbol = "INVALID123"
            logger.info(f"Getting historical trades for invalid symbol {invalid_symbol}")
            msg_id = await get_historical_trades(
                connection=self.connection,
                symbol=invalid_symbol
            )
            logger.info(f"Sent historical trades request with ID: {msg_id}")
            
            # Wait for response
            for _ in range(10):  # Wait up to 5 seconds
                if self.response_received:
                    break
                await asyncio.sleep(0.5)
                
            # We expect an error for invalid symbol
            received_error = 'error' in self.last_message if self.last_message else False
            self.test_results["historical_trades_invalid_symbol"] = self.response_received and received_error
            
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
            error_msg = f"Error testing historical trades with invalid symbol: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["historical_trades_invalid_symbol"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_historical_trades_parameter_validation(self):
        """Test historical trades parameter validation"""
        print_test_header("Testing historical trades parameter validation")
        
        try:
            # Test with invalid limit (too high)
            invalid_limit = 10000  # Maximum allowed is 1000
            
            validation_error_caught = False
            try:
                await get_historical_trades(
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
                await get_historical_trades(
                    connection=self.connection,
                    symbol=""
                )
            except ValueError as e:
                empty_symbol_error_caught = True
                print(f"  Correctly caught empty symbol error: {str(e)}")
            
            # Test with negative from_id
            negative_from_id_error_caught = False
            try:
                await get_historical_trades(
                    connection=self.connection,
                    symbol=TEST_SYMBOL,
                    from_id=-10
                )
            except ValueError as e:
                negative_from_id_error_caught = True
                print(f"  Correctly caught negative from_id error: {str(e)}")
            
            # Test with negative limit
            negative_limit_error_caught = False
            try:
                await get_historical_trades(
                    connection=self.connection,
                    symbol=TEST_SYMBOL,
                    limit=-10
                )
            except ValueError as e:
                negative_limit_error_caught = True
                print(f"  Correctly caught negative limit error: {str(e)}")
            
            success = validation_error_caught and empty_symbol_error_caught and negative_from_id_error_caught and negative_limit_error_caught
            self.test_results["historical_trades_parameter_validation"] = success
            
            print_test_result(success, "Parameter validation is working correctly")
            return success
        except Exception as e:
            error_msg = f"Error testing historical trades parameter validation: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["historical_trades_parameter_validation"] = False
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
        """Run all historical trades tests sequentially"""
        try:
            if not await self.setup():
                logger.error("Setup failed, aborting tests")
                return
            
            # Check API key availability first (historical_trades needs it)
            api_key_available = await self.test_api_key_availability()
            
            if api_key_available:
                await self.test_historical_trades_default()
                await self.test_historical_trades_with_limit()
                await self.test_historical_trades_with_from_id()
                await self.test_historical_trades_invalid_symbol()
            else:
                logger.warning("Skipping historical trades tests due to missing API key")
                self.test_results["historical_trades_default"] = None
                self.test_results["historical_trades_with_limit"] = None
                self.test_results["historical_trades_with_from_id"] = None
                self.test_results["historical_trades_invalid_symbol"] = None
            
            # Run parameter validation tests regardless of API key
            await self.test_historical_trades_parameter_validation()
            
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
    """Run the historical trades diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance Historical Trades WebSocket Request Diagnostic ===={Style.RESET_ALL}")
    print(f"Current date/time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print()
    
    try:
        # Create and run the tester
        tester = HistoricalTradesTester()
        
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