"""
Binance REST API Diagnostic Script
----------------------------------
Tests the Binance REST API client to verify connectivity and data retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/diagnostic_b_rest_api.py

Note:
    This script focuses on testing market data and general API functionality,
    not order-related endpoints.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, settings
from cryptotrader.services.binance.binance_rest_client import RestClient

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    # Get API credentials from settings 
    api_key = settings.BINANCE_API_KEY
    api_secret = settings.BINANCE_API_SECRET
    
    logger.info(f"API Key loaded: {'Yes' if api_key else 'No'}")
    logger.info(f"API Secret loaded: {'Yes' if api_secret else 'No'}")
    
    if not api_key or not api_secret:
        logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file")
        return
    
    logger.info("Initializing Binance client...")
    client = RestClient(api_key, api_secret)
    
    # Test 1: Get system status
    logger.info("\nTest 1: Checking system status...")
    system_status = client.get_system_status()
    logger.info(f"System status: {system_status.status_description}")
    
    # Test 2: Check server time
    logger.info("\nTest 2: Checking server time...")
    server_time = client.get_server_time()
    logger.info(f"Server timestamp: {server_time}")
    
    # Test 3: Get available symbols
    logger.info("\nTest 3: Getting available symbols...")
    symbols = RestClient.get_symbols_binance()
    logger.info(f"Retrieved {len(symbols)} symbols")
    logger.info(f"First 5 symbols: {symbols[:5]}")
    
    # Test 4: Get ticker prices
    logger.info("\nTest 4: Getting current BTC/USDT ticker price...")
    btc_ticker = client.get_ticker_price("BTCUSDT")
    if btc_ticker:
        logger.info(f"BTC/USDT Price: ${float(btc_ticker.price):.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT ticker price")
    
    # Test 5: Get bid/ask
    logger.info("\nTest 5: Getting current BTC/USDT bid/ask prices...")
    btc_price = client.get_bid_ask("BTCUSDT")
    if btc_price:
        logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
        logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT bid/ask prices")
    
    # Test 6: Get 24h statistics
    logger.info("\nTest 6: Getting 24h statistics for BTC/USDT...")
    btc_stats = client.get_24h_stats("BTCUSDT")
    if btc_stats:
        logger.info(f"BTC/USDT 24h Volume: {btc_stats.volume:.4f}")
        logger.info(f"BTC/USDT 24h Price Change: ${btc_stats.price_change:.2f} ({btc_stats.price_change_percent:.2f}%)")
        logger.info(f"BTC/USDT 24h High: ${btc_stats.high_price:.2f}")
        logger.info(f"BTC/USDT 24h Low: ${btc_stats.low_price:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT 24h statistics")
    
    # Test 7: Get order book
    logger.info("\nTest 7: Getting BTC/USDT order book (depth=5)...")
    order_book = client.get_order_book("BTCUSDT", limit=5)
    if order_book:
        logger.info(f"Order book last update ID: {order_book.last_update_id}")
        logger.info("Top 5 bids:")
        for i, bid in enumerate(order_book.bids[:5], 1):
            logger.info(f"  {i}. Price: ${bid.price:.2f}, Quantity: {bid.quantity:.8f}")
        logger.info("Top 5 asks:")
        for i, ask in enumerate(order_book.asks[:5], 1):
            logger.info(f"  {i}. Price: ${ask.price:.2f}, Quantity: {ask.quantity:.8f}")
    else:
        logger.error("Failed to retrieve BTC/USDT order book")
    
    # Test 8: Get account balance (if authenticated)
    logger.info("\nTest 8: Getting account balance...")
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