#!/usr/bin/env python3
"""
Binance WebSocket API Diagnostic Script
---------------------------------------
Tests the Binance WebSocket API client to verify functionality.

This script performs basic connectivity tests, checks ping/pong functionality,
tests various API methods, and verifies rate limit handling.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/binance_websocket_diagnostic.py
"""

import sys
import asyncio
import json
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta
import traceback
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from config import get_logger, Secrets
    from services.binance.websockets.base_operations import (
        BinanceWebSocketConnection,
        SecurityType
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

class BinanceWebSocketTester:
    """Tests the Binance WebSocket API client functionality"""
    
    def __init__(self):
        """Initialize the WebSocket tester"""
        self.connection = None
        self.messages_received = 0
        self.errors_received = 0
        self.test_results = {}
        self.last_ping_id = None
        self.ping_pong_received = False
        self.running = True
        self.rate_limits_received = False
        self.last_message = None
        
    async def on_message(self, message):
        """Handle received messages"""
        self.messages_received += 1
        self.last_message = message
        
        # Pretty print the message
        pretty_json = json.dumps(message, indent=2)
        logger.debug(f"Received message: {pretty_json}")
        print(f"{Fore.YELLOW}Received:{Style.RESET_ALL} {pretty_json[:200]}...")
        
        # Check for ping response
        if self.last_ping_id and 'id' in message and message['id'] == self.last_ping_id:
            if message.get('result', None) is not None:
                self.ping_pong_received = True
                logger.info("Ping response received")
        
        # Check for rate limits
        if 'rateLimits' in message and message['rateLimits']:
            self.rate_limits_received = True
            rate_limits = message['rateLimits']
            logger.info(f"Rate limits received: {json.dumps(rate_limits, indent=2)}")
            
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
                pong_timeout=5,    # Shorter timeout for testing
                reconnect_attempts=2
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
            
    async def test_ping(self):
        """Test the ping functionality"""
        print_test_header("Testing ping functionality")
        
        try:
            logger.info("Sending ping message")
            self.last_ping_id = await self.connection.send("ping")
            logger.info(f"Sent ping with ID: {self.last_ping_id}")
            
            # Wait for ping response
            for _ in range(10):  # Wait up to 5 seconds
                if self.ping_pong_received:
                    break
                await asyncio.sleep(0.5)
                
            success = self.ping_pong_received
            self.test_results["ping_test"] = success
            print_test_result(success, "Ping response received" if success else "No ping response received")
            return success
        except Exception as e:
            error_msg = f"Error testing ping: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["ping_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_server_time(self):
        """Test the server time API"""
        print_test_header("Testing server time API")
        
        try:
            logger.info("Sending server time request")
            msg_id = await self.connection.send("time")
            logger.info(f"Sent time request with ID: {msg_id}")
            
            # Wait a moment for the response
            await asyncio.sleep(2)
            
            success = self.messages_received > 0 and self.errors_received == 0
            self.test_results["server_time_test"] = success
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            if self.last_message and 'result' in self.last_message and 'serverTime' in self.last_message['result']:
                server_time = self.last_message['result']['serverTime']
                server_time_date = datetime.fromtimestamp(server_time / 1000)
                print(f"  Server time: {server_time_date}")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing server time: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["server_time_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_rate_limits(self):
        """Test rate limit information"""
        print_test_header("Testing rate limit information")
        
        try:
            # Reset flag
            self.rate_limits_received = False
            
            # Check if we've already received rate limits
            if self.rate_limits_received:
                self.test_results["rate_limits_test"] = True
                print_test_result(True, "Rate limits already received")
                return True
            
            # Make a request that should return rate limits
            logger.info("Sending exchangeInfo request")
            msg_id = await self.connection.send("exchangeInfo", {"symbols": [TEST_SYMBOL]}, return_rate_limits=True)
            logger.info(f"Sent exchangeInfo request with ID: {msg_id}")
            
            # Wait a moment for the response
            await asyncio.sleep(2)
            
            success = self.rate_limits_received
            self.test_results["rate_limits_test"] = success
            print_test_result(success, "Rate limits received" if success else "No rate limits received")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing rate limits: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["rate_limits_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_ticker_price(self):
        """Test ticker price API"""
        print_test_header("Testing ticker price API")
        
        try:
            logger.info("Sending ticker.price request")
            msg_id = await self.connection.send("ticker.price", {"symbol": TEST_SYMBOL})
            logger.info(f"Sent ticker.price request with ID: {msg_id}")
            
            # Wait a moment for the response
            await asyncio.sleep(2)
            
            success = self.messages_received > 0 and self.errors_received == 0
            self.test_results["ticker_price_test"] = success
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            if self.last_message and 'result' in self.last_message:
                price_data = self.last_message['result']
                if isinstance(price_data, dict) and 'price' in price_data:
                    print(f"  {TEST_SYMBOL} price: {price_data['price']}")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing ticker price: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["ticker_price_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_authenticated_request(self):
        """Test an authenticated request (if API keys are available)"""
        print_test_header("Testing authenticated request")
        
        # Check if API keys are available
        has_api_key = hasattr(Secrets, 'BINANCE_API_KEY') and bool(getattr(Secrets, 'BINANCE_API_KEY', None))
        has_api_secret = hasattr(Secrets, 'BINANCE_API_SECRET') and bool(getattr(Secrets, 'BINANCE_API_SECRET', None))
        
        if not has_api_key or not has_api_secret:
            logger.warning("No API keys available, skipping authenticated request test")
            self.test_results["authenticated_request_test"] = None
            print_test_result(True, "Test skipped - No API keys available")
            return None
        
        try:
            # Try to get account information (requires authentication)
            logger.info("Sending account.status request")
            msg_id = await self.connection.send("account.status", {}, SecurityType.USER_DATA)
            logger.info(f"Sent account.status request with ID: {msg_id}")
            
            # Wait a moment for the response
            await asyncio.sleep(2)
            
            success = self.messages_received > 0 and self.errors_received == 0
            self.test_results["authenticated_request_test"] = success
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing authenticated request: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.test_results["authenticated_request_test"] = False
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
        """Run all tests sequentially"""
        try:
            if not await self.setup():
                logger.error("Setup failed, aborting tests")
                return
            
            await self.test_ping()
            await self.test_server_time()
            await self.test_rate_limits()
            await self.test_ticker_price()
            await self.test_authenticated_request()
            
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
    """Run the WebSocket diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance WebSocket API Diagnostic ===={Style.RESET_ALL}")
    print(f"Current date/time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print()
    
    try:
        # Create and run the tester
        tester = BinanceWebSocketTester()
        
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