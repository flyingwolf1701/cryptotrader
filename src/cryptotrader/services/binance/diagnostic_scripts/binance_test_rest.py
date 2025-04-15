#!/usr/bin/env python
"""
Binance REST Client Test Script
-------------------------------
Tests the Binance REST API client to verify connectivity and data retrieval.

This script tests the functionality of the Binance REST client by making direct
API calls and verifying responses. It focuses purely on testing the API connectivity
and response handling, without implementing any business logic.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/binance_test_rest.py

This script focuses on testing the RestClient directly rather than the unified Client.
"""

import sys
from pathlib import Path
import time
import json
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Config
from cryptotrader.services.binance.binance_rest_client import RestClient
from cryptotrader.services.binance.binance_models import (
    OrderRequest, OrderType, OrderSide, TimeInForce
)

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
    logger.info(f"{Fore.MAGENTA}Test 1: Checking rate limits configuration...")
    for rate_limit in rest_client.rate_limiter.rate_limits:
        logger.info(f"Rate limit: {rate_limit.rate_limit_type} - {rate_limit.limit} per {rate_limit.interval_num} {rate_limit.interval}")
    
    # Test 2: Get available symbols
    logger.info(f"\n{Fore.MAGENTA}Test 2: Getting available symbols...")
    symbols = RestClient.get_symbols_binance()
    logger.info(f"Retrieved {len(symbols)} symbols")
    logger.info(f"First 5 symbols: {symbols[:5]}")
    
    # Test 3: Server time
    logger.info(f"\n{Fore.MAGENTA}Test 3: Checking server time...")
    server_time = rest_client.get_server_time()
    logger.info(f"Server time: {server_time}")
    
    time_diff = rest_client.check_server_time()
    logger.info(f"Time difference between local and server: {time_diff}ms")
    
    # Test 4: System status
    logger.info(f"\n{Fore.MAGENTA}Test 4: Checking system status...")
    system_status = rest_client.get_system_status()
    logger.info(f"System status: {system_status.status_description} (code: {system_status.status_code})")
    logger.info(f"Is normal: {system_status.is_normal}")
    logger.info(f"Is maintenance: {system_status.is_maintenance}")
    
    # Test 5: Exchange info
    logger.info(f"\n{Fore.MAGENTA}Test 5: Getting exchange info...")
    exchange_info = rest_client.get_exchange_info()
    logger.info(f"Exchange info retrieved with {len(exchange_info.get('symbols', []))} symbols")
    
    # Test 6: Symbol info
    logger.info(f"\n{Fore.MAGENTA}Test 6: Getting symbol info for BTC/USDT...")
    symbol_info = rest_client.get_symbol_info("BTCUSDT")
    if symbol_info:
        logger.info(f"Symbol: {symbol_info.symbol}")
        logger.info(f"Base Asset: {symbol_info.baseAsset}")
        logger.info(f"Quote Asset: {symbol_info.quoteAsset}")
        logger.info(f"Status: {symbol_info.status}")
    else:
        logger.error("Failed to retrieve symbol info for BTCUSDT")
    
    # Test 7: Self-trade prevention modes
    logger.info(f"\n{Fore.MAGENTA}Test 7: Getting self-trade prevention modes...")
    stp_modes = rest_client.get_self_trade_prevention_modes()
    logger.info(f"Default mode: {stp_modes['default']}")
    logger.info(f"Allowed modes: {stp_modes['allowed']}")
    
    # Test 8: Order book (market depth)
    logger.info(f"\n{Fore.MAGENTA}Test 8: Getting order book for BTC/USDT...")
    order_book = rest_client.get_order_book("BTCUSDT", limit=5)
    if order_book:
        logger.info(f"Order book retrieved with last update ID: {order_book.last_update_id}")
        logger.info(f"Top {len(order_book.bids)} bids:")
        for i, bid in enumerate(order_book.bids[:3]):
            logger.info(f"  {i+1}. Price: ${bid.price:.2f}, Quantity: {bid.quantity:.8f}")
        
        logger.info(f"Top {len(order_book.asks)} asks:")
        for i, ask in enumerate(order_book.asks[:3]):
            logger.info(f"  {i+1}. Price: ${ask.price:.2f}, Quantity: {ask.quantity:.8f}")
    else:
        logger.error("Failed to retrieve order book")
    
    # Test 9: Bid/Ask price
    logger.info(f"\n{Fore.MAGENTA}Test 9: Getting current BTC/USDT bid/ask price...")
    btc_price = rest_client.get_bid_ask("BTCUSDT")
    if btc_price:
        logger.info(f"BTC/USDT Bid: ${btc_price.bid:.2f}")
        logger.info(f"BTC/USDT Ask: ${btc_price.ask:.2f}")
    else:
        logger.error("Failed to retrieve BTC/USDT price")
    
    # Test 10: Recent trades
    logger.info(f"\n{Fore.MAGENTA}Test 10: Getting recent trades for BTC/USDT...")
    recent_trades = rest_client.get_recent_trades("BTCUSDT", limit=5)
    logger.info(f"Retrieved {len(recent_trades)} recent trades")
    if recent_trades:
        logger.info("Most recent trade:")
        latest_trade = recent_trades[-1]
        logger.info(f"  ID: {latest_trade.id}")
        logger.info(f"  Price: ${latest_trade.price:.2f}")
        logger.info(f"  Quantity: {latest_trade.quantity:.8f}")
    else:
        logger.error("Failed to retrieve recent trades")
    
    # Test 11: Historical trades
    logger.info(f"\n{Fore.MAGENTA}Test 11: Getting historical trades for BTC/USDT...")
    historical_trades = rest_client.get_historical_trades("BTCUSDT", limit=5)
    logger.info(f"Retrieved {len(historical_trades)} historical trades")
    if historical_trades:
        logger.info("Sample historical trade:")
        sample_trade = historical_trades[0]
        logger.info(f"  ID: {sample_trade.id}")
        logger.info(f"  Price: ${sample_trade.price:.2f}")
    else:
        logger.error("Failed to retrieve historical trades")
    
    # Test 12: Aggregate trades
    logger.info(f"\n{Fore.MAGENTA}Test 12: Getting aggregate trades for BTC/USDT...")
    agg_trades = rest_client.get_aggregate_trades("BTCUSDT", limit=5)
    logger.info(f"Retrieved {len(agg_trades)} aggregate trades")
    if agg_trades:
        logger.info("Sample aggregate trade:")
        sample_agg_trade = agg_trades[0]
        logger.info(f"  ID: {sample_agg_trade.aggregate_trade_id}")
        logger.info(f"  Price: ${sample_agg_trade.price:.2f}")
        logger.info(f"  Quantity: {sample_agg_trade.quantity:.8f}")
    else:
        logger.error("Failed to retrieve aggregate trades")
    
    # Test 13: Historical candles
    logger.info(f"\n{Fore.MAGENTA}Test 13: Getting historical candles for BTC/USDT...")
    candles = rest_client.get_historical_candles("BTCUSDT", "1h", limit=5)
    logger.info(f"Retrieved {len(candles)} candles")
    if candles:
        logger.info("Most recent candle:")
        logger.info(f"  Time: {candles[-1].timestamp}")
        logger.info(f"  Open: ${candles[-1].open_price:.2f}")
        logger.info(f"  High: ${candles[-1].high_price:.2f}")
        logger.info(f"  Low: ${candles[-1].low_price:.2f}")
        logger.info(f"  Close: ${candles[-1].close_price:.2f}")
    else:
        logger.error("Failed to retrieve historical candles")
    
    # Test 14: Ticker price
    logger.info(f"\n{Fore.MAGENTA}Test 14: Getting ticker price for BTC/USDT...")
    ticker_price = rest_client.get_ticker_price(symbol="BTCUSDT")
    if ticker_price:
        logger.info(f"BTC/USDT Price: ${ticker_price.price:.2f}")
    else:
        logger.error("Failed to retrieve ticker price")
    
    # Test 15: Average price
    logger.info(f"\n{Fore.MAGENTA}Test 15: Getting average price for BTC/USDT...")
    avg_price = rest_client.get_avg_price("BTCUSDT")
    if avg_price:
        logger.info(f"BTC/USDT Average Price (over {avg_price.mins} minutes): ${avg_price.price:.2f}")
    else:
        logger.error("Failed to retrieve average price")
    
    # Test 16: 24h statistics (FULL)
    logger.info(f"\n{Fore.MAGENTA}Test 16: Getting 24h statistics for BTC/USDT (FULL)...")
    stats_24h = rest_client.get_24h_stats(symbol="BTCUSDT")
    if stats_24h:
        logger.info(f"24h Statistics for {stats_24h.symbol}:")
        logger.info(f"  Price Change: ${stats_24h.price_change:.2f} ({stats_24h.price_change_percent}%)")
        logger.info(f"  Weighted Avg Price: ${stats_24h.weighted_avg_price:.2f}")
        logger.info(f"  High: ${stats_24h.high_price:.2f}")
        logger.info(f"  Low: ${stats_24h.low_price:.2f}")
        logger.info(f"  Volume: {stats_24h.volume:.8f}")
    else:
        logger.error("Failed to retrieve 24h statistics")
    
    # Test 17: 24h statistics (MINI)
    logger.info(f"\n{Fore.MAGENTA}Test 17: Getting 24h statistics for BTC/USDT (MINI)...")
    stats_24h_mini = rest_client.get_24h_stats(symbol="BTCUSDT", type="MINI")
    if stats_24h_mini:
        logger.info(f"24h MINI Statistics for {stats_24h_mini.symbol}:")
        logger.info(f"  Price Change: ${stats_24h_mini.price_change:.2f}")
        logger.info(f"  High: ${stats_24h_mini.high_price:.2f}")
        logger.info(f"  Low: ${stats_24h_mini.low_price:.2f}")
        logger.info(f"  Volume: {stats_24h_mini.volume:.8f}")
    else:
        logger.error("Failed to retrieve 24h MINI statistics")
    
    # Test 18: Multiple symbols for 24h stats
    logger.info(f"\n{Fore.MAGENTA}Test 18: Getting 24h statistics for multiple symbols...")
    multi_symbols = ["BTCUSDT", "ETHUSDT"]
    multi_stats = rest_client.get_24h_stats(symbols=multi_symbols)
    if multi_stats and len(multi_stats) > 0:
        logger.info(f"Retrieved statistics for {len(multi_stats)} symbols")
        for stats in multi_stats:
            logger.info(f"  {stats.symbol}: Volume: {stats.volume:.4f}")
    else:
        logger.error("Failed to retrieve multi-symbol 24h statistics")
    
    # Test 19: Rolling window statistics
    logger.info(f"\n{Fore.MAGENTA}Test 19: Getting rolling window statistics for BTC/USDT...")
    window_stats = rest_client.get_rolling_window_stats(symbol="BTCUSDT", window_size="1d")
    if window_stats:
        logger.info(f"Rolling Window Statistics for {window_stats.symbol} (1d window):")
        logger.info(f"  Price Change: ${window_stats.price_change:.2f} ({window_stats.price_change_percent}%)")
        logger.info(f"  Weighted Avg Price: ${window_stats.weighted_avg_price:.2f}")
        logger.info(f"  Open Time: {window_stats.open_time}")
        logger.info(f"  Close Time: {window_stats.close_time}")
    else:
        logger.error("Failed to retrieve rolling window statistics")
    
    # Test 20: Account balance (authenticated)
    logger.info(f"\n{Fore.MAGENTA}Test 20: Getting account balance...")
    balance = rest_client.get_balance()
    if balance and balance.assets:
        logger.info("Account balance retrieved successfully")
        non_zero_assets = {asset: data for asset, data in balance.assets.items() 
                         if float(data.free) > 0 or float(data.locked) > 0}
        
        if non_zero_assets:
            logger.info(f"Found {len(non_zero_assets)} assets with non-zero balance")
            for asset, data in list(non_zero_assets.items())[:3]:  # Show first 3 assets only
                logger.info(f"  {asset}: Free={data.free}, Locked={data.locked}")
        else:
            logger.info("No assets with non-zero balance found")
    else:
        logger.warning("No balance data retrieved or empty response")
    
    # Test 21: Rate limit usage
    logger.info(f"\n{Fore.MAGENTA}Test 21: Checking rate limit usage...")
    usage = rest_client.rate_limiter.get_rate_limit_usage()
    logger.info("Current rate limit usage:")
    for limit_key, count in usage.items():
        logger.info(f"  {limit_key}: {count}")
    
    # Test 22: Order request simulation (no actual order placement)
    logger.info(f"\n{Fore.MAGENTA}Test 22: Simulating an order request...")
    order_request = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        quantity=0.001,
        order_type=OrderType.LIMIT,
        price=10000.0,  # Unrealistic price to ensure it wouldn't execute
        time_in_force=TimeInForce.GTC,
        self_trade_prevention_mode="EXPIRE_MAKER"
    )
    logger.info("Order request created successfully:")
    logger.info(f"  Symbol: {order_request.symbol}")
    logger.info(f"  Side: {order_request.side}")
    logger.info(f"  Type: {order_request.order_type}")
    logger.info(f"  Quantity: {order_request.quantity}")
    logger.info(f"  Price: ${order_request.price}")
    logger.info(f"  Self-trade prevention: {order_request.self_trade_prevention_mode}")
    logger.info("(Order not actually placed to avoid accidental execution)")

if __name__ == "__main__":
    main()