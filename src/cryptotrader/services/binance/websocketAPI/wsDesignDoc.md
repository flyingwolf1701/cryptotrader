Binance WebSocket API Design Document
Overview
This document outlines the design and implementation patterns for the Binance WebSocket API client. The WebSocket API provides real-time data and trading operations with lower latency compared to REST API endpoints. This implementation complements the existing REST API client while following similar design principles.

Project Structure and Naming Conventions
src/cryptotrader/services/binance/websocketAPI/
├── __init__.py                                    # Main package exports
├── base_operations.py                             # Core WebSocket functionality
├── account_requests/                              # Account data operations
│   ├── __init__.py                                # Package exports
│   ├── acct_oco_history.py                        # OCO order history requests
│   ├── acct_order_history.py                      # Order history requests
│   ├── acct_prevented_matches.py                  # Self-trade prevention matches
│   ├── acct_trade_history.py                      # Trade history requests
│   ├── get_order_rate_limits.py                   # Order rate limit requests
│   └── get_user_acct_info.py                      # Account information requests
├── market_data_requests/                          # Market data operations
│   ├── __init__.py                                # Package exports
│   ├── aggregate_trades.py                        # Aggregate trade requests
│   ├── current_average_price.py                   # Average price requests
│   ├── historical_trades.py                       # Historical trade requests
│   ├── klines.py                                  # Kline/candlestick requests
│   ├── order_book.py                              # Order book requests
│   ├── recent_trades.py                           # Recent trade requests
│   ├── rolling_window_price.py                    # Rolling window price stats
│   ├── symbol_order_book_ticker.py                # Order book ticker requests
│   ├── symbol_price_ticker.py                     # Symbol price ticker requests
│   └── ticker_price_24h.py                        # 24h price statistics requests
├── trading_requests/                              # Trading operations
│   ├── __init__.py                                # Package exports
│   ├── cancel_oco_order.py                        # Cancel OCO order requests
│   ├── cancel_open_orders.py                      # Cancel open orders requests
│   ├── cancel_order.py                            # Cancel order requests
│   ├── create_new_oco_order.py                    # Create OCO order requests
│   ├── current_open_orders.py                     # Get open orders requests
│   ├── get_oco_order.py                           # Get OCO order details
│   ├── get_open_oco_orders.py                     # Get open OCO orders requests
│   ├── place_new_order.py                         # Place order requests
│   ├── query_order.py                             # Query order details requests
│   ├── replace_order.py                           # Replace order requests
│   └── test_new_order.py                          # Test order placement requests
├── user_data_stream_requests/                     # User data stream operations
│   ├── __init__.py                                # Package exports
│   ├── ping_user_data_stream.py                   # Ping user data stream requests
│   ├── start_user_data_stream.py                  # Start user data stream requests
│   └── stop_user_data_stream.py                   # Stop user data stream requests
└── diagnostic_scripts/                            # WebSocket testing scripts parent directory
    ├── account_diagnostics/                       # Diagnostic scripts for account requests
    │   └── account_requests_diagnostic.py         # Tests for account requests
    ├── market_diagnostics/                        # Diagnostic scripts for market data requests
    │   └── order_book_diagnostic.py               # Tests for order book requests
    ├── trading_diagnostics/                       # Diagnostic scripts for trading requests
    │   └── trading_requests_diagnostic.py         # Tests for trading requests
    ├── user_stream_diagnostics/                   # Diagnostic scripts for user data stream
    │   └── user_data_stream_requests_diagnostic.py # Tests for user data stream
    └── binance_websocket_diagnostic.py            # Tests for base operations
We follow these naming conventions:

Request-specific implementations use the Binance API method names as closely as possible (e.g., get_user_acct_info.py, place_new_order.py)
Requests are organized by functional category in dedicated directories (e.g., account_requests, market_data_requests)
Each request category has a corresponding diagnostic script subdirectory that matches the module structure with a slightly different naming pattern:
account_requests → account_diagnostics
market_data_requests → market_diagnostics
trading_requests → trading_diagnostics
user_data_stream_requests → user_stream_diagnostics
Diagnostic scripts are stored in the diagnostic_scripts directory with subdirectories as outlined above
Each diagnostic script follows the pattern *_diagnostic.py
Request Implementation Pattern
When implementing a new WebSocket API request, follow this pattern:

python
"""
Binance WebSocket API [Method Name] Request

This module provides functionality to [brief description of what the request does].
It follows the Binance WebSocket API specifications for the [endpoint name] endpoint.
"""

import json
from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import [relevant_models]

logger = get_logger(__name__)

async def process_request(
    connection: BinanceWebSocketConnection,
    params: Dict[str, Any],
    callback: Callable[[Dict[str, Any]], Awaitable[None]]
) -> str:
    """
    Process a [method name] request.
    
    [Brief description of what this method does]
    
    Endpoint: [endpoint path]
    Method: [method name]
    Weight: [request weight]
    Security Type: [security type]
    
    Args:
        connection: Active WebSocket connection
        params: Request parameters
        callback: Callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters are missing
    """
    # Validate required parameters
    if 'required_param' not in params:
        raise ValueError("Missing required parameter: required_param")
        
    # Send the request
    msg_id = await connection.send(
        method="[method_name]",
        params=params,
        security_type=SecurityType.[SECURITY_TYPE]
    )
    
    return msg_id
Diagnostic Scripts
Each component of the WebSocket API should have a corresponding diagnostic script that tests its functionality. Diagnostic scripts are now organized in a directory structure that mirrors the main WebSocket API modules but with slightly different naming, making it easier to locate and maintain them.

Diagnostic Script Organization
The diagnostic_scripts directory contains subdirectories that correspond to the main module structure with adjusted naming:

account_diagnostics/ - Diagnostic scripts for account-related operations
market_diagnostics/ - Diagnostic scripts for market data operations
trading_diagnostics/ - Diagnostic scripts for trading operations
user_stream_diagnostics/ - Diagnostic scripts for user data stream operations
The main binance_websocket_diagnostic.py script serves as a reference implementation for testing the core WebSocket functionality.

Diagnostic Script Pattern
All diagnostic scripts should follow the design pattern established in binance_websocket_diagnostic.py, which serves as the reference implementation.

Key characteristics of the diagnostic scripts:

Comprehensive Testing: Test all major functionality in the corresponding module
Colorful Output: Use colorama for clear, color-coded test results
Graceful Error Handling: Wrap tests in try/except blocks for robustness
Isolated Tests: Each test function should be independent
Summary Reporting: Provide a clear summary of all test results at the end
Clean Project Path Management: Add the project root to Python path
Signal Handling: Properly handle interruption signals
Connection Management: Ensure connections are properly closed after tests
Example of the diagnostic script structure:

python
#!/usr/bin/env python3
"""
Binance [Category] WebSocket Requests Diagnostic Script
---------------------------------------------
Tests the Binance [Category] WebSocket requests to verify functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/websocketAPI/diagnostic_scripts/[category]_diagnostics/[specific]_diagnostic.py
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
from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.websocketAPI.[category]_requests import [relevant_modules]

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"

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

class [Category]RequestsTester:
    """Tests the [Category] WebSocket requests functionality"""
    
    # Implementation goes here...

async def main():
    """Run the diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance [Category] WebSocket Requests Diagnostic ===={Style.RESET_ALL}")
    print(f"Current date/time: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Project root: {project_root}")
    print()
    
    # Create and run tests here...

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Diagnostic interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error in diagnostic: {str(e)}{Style.RESET_ALL}")
        traceback.print_exc()
Authentication and Security Types
The WebSocket API uses different security types based on the endpoint:

SecurityType.NONE: Public market data endpoints that require no authentication
SecurityType.TRADE: Trading endpoints that require API key and signature
SecurityType.USER_DATA: User account endpoints that require API key and signature
SecurityType.USER_STREAM: User data stream endpoints that require API key only
SecurityType.MARKET_DATA: Historical market data endpoints that require API key only
Authentication is handled by the BinanceWebSocketConnection class based on the security type. For signed requests (TRADE and USER_DATA), a timestamp and signature are automatically added to the request parameters.

Request Categories
Market Data Requests
These requests provide market information such as prices, trades, order books, and statistics.

Account Requests
These requests provide information about the user's account, orders, trades, and balances.

Trading Requests
These requests allow placing, canceling, and modifying orders.

User Data Stream Requests
These requests manage the user data stream for receiving real-time account updates.

Response Handling
All WebSocket responses are handled via callback functions. The response for a specific request can be tied to a message ID, allowing for request-response correlation.

Error Handling
Error handling should follow these principles:

All errors should be logged with appropriate severity levels
Network-related errors should trigger reconnection logic
API errors should be parsed and handled based on error codes
Rate limiting and IP bans should be respected with appropriate waiting periods
Reconnection Strategy
The BinanceWebSocketConnection class implements a reconnection strategy with exponential backoff. When implementing request handlers, be mindful of the connection state and handle reconnection gracefully.

Implementation Process for New Requests
Identify the Binance API endpoint and method name
Determine the security type required for the endpoint
Review request parameters and response format
Create the request handler module in the appropriate directory
Create a corresponding diagnostic script in the diagnostic_scripts subdirectory that mirrors the module structure
Update the diagnostic scripts to test the new functionality
Add any new models required for request/response handling
Update the init.py file to export the new functionality
DO NOT add classes or functions to an init.py
