Binance WebSocket API Design Document
Overview
This document outlines the design and implementation patterns for the Binance WebSocket API client. The WebSocket API provides real-time data and trading capabilities with lower latency compared to REST API endpoints. This implementation complements the existing REST API client while following similar design principles.

Project Structure and Naming Conventions
src/cryptotrader/services/binance/websocketAPI/
├── __init__.py                        # Main package exports
├── base_operations.py                 # Core WebSocket functionality
├── market_stream.py                   # Market data streams (to be implemented)
├── user_stream.py                     # User data streams (to be implemented)
├── order_stream.py                    # Trading operations (to be implemented)
└── diagnostic_scripts/                # WebSocket testing scripts
    ├── binance_websocket_diagnostic.py     # Tests for base operations
    ├── market_stream_diagnostic.py         # Tests for market streams
    ├── user_stream_diagnostic.py           # Tests for user streams
    └── order_stream_diagnostic.py          # Tests for order streams
We follow these naming conventions:

Feature-specific implementations use the "_stream.py" suffix (e.g., market_stream.py, user_stream.py)
Each stream implementation has a corresponding diagnostic script with a "_diagnostic.py" suffix
Diagnostic scripts are stored in the diagnostic_scripts directory
Diagnostic Scripts
Each component of the WebSocket API should have a corresponding diagnostic script that tests its functionality. All diagnostic scripts should follow the design pattern established in binance_websocket_diagnostic.py, which serves as the reference implementation.

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
Binance [Feature] WebSocket Diagnostic Script
---------------------------------------------
Tests the Binance [Feature] WebSocket implementation to verify functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/[feature]_stream_diagnostic.py
"""

import sys
import asyncio
import json
import time
import signal
from pathlib import Path
import traceback
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI import [relevant_classes]

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

class [Feature]WebSocketTester:
    """Tests the [Feature] WebSocket functionality"""
    
    # Implementation goes here...

async def main():
    """Run the diagnostic tests"""
    logger.info(f"Added {project_root} to Python path")
    print(f"{Fore.CYAN}=== Binance [Feature] WebSocket Diagnostic ===={Style.RESET_ALL}")
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
