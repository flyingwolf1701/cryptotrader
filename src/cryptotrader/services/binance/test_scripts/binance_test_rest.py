#!/usr/bin/env python
"""
Binance REST Client Test Script
-------------------------------
Tests the Binance REST API client to verify connectivity and data retrieval.

This script tests both core and extended functionality of the Binance REST client,
including new features like system status, self-trade prevention modes, and
advanced rate limit handling.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/binance_test_rest.py

This script focuses on testing the RestClient directly rather than the unified Client.
"""

import sys
from pathlib import Path
import time

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Config
from cryptotrader.services.binance.binance_rest_client import RestClient
from cryptotrader.services.binance.binance_models import OrderRequest, OrderType, OrderSide, TimeInForce

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
    
    logger.info("Initializing Binance REST client...")
    rest_client = RestClient(api_key, api_secret)
    
    # Test 1: Check rate limits
    logger.info("Test 1: Checking rate limits configuration...")
    for rate_limit in rest_client.rate_limiter.rate_limits:
        logger.info(f"Rate limit: {rate_limit.rate_limit_type} - {rate_limit.limit} per {rate_limit.interval_num} {rate_limit.interval}")
    
    # Test 2: Get available symbols
    logger.info("\nTest 2: Getting available symbols...")
    symbols = RestClient.get_symbols_binance()
    logger.info(f"Retrieved {len(symbols)} symbols")
    logger.info(f"First 5 symbols: {symbols[:5]}")
    
    # Test 3: Get bid/ask for BTC/USDT
    logger.info("\nTest 3: Getting current BTC/USDT price...")
    btc_price = rest_client.get_bid_ask("BTCUSDT")
    if btc_price:
        logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
        logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT price")
    
    # Test 4: Get historical candles
    logger.info("\nTest 4: Getting historical candles for BTC/USDT (1-hour interval)...")
    candles = rest_client.get_historical_candles("BTCUSDT", "1h")
    logger.info(f"Retrieved {len(candles)} candles")
    if candles:
        logger.info("Most recent candle:")
        logger.info(f"  Time: {candles[-1].timestamp}")
        logger.info(f"  Open: ${candles[-1].open_price:.2f}")
        logger.info(f"  High: ${candles[-1].high_price:.2f}")
        logger.info(f"  Low: ${candles[-1].low_price:.2f}")
        logger.info(f"  Close: ${candles[-1].close_price:.2f}")
        logger.info(f"  Volume: {candles[-1].volume:.8f}")
    
    # Test 5: Get account balance
    logger.info("\nTest 5: Getting account balance...")
    balance = rest_client.get_balance()
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
    
    # Test 6: Get server time and check time drift
    logger.info("\nTest 6: Checking server time...")
    server_time = rest_client.get_server_time()
    logger.info(f"Server time: {server_time}")
    
    time_diff = rest_client.check_server_time()
    logger.info(f"Time difference between local and server: {time_diff}ms")
    
    # Test 7: Get exchange info and symbol info
    logger.info("\nTest 7: Getting exchange info...")
    exchange_info = rest_client.get_exchange_info()
    logger.info(f"Exchange info retrieved with {len(exchange_info.get('symbols', []))} symbols")
    
    logger.info("\nGetting BTC/USDT symbol info...")
    symbol_info = rest_client.get_symbol_info("BTCUSDT")
    if symbol_info:
        logger.info(f"Symbol: {symbol_info.symbol}")
        logger.info(f"Base Asset: {symbol_info.baseAsset}")
        logger.info(f"Quote Asset: {symbol_info.quoteAsset}")
        logger.info(f"Status: {symbol_info.status}")
        logger.info(f"Available Order Types: {[ot for ot in symbol_info.orderTypes]}")
    else:
        logger.error("Failed to retrieve symbol info for BTCUSDT")
    
    # Test 8: Get system status - NEW TEST
    logger.info("\nTest 8: Checking system status...")
    system_status = rest_client.get_system_status()
    logger.info(f"System status: {system_status.status_description} (code: {system_status.status_code})")
    logger.info(f"Is normal: {system_status.is_normal}")
    logger.info(f"Is maintenance: {system_status.is_maintenance}")
    
    # Test 9: Get self-trade prevention modes - NEW TEST
    logger.info("\nTest 9: Getting self-trade prevention modes...")
    stp_modes = rest_client.get_self_trade_prevention_modes()
    logger.info(f"Default mode: {stp_modes['default']}")
    logger.info(f"Allowed modes: {stp_modes['allowed']}")
    
    # Test 10: Get filtered exchange info - NEW TEST
    logger.info("\nTest 10: Getting filtered exchange info...")
    eth_info = rest_client.get_exchange_info(symbol="ETHUSDT")
    if 'symbols' in eth_info and len(eth_info['symbols']) > 0:
        logger.info(f"ETHUSDT symbol info retrieved successfully")
        eth_symbol = eth_info['symbols'][0]
        logger.info(f"Symbol: {eth_symbol['symbol']}")
        logger.info(f"Status: {eth_symbol['status']}")
    else:
        logger.error("Failed to retrieve ETHUSDT exchange info")
        
    # Test multiple symbols
    multi_symbols = rest_client.get_exchange_info(symbols=["BTCUSDT", "ETHUSDT"])
    if 'symbols' in multi_symbols:
        logger.info(f"Multi-symbol info retrieved successfully with {len(multi_symbols['symbols'])} symbols")
    else:
        logger.error("Failed to retrieve multi-symbol exchange info")
        
    # Test with permissions
    spot_symbols = rest_client.get_exchange_info(permissions=["SPOT"])
    if 'symbols' in spot_symbols:
        logger.info(f"SPOT permissions info retrieved with {len(spot_symbols['symbols'])} symbols")
    else:
        logger.error("Failed to retrieve SPOT permissions exchange info")
    
    # Test 11: Rate limit usage - NEW TEST
    logger.info("\nTest 11: Checking rate limit usage...")
    usage = rest_client.rate_limiter.get_rate_limit_usage()
    logger.info("Current rate limit usage:")
    for limit_key, count in usage.items():
        logger.info(f"  {limit_key}: {count}")
    
    # Test 12: Order with self-trade prevention - NEW TEST (simulation only)
    logger.info("\nTest 12: Simulating an order with self-trade prevention mode...")
    # We won't actually place this order, just show how it would be created
    order_request = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        quantity=0.001,
        order_type=OrderType.LIMIT,
        price=10000.0,  # Unrealistic price to ensure it doesn't execute
        time_in_force=TimeInForce.GTC,
        self_trade_prevention_mode="EXPIRE_MAKER"  # Using the new field
    )
    logger.info(f"Order request created with self-trade prevention mode: {order_request.self_trade_prevention_mode}")
    logger.info("(Order not actually placed to avoid accidental execution)")
    
    # Test 13: Retry mechanism with delay - NEW TEST
    logger.info("\nTest 13: Testing retry mechanism (simulation)...")
    logger.info("In a real scenario, retries would happen automatically on 429/418 responses")
    logger.info("The client would honor the Retry-After header and use exponential backoff")
    
    # Demonstrate rate limiting by making rapid requests
    logger.info("\nMaking multiple rapid requests to demonstrate rate limit awareness...")
    for i in range(5):
        logger.info(f"Request {i+1}/5: Getting server time")
        start_time = time.time()
        server_time = rest_client.get_server_time()
        end_time = time.time()
        logger.info(f"Request completed in {(end_time - start_time)*1000:.2f}ms")
        # No sleep to demonstrate rate limit awareness

if __name__ == "__main__":
    main()