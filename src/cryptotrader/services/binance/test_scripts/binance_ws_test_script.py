#!/usr/bin/env python
"""
Binance WebSocket Client Test Script
-----------------------------------
Tests the Binance WebSocket API client to verify connectivity and data streaming.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/binance_ws_test_script.py

This script focuses on testing the WebSocketClient directly rather than the unified Client.
"""

import sys
import time
import asyncio
import signal
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Config
from cryptotrader.services.binance.binance_ws_client import WebSocketClient

logger = get_logger(__name__)

# Global flag to track when to exit
should_exit = False

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit"""
    global should_exit
    logger.info("Received signal to terminate. Cleaning up...")
    should_exit = True

def ws_data_callback(event_type, data):
    """Callback function to handle WebSocket data"""
    logger.info(f"Received WebSocket event: {event_type}")
    if event_type == "bookTicker":
        symbol = data.get('s', 'Unknown')
        bid = data.get('b', 'Unknown')
        ask = data.get('a', 'Unknown')
        logger.info(f"Price update for {symbol}: Bid=${bid}, Ask=${ask}")
    elif event_type == "kline":
        symbol = data.get('s', 'Unknown')
        interval = data.get('k', {}).get('i', 'Unknown')
        close_price = data.get('k', {}).get('c', 'Unknown')
        logger.info(f"Kline update for {symbol} ({interval}): Close=${close_price}")

def main():
    global should_exit
    
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info(f"Added {project_root} to Python path")
    
    # Initialize WebSocket client
    logger.info("Initializing Binance WebSocket client...")
    ws_client = WebSocketClient(callback=ws_data_callback)
    
    try:
        # Test 1: Start WebSocket connection
        logger.info("Test 1: Starting WebSocket connection...")
        ws_client.start()
        logger.info("WebSocket connection started")
        
        # Allow some time for connection to establish
        logger.info("Waiting for connection to establish...")
        time.sleep(2)
        
        # Test 2: Subscribe to BTC/USDT ticker updates
        logger.info("\nTest 2: Subscribing to BTC/USDT ticker...")
        ws_client.subscribe("BTCUSDT", ["bookTicker"])
        logger.info("Subscribed to BTC/USDT ticker")
        
        # Wait for some data to arrive
        logger.info("Waiting for ticker data (5 seconds)...")
        time.sleep(5)
        
        # Test 3: Check if we received price data
        logger.info("\nTest 3: Checking received price data...")
        price_data = ws_client.get_price("BTCUSDT")
        if price_data:
            logger.info(f"BTC/USDT Bid: ${price_data.bid:.2f}")
            logger.info(f"BTC/USDT Ask: ${price_data.ask:.2f}")
        else:
            logger.warning("No price data received yet for BTC/USDT")
        
        # Test 4: Subscribe to candlestick data
        logger.info("\nTest 4: Subscribing to BTC/USDT 1-minute candlesticks...")
        ws_client.subscribe("BTCUSDT", ["kline_1m"])
        logger.info("Subscribed to BTC/USDT 1-minute candlesticks")
        
        # Wait for some candlestick data
        logger.info("Waiting for candlestick data (10 seconds)...")
        time.sleep(10)
        
        # Test 5: Check if we received candlestick data
        logger.info("\nTest 5: Checking received candlestick data...")
        candles = ws_client.get_candles("BTCUSDT", "1m")
        if candles:
            logger.info(f"Received {len(candles)} candles for BTC/USDT")
            if len(candles) > 0:
                latest = candles[-1]
                logger.info(f"Latest candle: Open=${latest.open_price:.2f}, Close=${latest.close_price:.2f}")
        else:
            logger.warning("No candlestick data received yet for BTC/USDT")
        
        # Test 6: Subscribe to a different symbol
        logger.info("\nTest 6: Subscribing to ETH/USDT ticker...")
        ws_client.subscribe("ETHUSDT", ["bookTicker"])
        logger.info("Subscribed to ETH/USDT ticker")
        
        # Wait for some data
        logger.info("Waiting for ETH/USDT data (5 seconds)...")
        time.sleep(5)
        
        # Check ETH price
        price_data = ws_client.get_price("ETHUSDT")
        if price_data:
            logger.info(f"ETH/USDT Bid: ${price_data.bid:.2f}")
            logger.info(f"ETH/USDT Ask: ${price_data.ask:.2f}")
        else:
            logger.warning("No price data received yet for ETH/USDT")
        
        # Test 7: Unsubscribe from a channel
        logger.info("\nTest 7: Unsubscribing from BTC/USDT ticker...")
        ws_client.unsubscribe("BTCUSDT", ["bookTicker"])
        logger.info("Unsubscribed from BTC/USDT ticker")
        
        # Let it run for a bit to verify
        logger.info("\nRunning for 5 more seconds to observe updates...")
        timeout = time.time() + 5
        while time.time() < timeout and not should_exit:
            time.sleep(0.1)
        
    except Exception as e:
        logger.error(f"Error during WebSocket testing: {e}")
    finally:
        # Test 8: Close the WebSocket connection
        logger.info("\nTest 8: Closing WebSocket connection...")
        ws_client.close()
        logger.info("WebSocket connection closed")
        
        # Give a moment for the connection to fully close
        time.sleep(1)

if __name__ == "__main__":
    main()