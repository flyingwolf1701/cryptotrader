#!/usr/bin/env python
"""
Binance API Test Script
-----------------------
Tests the Binance API client to verify connectivity and data retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/binance_test_script.py

Note:
    This script was previously located at src/cryptotrader/binance_test_script.py
    and has been moved to the current location under the test_scripts directory.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Config
from cryptotrader.services.binance import Client

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    # Get API credentials from Config 
    api_key = Config.BINANCE_API_KEY
    api_secret = Config.BINANCE_API_SECRET
    
    logger.info(f"API Key loaded: {'Yes' if api_key else 'No'}")
    logger.info(f"API Secret loaded: {'Yes' if api_secret else 'No'}")
    
    if not api_key or not api_secret:
        logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file")
        return
    
    logger.info("Initializing Binance client...")
    client = Client(api_key, api_secret)
    
    # Test 1: Get available symbols
    logger.info("Test 1: Getting available symbols...")
    symbols = Client.get_symbols_binance()
    logger.info(f"Retrieved {len(symbols)} symbols")
    logger.info(f"First 5 symbols: {symbols[:5]}")
    
    # Test 2: Get bid/ask for BTC/USDT
    logger.info("\nTest 2: Getting current BTC/USDT price...")
    btc_price = client.get_bid_ask("BTCUSDT")
    if btc_price:
        logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
        logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT price")
    
    # Test 3: Get historical candles
    logger.info("\nTest 3: Getting historical candles for BTC/USDT (1-hour interval)...")
    candles = client.get_historical_candles("BTCUSDT", "1h")
    logger.info(f"Retrieved {len(candles)} candles")
    if candles:
        logger.info("Most recent candle:")
        logger.info(f"  Time: {candles[-1].timestamp}")
        logger.info(f"  Open: ${candles[-1].open_price:.2f}")
        logger.info(f"  High: ${candles[-1].high_price:.2f}")
        logger.info(f"  Low: ${candles[-1].low_price:.2f}")
        logger.info(f"  Close: ${candles[-1].close_price:.2f}")
        logger.info(f"  Volume: {candles[-1].volume:.8f}")
    
    # Test 4: Get account balance
    logger.info("\nTest 4: Getting account balance...")
    balance = client.get_balance()
    if balance and balance.assets:
        logger.info("Account balance retrieved successfully")
        # Print assets with non-zero balances
        non_zero_assets = {asset: data for asset, data in balance.assets.items() 
                          if float(data.free) > 0 or float(data.locked) > 0}
        
        if non_zero_assets:
            logger.info("Assets with non-zero balance:")
            for asset, data in non_zero_assets.items():
                logger.info(f"  {asset}: Free={data.free}, Locked={data.locked}")
        else:
            logger.info("No assets with non-zero balance found")
    else:
        logger.warning("No balance data retrieved or empty response")

if __name__ == "__main__":
    main()