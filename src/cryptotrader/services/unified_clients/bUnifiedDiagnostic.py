"""
Binance REST Unified Client Diagnostic Script
---------------------------------------------
Tests the Binance REST Unified Client to verify functionality.

Usage:
    # As a module (after installation/editable install):
    python -m cryptotrader.services.binance.diagnostic_scripts.rest_unified_client_diagnostic

    # Or via console script (if configured):
    rest-unified-client-diagnostic
"""

import traceback
from colorama import Fore, Style, init
from cryptotrader.config import get_logger
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

# Initialize colorama for colored console output
init(autoreset=True)
logger = get_logger(__name__)

TEST_SYMBOL = "BTCUSDT"  # Common trading pair for testing


def print_test_header(test_name: str) -> None:
    print(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_section_header(section_name: str) -> None:
    print(f"\n{Fore.MAGENTA}=== {section_name} ==={Style.RESET_ALL}")


def main() -> None:
    logger.info("Initializing Binance REST Unified Client for diagnostics.")
    client = BinanceRestUnifiedClient()

    tests_run = 0
    tests_passed = 0

    # System API Tests
    print_section_header("System API Tests")

    # Test 1: Fetch Binance Symbols
    print_test_header("Fetch Binance Symbols")
    tests_run += 1
    try:
        symbols = client.get_binance_symbols()
        if TEST_SYMBOL in symbols:
            print_success(f"Found symbol {TEST_SYMBOL}")
            tests_passed += 1
        else:
            print_error(f"Symbol '{TEST_SYMBOL}' not found in symbol list.")
    except Exception as e:
        print_error(f"Error fetching symbol list: {e}")
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
            print_error("No 24h ticker data returned.")
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
            print_error("No open orders returned.")
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
            print_error("No trade data returned.")
    except Exception as e:
        print_error(f"Error fetching recent trades: {e}")
        logger.debug(traceback.format_exc())

    # Diagnostic Summary
    print_section_header("Diagnostic Summary")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")

    if tests_passed < tests_run:
        print_error("Some tests failed. Check API keys and endpoint availability.")

    logger.info("Diagnostic completed.")


if __name__ == "__main__":
    main()
