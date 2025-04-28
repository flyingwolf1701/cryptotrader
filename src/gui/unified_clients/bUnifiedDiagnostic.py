"""
Binance REST Unified Client Diagnostic Script
---------------------------------------
Tests the Binance REST Unified Client to verify functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/rest_unified_client_diagnostic.py
"""

import sys
from pathlib import Path
import traceback
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from config import get_logger
from services.binance.models import OrderSide, OrderType, TimeInForce
from gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)

# Test constants
TEST_SYMBOL = "BTCUSDT"  # Use a common trading pair for testing


def print_test_header(test_name):
    """Print a test header in cyan color"""
    print(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


def print_success(message):
    """Print a success message in green"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print an error message in red"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_info(message):
    """Print an info message in yellow"""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


def print_section_header(section_name):
    """Print a section header in magenta"""
    print(f"\n{Fore.MAGENTA}=== {section_name} ==={Style.RESET_ALL}")


def main():
    logger.info(f"Added {project_root} to Python path")

    logger.info("Initializing Binance REST Unified Client...")
    client = BinanceRestUnifiedClient()

    # Track test results
    tests_run = 0
    tests_passed = 0

    # Market API Tests
    print_section_header("Market API Tests")

    # Test 1: Get ticker price
    print_test_header("Get Ticker Price")
    tests_run += 1
    try:
        ticker = client.get_ticker_price(TEST_SYMBOL)
        if ticker and hasattr(ticker, "price"):
            print_success(f"Got ticker price for {TEST_SYMBOL}: {ticker.price}")
            tests_passed += 1
        else:
            print_error(f"Failed to get ticker price for {TEST_SYMBOL}")
    except Exception as e:
        print_error(f"Error getting ticker price: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 2: Get historical candles
    print_test_header("Get Historical Candles")
    tests_run += 1
    try:
        candles = client.get_historical_candles(TEST_SYMBOL, "1h", limit=10)
        if candles and len(candles) > 0:
            print_success(f"Got {len(candles)} candles for {TEST_SYMBOL}")
            # Print the first candle
            first_candle = candles[0]
            candle_time = datetime.fromtimestamp(first_candle.timestamp / 1000)
            print_info(
                f"First candle time: {candle_time}, Open: {first_candle.openPrice}, Close: {first_candle.closePrice}"
            )
            tests_passed += 1
        else:
            print_error(f"Failed to get candles for {TEST_SYMBOL}")
    except Exception as e:
        print_error(f"Error getting historical candles: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 3: Get order book
    print_test_header("Get Order Book")
    tests_run += 1
    try:
        order_book = client.get_order_book(TEST_SYMBOL, limit=5)
        if order_book and order_book.bids and order_book.asks:
            print_success(f"Got order book for {TEST_SYMBOL}")
            print_info(
                f"Best bid: {order_book.bids[0].price}, Best ask: {order_book.asks[0].price}"
            )
            tests_passed += 1
        else:
            print_error(f"Failed to get order book for {TEST_SYMBOL}")
    except Exception as e:
        print_error(f"Error getting order book: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 4: Get recent trades
    print_test_header("Get Recent Trades")
    tests_run += 1
    try:
        trades = client.get_recent_trades(TEST_SYMBOL, limit=5)
        if trades and len(trades) > 0:
            print_success(f"Got {len(trades)} recent trades for {TEST_SYMBOL}")
            # Print the most recent trade
            latest_trade = trades[0]
            trade_time = datetime.fromtimestamp(latest_trade.time / 1000)
            print_info(
                f"Latest trade time: {trade_time}, Price: {latest_trade.price}, Quantity: {latest_trade.qty}"
            )
            tests_passed += 1
        else:
            print_error(f"Failed to get recent trades for {TEST_SYMBOL}")
    except Exception as e:
        print_error(f"Error getting recent trades: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 5: Get 24h stats
    print_test_header("Get 24h Stats")
    tests_run += 1
    try:
        stats = client.get_24h_stats(TEST_SYMBOL)
        if stats:
            print_success(f"Got 24h stats for {TEST_SYMBOL}")
            print_info(
                f"Price change: {stats.priceChange}, High: {stats.highPrice}, Low: {stats.lowPrice}"
            )
            tests_passed += 1
        else:
            print_error(f"Failed to get 24h stats for {TEST_SYMBOL}")
    except Exception as e:
        print_error(f"Error getting 24h stats: {str(e)}")
        logger.debug(traceback.format_exc())

    # User API Tests
    print_section_header("User API Tests")

    # Test 6: Get Account (Authentication required)
    print_test_header("Get Account")
    tests_run += 1
    try:
        account = client.getAccountRest()
        if account and hasattr(account, "balances"):
            print_success("Got account information")
            # Print a few balances with non-zero values
            non_zero_balances = {
                asset: data
                for asset, data in account.balances.items()
                if float(data.free) > 0 or float(data.locked) > 0
            }
            if non_zero_balances:
                print_info(
                    f"Found {len(non_zero_balances)} assets with non-zero balance"
                )
                # Print the first 3
                for i, (asset, data) in enumerate(list(non_zero_balances.items())[:3]):
                    print_info(f"{asset}: Free={data.free}, Locked={data.locked}")
            else:
                print_info("No assets with non-zero balance found")
            tests_passed += 1
        else:
            print_info(
                "Failed to get account information (may need API key with permissions)"
            )
    except Exception as e:
        print_info(
            f"Error getting account info: {str(e)} (may need API key with permissions)"
        )
        logger.debug(traceback.format_exc())

    # Order API Tests (read-only)
    print_section_header("Order API Tests (Read-Only)")

    # Test 7: Get Open Orders (Authentication required)
    print_test_header("Get Open Orders")
    tests_run += 1
    try:
        open_orders = client.get_open_orders(TEST_SYMBOL)
        if open_orders is not None:  # Could be empty list if no open orders
            print_success(f"Fetched open orders for {TEST_SYMBOL}")
            print_info(f"Number of open orders: {len(open_orders)}")
            tests_passed += 1
        else:
            print_info("Failed to get open orders (may need API key with permissions)")
    except Exception as e:
        print_info(
            f"Error getting open orders: {str(e)} (may need API key with permissions)"
        )
        logger.debug(traceback.format_exc())

    # Wallet API Tests
    print_section_header("Wallet API Tests (Read-Only)")

    # Test 8: Get Asset Details (Authentication required)
    print_test_header("Get Asset Details")
    tests_run += 1
    try:
        assets = client.getAssetDetails()
        if assets and len(assets) > 0:
            print_success(f"Got details for {len(assets)} assets")
            # Print a few well-known assets
            for asset_name in ["BTC", "ETH", "BNB"]:
                for asset in assets:
                    if asset.coin == asset_name:
                        print_info(
                            f"{asset_name}: Withdraw Enabled: {asset.withdrawAllEnable}, Deposit Enabled: {asset.depositAllEnable}"
                        )
                        break
            tests_passed += 1
        else:
            print_info(
                "Failed to get asset details (may need API key with permissions)"
            )
    except Exception as e:
        print_info(
            f"Error getting asset details: {str(e)} (may need API key with permissions)"
        )
        logger.debug(traceback.format_exc())

    # Summary
    print_section_header("Diagnostic Summary")
    print(f"Tests run: {tests_run}")
    print(f"Tests passed: {tests_passed}")

    if tests_passed < tests_run:
        print_info(
            "Note: Some tests may have failed due to missing API keys or permissions."
        )
        print_info(
            "For authenticated endpoints, make sure your API keys are set in the Secrets configuration."
        )

    logger.info("\nDiagnostic completed.")


if __name__ == "__main__":
    main()
