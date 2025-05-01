"""
Binance REST Unified Client Diagnostic Script
---------------------------------------------
Tests the Binance REST Unified Client to verify functionality.

Usage:
    From the project root:
    python src/cryptotrader/services/binance/diagnostic_scripts/rest_unified_client_diagnostic.py
"""

# File: src/cryptotrader/services/binance/diagnostic_scripts/rest_unified_client_diagnostic.py

import sys
from pathlib import Path
import traceback
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

project_root = Path(__file__).parents[3]      # …/python_crypto_trader
src_folder   = project_root / "src"           # …/python_crypto_trader/src

# 1) so `import config` finds config.py in the project root
sys.path.insert(0, str(project_root))
# 2) so `import gui` and `import services` work from inside src/
sys.path.insert(0, str(src_folder))

from config import get_logger
from gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)

TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing

def print_test_header(test_name):
    print(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def print_success(message):
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_section_header(section_name):
    print(f"\n{Fore.MAGENTA}=== {section_name} ==={Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    logger.info("Initializing Binance REST Unified Client.")
    client = BinanceRestUnifiedClient()

    tests_run = 0
    tests_passed = 0

    # System API Tests
    print_section_header("System API Tests")

    # Test 1: Search Binance Symbols
    print_test_header("Search Binance Symbols")
    tests_run += 1
    try:
        symbol_provider = client.search_binance_symbols()
        symbols = symbol_provider() if callable(symbol_provider) else symbol_provider
        if symbols and TEST_SYMBOL in symbols:
            print_success(f"Found symbol {TEST_SYMBOL}")
            tests_passed += 1
        else:
            print_error(f"Symbol '{TEST_SYMBOL}' not found in symbols")
    except Exception as e:
        print_error(f"Error searching symbols: {e}")
        logger.debug(traceback.format_exc())

    # Test 2: 24h Ticker Price
    print_test_header("Get 24h Ticker Price")
    tests_run += 1
    try:
        stats = client.get_24h_ticker_price(TEST_SYMBOL)
        if stats:
            print_success(f"Fetched 24h ticker price for {TEST_SYMBOL}")
            tests_passed += 1
        else:
            print_error("No 24h ticker price returned")
    except Exception as e:
        print_error(f"Error fetching 24h ticker price: {e}")
        logger.debug(traceback.format_exc())

    # Order API Tests (Read-Only)
    print_section_header("Order API Tests")

    # Test 3: Get Open Orders
    print_test_header("Get Open Orders")
    tests_run += 1
    try:
        open_orders = client.get_open_orders(TEST_SYMBOL)
        if open_orders is not None:
            print_success(f"Fetched open orders ({len(open_orders)})")
            tests_passed += 1
        else:
            print_error("Failed to fetch open orders")
    except Exception as e:
        print_error(f"Error fetching open orders: {e}")
        logger.debug(traceback.format_exc())

    # Test 4: Get My Trades
    print_test_header("Get My Trades")
    tests_run += 1
    try:
        trades = client.get_my_trades(TEST_SYMBOL)
        if trades is not None:
            print_success(f"Fetched recent trades ({len(trades)})")
            tests_passed += 1
        else:
            print_error("Failed to fetch recent trades")
    except Exception as e:
        print_error(f"Error fetching recent trades: {e}")
        logger.debug(traceback.format_exc())

    # Diagnostic Summary
    print_section_header("Diagnostic Summary")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")

    if tests_passed < tests_run:
        print_error("Some tests failed. Check logs/API keys and endpoint availability.")

    logger.info("Diagnostic completed.")

if __name__ == "__main__":
    main()
