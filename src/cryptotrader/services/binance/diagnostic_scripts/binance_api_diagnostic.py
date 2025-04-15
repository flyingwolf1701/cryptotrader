"""
Binance REST API Diagnostic

This script tests the Binance REST API client functionality without accessing real credentials.
It creates a mock client and attempts to call various API methods to verify the code structure.
"""

import sys
import os
from typing import Optional, Dict, Any

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the RestClient from the binance_rest_api module
from cryptotrader.services.binance.binance_rest_api import RestClient
from cryptotrader.config import get_logger

# Get a logger for this module
logger = get_logger(__name__)

def test_market_data_endpoints(client: RestClient) -> None:
    """Test market data endpoints."""
    logger.info("Testing market data endpoints...")
    
    # Test server time endpoint
    try:
        server_time = client.get_server_time()
        logger.info(f"Server time: {server_time}")
    except Exception as e:
        logger.error(f"Error getting server time: {str(e)}")
    
    # Test system status endpoint
    try:
        system_status = client.get_system_status()
        logger.info(f"System status: {system_status.status_description}")
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
    
    # Test exchange info endpoint
    try:
        exchange_info = client.get_exchange_info()
        logger.info(f"Exchange info contains {len(exchange_info.get('symbols', []))} symbols")
    except Exception as e:
        logger.error(f"Error getting exchange info: {str(e)}")
    
    # Test ticker price endpoint
    try:
        btc_ticker = client.get_ticker_price(symbol="BTCUSDT")
        if btc_ticker:
            logger.info(f"BTCUSDT price: {btc_ticker.price}")
    except Exception as e:
        logger.error(f"Error getting ticker price: {str(e)}")

def test_order_book_endpoints(client: RestClient) -> None:
    """Test order book related endpoints."""
    logger.info("Testing order book endpoints...")
    
    # Test get order book endpoint
    try:
        order_book = client.get_order_book(symbol="BTCUSDT", limit=10)
        if order_book:
            logger.info(f"Order book contains {len(order_book.bids)} bids and {len(order_book.asks)} asks")
    except Exception as e:
        logger.error(f"Error getting order book: {str(e)}")
    
    # Test get recent trades endpoint
    try:
        trades = client.get_recent_trades(symbol="BTCUSDT", limit=5)
        logger.info(f"Got {len(trades)} recent trades")
    except Exception as e:
        logger.error(f"Error getting recent trades: {str(e)}")

def main() -> None:
    """Main function to test the Binance REST API client."""
    logger.info("Starting Binance REST API diagnostics")
    
    try:
        # Create a client without API credentials for public endpoint testing
        client = RestClient()
        logger.info("Created REST client instance")
        
        # Test market data endpoints
        test_market_data_endpoints(client)
        
        # Test order book endpoints
        test_order_book_endpoints(client)
        
        logger.info("Binance REST API diagnostics completed")
    except Exception as e:
        logger.error(f"Unexpected error during diagnostics: {str(e)}")

if __name__ == "__main__":
    main()