#!/usr/bin/env python3
"""
Crypto.com API Diagnostic Script
--------------------------------
Tests the Crypto.com unified client to verify connectivity and data retrieval for all endpoints.
"""
import os
import sys
import traceback
from pathlib import Path
from colorama import init, Fore, Style
from cryptotrader.config import get_logger
from cryptotrader.services.unified_clients.cryptoRestUnifiedClient import CryptoRestUnifiedClient

# Initialize colorama
init(autoreset=True)
logger = get_logger(__name__)

# Test constants
test_instrument = os.getenv("CRYPTO_TEST_INSTRUMENT", "BTC_USDT")


def print_test_header(name: str):
    logger.info(f"\n{Fore.CYAN}=== {name} ==={Style.RESET_ALL}")


def main():
    # Add src/ to path for local imports
    project_root = Path(__file__).resolve().parents[5]
    sys.path.insert(0, str(project_root / "src"))

    logger.info("Initializing Crypto.com unified client...")
    client = CryptoRestUnifiedClient(testnet=True)

    # Test 1: Exchange Info
    print_test_header("Exchange Info")
    try:
        info = client.get_exchange_info()
        count = len(info.get("instruments", [])) if isinstance(info, dict) else None
        logger.info(f"Fetched instruments count: {count}")
    except Exception as e:
        logger.error(f"Error fetching exchange info: {e}")
        logger.debug(traceback.format_exc())

    # Test 2: 24h Ticker
    print_test_header("24h Ticker")
    try:
        ticker = client.get_ticker_24h(test_instrument)
        logger.info(f"Ticker data for {test_instrument}: {ticker}")
    except Exception as e:
        logger.error(f"Error fetching ticker: {e}")
        logger.debug(traceback.format_exc())

    # Test 3: Account Summary
    print_test_header("Account Summary")
    try:
        summary = client.get_account_summary()
        balances = summary.get("balances", summary)
        logger.info(f"Account balances: {balances}")
    except Exception as e:
        logger.error(f"Error fetching account summary: {e}")
        logger.debug(traceback.format_exc())

    # Test 4: Trade History
    print_test_header("Trade History")
    try:
        trades = client.get_my_trades(test_instrument)
        logger.info(f"Retrieved {len(trades)} trades for {test_instrument}")
    except Exception as e:
        logger.error(f"Error fetching trade history: {e}")
        logger.debug(traceback.format_exc())

    logger.info(f"{Fore.GREEN}Crypto.com API diagnostics completed.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
