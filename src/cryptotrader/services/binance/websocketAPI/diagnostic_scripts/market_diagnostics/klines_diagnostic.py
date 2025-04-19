#!/usr/bin/env python3
"""
Binance WebSocket Klines Diagnostic Script
-----------------------------------------
Tests the Binance WebSocket API klines functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/market_diagnostics/klines_diagnostic.py
"""

import sys
import asyncio
import json
from datetime import datetime
import traceback
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection
from cryptotrader.services.binance.websocketAPI.market_data_requests.klines import get_klines, process_klines_response

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing

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

class KlinesRequestTester:
    """Tests the klines WebSocket request functionality"""
    
    def __init__(self):
        """Initialize the WebSocket tester"""
        self.connection = None
        self.messages_received = 0
        self.errors_received = 0
        self.test_results = {}
        self.last_message = None
        
    async def on_message(self, message):
        """Handle received messages"""
        self.messages_received += 1
        self.last_message = message
        
        # Pretty print the message
        pretty_json = json.dumps(message, indent=2)
        logger.debug(f"Received message: {pretty_json}")
        print(f"{Fore.YELLOW}Received:{Style.RESET_ALL} {pretty_json[:200]}...")
    
    async def on_error(self, error):
        """Handle WebSocket errors"""
        self.errors_received += 1
        logger.error(f"WebSocket error: {str(error)}")
        print(f"{Fore.RED}WebSocket error: {str(error)}{Style.RESET_ALL}")
        
    async def setup(self):
        """Set up the WebSocket connection"""
        print_test_header("Setting up WebSocket connection")
        
        try:
            self.connection = BinanceWebSocketConnection(
                on_message=self.on_message,
                on_error=self.on_error
            )
            
            success = await self.connection.connect()
            self.test_results["connection_setup"] = success
            print_test_result(success, "WebSocket connection established" if success else "Failed to connect")
            return success
        except Exception as e:
            logger.error(f"Error setting up connection: {str(e)}")
            self.test_results["connection_setup"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
            
    async def test_klines(self):
        """Test the klines functionality"""
        print_test_header("Testing klines API")
        
        try:
            # Test getting klines for a symbol
            symbol = TEST_SYMBOL
            interval = "1h"
            limit = 5
            
            logger.info(f"Requesting klines for {symbol}, interval {interval}, limit {limit}")
            await get_klines(
                self.connection,
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            # Wait for the response
            await asyncio.sleep(2)
            
            # Check if we received a response
            success = self.messages_received > 0 and self.errors_received == 0
            self.test_results["klines_test"] = success
            
            if success and self.last_message and 'result' in self.last_message:
                klines_data = self.last_message['result']
                if klines_data and len(klines_data) > 0:
                    print(f"  Received {len(klines_data)} klines")
                    # Show sample of first kline
                    if klines_data[0]:
                        sample = klines_data[0]
                        open_time = datetime.fromtimestamp(sample[0] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        print(f"  Sample: Open time={open_time}, O={sample[1]}, H={sample[2]}, L={sample[3]}, C={sample[4]}")
                    
                    # Process into Candle objects
                    candles = await process_klines_response(self.last_message)
                    if candles:
                        print(f"  Successfully processed {len(candles)} candles")
                    else:
                        print(f"  Failed to process candles from response")
                else:
                    print(f"  No klines data received")
            
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing klines: {str(e)}"
            logger.error(error_msg)
            self.test_results["klines_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def test_klines_with_timeframe(self):
        """Test the klines functionality with timeframe parameters"""
        print_test_header("Testing klines API with timeframe")
        
        try:
            # Get klines with start and end time (last 24 hours)
            symbol = TEST_SYMBOL
            interval = "15m"
            current_time = int(datetime.now().timestamp() * 1000)
            start_time = current_time - (24 * 60 * 60 * 1000)  # 24 hours ago
            limit = 10
            
            logger.info(f"Requesting klines for {symbol} with timeframe, interval {interval}")
            await get_klines(
                self.connection,
                symbol=symbol,
                interval=interval,
                start_time=start_time,
                limit=limit
            )
            
            # Wait for the response
            await asyncio.sleep(2)
            
            success = self.messages_received > 0 and self.errors_received == 0
            self.test_results["klines_timeframe_test"] = success
            print_test_result(success, f"Received {self.messages_received} messages, {self.errors_received} errors")
            
            # Reset counters for next test
            self.messages_received = 0
            self.errors_received = 0
            self.last_message = None
            
            return success
        except Exception as e:
            error_msg = f"Error testing klines with timeframe: {str(e)}"
            logger.error(error_msg)
            self.test_results["klines_timeframe_test"] = False
            print_test_result(False, f"Exception: {str(e)}")
            return False
    
    async def close(self):
        """Close the WebSocket connection"""
        if self.connection:
            await self.connection.close()
    
    async def run_all_tests(self):
        """Run all tests sequentially"""
        try:
            if not await self.setup():
                return
            
            await self.test_klines()
            await self.test_klines_with_timeframe()
            
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
            
        finally:
            await self.close()

async def main():
    """Run the WebSocket diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance WebSocket Klines Diagnostic ===={Style.RESET_ALL}")
    print(f"Current date/time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Debug project path
    print(f"Project root path: {project_root}")
    print(f"Script location: {Path(__file__)}")
    
    tester = KlinesRequestTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Diagnostic interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error in diagnostic: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()