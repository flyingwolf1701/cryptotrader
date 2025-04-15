"""
Binance Market API Diagnostic Script
------------------------------------
Tests the Binance Market API client to verify connectivity and data retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/b_market_diagnostic.py
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.market_api import MarketClient

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance Market client...")
    client = MarketClient()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get bid/ask for BTC/USDT
    logger.info("\nTest 1: Getting current BTC/USDT price...")
    btc_price = client.get_bid_ask("BTCUSDT")
    if btc_price:
        logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
        logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT price")
    
    # Test 2: Get historical candles
    logger.info("\nTest 2: Getting historical candles for BTC/USDT (1-hour interval)...")
    candles = client.get_historical_candles("BTCUSDT", "1h", limit=10)
    logger.info(f"Retrieved {len(candles)} candles")
    if candles:
        logger.info("Most recent candle:")
        logger.info(f"  Time: {candles[-1].timestamp}")
        logger.info(f"  Open: ${candles[-1].open_price:.2f}")
        logger.info(f"  High: ${candles[-1].high_price:.2f}")
        logger.info(f"  Low: ${candles[-1].low_price:.2f}")
        logger.info(f"  Close: ${candles[-1].close_price:.2f}")
        logger.info(f"  Volume: {candles[-1].volume:.8f}")
    
    # Test 3: Get ticker price for BTC/USDT
    logger.info("\nTest 3: Getting ticker price for BTC/USDT...")
    ticker = client.get_ticker_price("BTCUSDT")
    if ticker:
        logger.info(f"BTC/USDT Price: ${float(ticker.price):.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT ticker price")
    
    # Test 4: Get average price for BTC/USDT
    logger.info("\nTest 4: Getting average price for BTC/USDT...")
    avg_price = client.get_avg_price("BTCUSDT")
    if avg_price:
        logger.info(f"BTC/USDT Average Price (mins={avg_price.mins}): ${avg_price.price:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT average price")
        
    # Test 5: Get order book
    logger.info("\nTest 5: Getting order book for BTC/USDT...")
    order_book = client.get_order_book("BTCUSDT", limit=5)
    if order_book:
        logger.info(f"Order Book Last Update ID: {order_book.last_update_id}")
        logger.info(f"Top 5 Bids:")
        for i, bid in enumerate(order_book.bids[:5]):
            logger.info(f"  {i+1}. Price: ${bid.price:.2f}, Quantity: {bid.quantity:.8f}")
        logger.info(f"Top 5 Asks:")
        for i, ask in enumerate(order_book.asks[:5]):
            logger.info(f"  {i+1}. Price: ${ask.price:.2f}, Quantity: {ask.quantity:.8f}")
    else:
        logger.error("Failed to retrieve BTC/USDT order book")
        
    # Test 6: Get 24-hour price statistics
    logger.info("\nTest 6: Getting 24-hour price statistics for BTC/USDT...")
    stats = client.get_24h_stats("BTCUSDT")
    if stats:
        logger.info(f"24h Price Change: ${stats.price_change:.2f} ({stats.price_change_percent:.2f}%)")
        logger.info(f"24h High: ${stats.high_price:.2f}")
        logger.info(f"24h Low: ${stats.low_price:.2f}")
        logger.info(f"24h Volume: {stats.volume:.8f} BTC")
        logger.info(f"24h Quote Volume: ${stats.quote_volume:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT 24-hour statistics")

if __name__ == "__main__":
    main()