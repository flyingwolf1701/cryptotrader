#!/usr/bin/env python
"""
Binance API Diagnostic Script
-----------------------------
Tests the Binance REST API client to verify market data functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/binance_api_diagnostic.py
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.binance import Client
from cryptotrader.services.binance.binance_models import KlineInterval

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    # Get API credentials from Secrets 
    api_key = Secrets.BINANCE_API_KEY
    api_secret = Secrets.BINANCE_API_SECRET
    
    logger.info(f"API Key loaded: {'Yes' if api_key else 'No'}")
    logger.info(f"API Secret loaded: {'Yes' if api_secret else 'No'}")
    
    if not api_key or not api_secret:
        logger.error("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET in your .env file")
        return
    
    logger.info("Initializing Binance client...")
    client = Client(api_key, api_secret)
    
    # Test 1: Get server time
    logger.info("\nTest 1: Getting server time...")
    server_time = client.get_server_time()
    logger.info(f"Server time: {server_time}")
    
    # Test 2: Get system status
    logger.info("\nTest 2: Getting system status...")
    system_status = client.get_system_status()
    logger.info(f"System status: {system_status.status_description}")
    
    # Test 3: Get ticker price for BTC/USDT
    logger.info("\nTest 3: Getting ticker price for BTC/USDT...")
    ticker = client.get_ticker_price("BTCUSDT")
    if ticker:
        logger.info(f"BTC/USDT price: ${float(ticker.price):.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT ticker price")
    
    # Test 4: Get average price for BTC/USDT
    logger.info("\nTest 4: Getting average price for BTC/USDT...")
    avg_price = client.get_avg_price("BTCUSDT")
    if avg_price:
        logger.info(f"BTC/USDT average price (past {avg_price.mins} mins): ${float(avg_price.price):.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT average price")
    
    # Test 5: Get 24h statistics for BTC/USDT
    logger.info("\nTest 5: Getting 24h statistics for BTC/USDT...")
    stats = client.get_24h_stats("BTCUSDT")
    if stats:
        logger.info(f"BTC/USDT 24h price change: ${float(stats.price_change):.2f} ({float(stats.price_change_percent):.2f}%)")
        logger.info(f"BTC/USDT 24h high: ${float(stats.high_price):.2f}")
        logger.info(f"BTC/USDT 24h low: ${float(stats.low_price):.2f}")
        logger.info(f"BTC/USDT 24h volume: {float(stats.volume):.2f} BTC")
        logger.info(f"BTC/USDT 24h quote volume: ${float(stats.quote_volume):.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT 24h statistics")
    
    # Test 6: Get recent trades for BTC/USDT
    logger.info("\nTest 6: Getting recent trades for BTC/USDT...")
    trades = client.get_recent_trades("BTCUSDT", limit=5)
    if trades:
        logger.info(f"Retrieved {len(trades)} recent trades")
        logger.info("Most recent trade:")
        logger.info(f"  ID: {trades[0].id}")
        logger.info(f"  Price: ${float(trades[0].price):.2f}")
        logger.info(f"  Quantity: {float(trades[0].quantity):.8f}")
        logger.info(f"  Time: {trades[0].time}")
    else:
        logger.error("Failed to retrieve BTC/USDT recent trades")
    
    # Test 7: Get order book for BTC/USDT
    logger.info("\nTest 7: Getting order book for BTC/USDT...")
    order_book = client.get_order_book("BTCUSDT", limit=5)
    if order_book:
        logger.info(f"Order book last update ID: {order_book.last_update_id}")
        logger.info(f"Top {len(order_book.bids)} bids:")
        for i, bid in enumerate(order_book.bids[:5]):
            logger.info(f"  {i+1}. Price: ${float(bid.price):.2f}, Quantity: {float(bid.quantity):.8f}")
        
        logger.info(f"Top {len(order_book.asks)} asks:")
        for i, ask in enumerate(order_book.asks[:5]):
            logger.info(f"  {i+1}. Price: ${float(ask.price):.2f}, Quantity: {float(ask.quantity):.8f}")
    else:
        logger.error("Failed to retrieve BTC/USDT order book")

if __name__ == "__main__":
    main()