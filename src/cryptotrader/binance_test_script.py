#!/usr/bin/env python
"""
Binance API Test Script
-----------------------
Tests the Binance API client to verify connectivity and data retrieval.
"""

import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)



def main():
    
    
    # Get API credentials
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file")
        return
    
    # Adjust import paths based on where the script is run from
    if "cryptotrader" not in sys.modules:
        sys.path.append(str(Path(__file__).parent.parent))  # Add parent directory to path
        if os.path.exists("src"):
            sys.path.append("src")  # Add src directory if it exists
    
    # Import our client
    try:
        from cryptotrader.services.binance_client import Client
    except ImportError:
        try:
            from services.binance_client import Client
        except ImportError:
            logger.error("Could not import the Binance Client. Check your directory structure.")
            return
    
    logger.info("Initializing Binance client...")
    client = Client(api_key, api_secret)
    
    # Test 1: Get available symbols
    logger.info("Test 1: Getting available symbols...")
    try:
        symbols = Client.get_symbols_binance()
        logger.info(f"Retrieved {len(symbols)} symbols")
        logger.info(f"First 5 symbols: {symbols[:5]}")
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
    
    # Test 2: Get bid/ask for BTC/USDT
    logger.info("\nTest 2: Getting current BTC/USDT price...")
    try:
        btc_price = client.get_bid_ask("BTCUSDT")
        if btc_price:
            logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
            logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
        else:
            logger.error("Failed to retrieve BTC/USDT price")
    except Exception as e:
        logger.error(f"Error getting BTC price: {e}")
    
    # Test 3: Get historical candles
    logger.info("\nTest 3: Getting historical candles for BTC/USDT (1-hour interval)...")
    try:
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
    except Exception as e:
        logger.error(f"Error getting historical candles: {e}")
    
    # Test 4: Get account balance (requires API key with permissions)
    logger.info("\nTest 4: Getting account balance...")
    try:
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
    except Exception as e:
        logger.error(f"Error getting account balance: {e}")
        logger.info("This may be due to insufficient API permissions")

if __name__ == "__main__":
    main()