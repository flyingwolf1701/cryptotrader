"""
Binance Order API Diagnostic Script
----------------------------------
Tests the Binance Order API client to verify order functionality.

This script performs read-only operations to test the Order API 
connectivity without placing actual orders on your account.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/order_diagnostic.py
"""

import sys
import time
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.order_api import OrderOperations
from cryptotrader.services.binance.models import (
    OrderRequest, OrderType, OrderSide, TimeInForce
)

logger = get_logger(__name__)

# Test symbol - Using a common trading pair
TEST_SYMBOL = "BTCUSDT"
# Small quantities for test scenarios (not actually placing orders)
TEST_QUANTITY = 0.001
TEST_PRICE = 10000.0  # Placeholder price for limit orders

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance Order client...")
    client = OrderOperations()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get open orders
    print_test_header("Getting Open Orders")
    try:
        open_orders = client.get_open_orders(TEST_SYMBOL)
        logger.info(f"Retrieved open orders for {TEST_SYMBOL}")
        logger.info(f"Number of open orders: {len(open_orders) if open_orders else 0}")
        
        if open_orders and len(open_orders) > 0:
            logger.info(f"First open order details:")
            logger.info(f"  Order ID: {open_orders[0].orderId}")
            logger.info(f"  Symbol: {open_orders[0].symbol}")
            logger.info(f"  Type: {open_orders[0].type}")
            logger.info(f"  Side: {open_orders[0].side}")
            logger.info(f"  Price: {open_orders[0].price}")
            logger.info(f"  Quantity: {open_orders[0].origQty}")
        else:
            logger.info(f"{Fore.YELLOW}No open orders found for {TEST_SYMBOL}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving open orders: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 2: Get order rate limits
    print_test_header("Getting Order Rate Limits")
    try:
        # This endpoint requires API key, but we're not actually placing orders
        rate_limits = client.get_order_rate_limits()
        if rate_limits:
            logger.info(f"{Fore.GREEN}Order rate limits retrieved: {len(rate_limits)} limits")
            for i, limit in enumerate(rate_limits):
                logger.info(f"  Limit {i+1}: {limit.rateLimitType} - {limit.limit} per {limit.intervalNum} {limit.interval} (Used: {limit.count})")
        else:
            logger.info(f"{Fore.YELLOW}No rate limit information available or authentication required")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving order rate limits: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 3: Test order creation (mock)
    print_test_header("Testing Order Creation API (No Actual Orders)")
    try:
        # Create a sample order request
        test_order = OrderRequest(
            symbol=TEST_SYMBOL,
            side=OrderSide.BUY,
            quantity=TEST_QUANTITY,
            order_type=OrderType.LIMIT,
            price=TEST_PRICE,
            time_in_force=TimeInForce.GTC
        )
        
        # Let the user know we're not actually placing orders
        logger.info(f"Would place a {test_order.side.value} {test_order.order_type.value} order for {test_order.quantity} {TEST_SYMBOL} at price {test_order.price}")
        logger.info(f"{Fore.YELLOW}NOTE: No actual orders will be placed during diagnostic")
        
        # Test the order test endpoint if we have API keys
        logger.info("Attempting to test order placement using test endpoint...")
        try:
            test_success = False
            # This will succeed only if API credentials are configured
            test_success = client.test_new_order(test_order)
            if test_success:
                logger.info(f"{Fore.GREEN}Order test successful - API credentials validated")
            else:
                logger.warning(f"{Fore.YELLOW}Order test failed - Check API credentials")
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not use test endpoint: {str(e)}")
            logger.info("Order testing requires valid API credentials with trading permissions")
    except Exception as e:
        logger.error(f"{Fore.RED}Error during order creation test: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 4: Get recent trade history
    print_test_header("Getting Trade History")
    try:
        # Get trades for the past day
        end_time = int(time.time() * 1000)
        start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago
        
        trades = client.get_my_trades(TEST_SYMBOL, start_time=start_time, end_time=end_time, limit=10)
        
        if trades:
            logger.info(f"{Fore.GREEN}Retrieved {len(trades)} recent trades for {TEST_SYMBOL}")
            logger.info(f"Most recent trades (last 24 hours):")
            
            for i, trade in enumerate(trades[:5]):  # Show up to 5 trades
                trade_time = datetime.fromtimestamp(trade.time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"  Trade {i+1}: {trade.qty} at price {trade.price} (Time: {trade_time})")
        else:
            logger.info(f"{Fore.YELLOW}No recent trades found for {TEST_SYMBOL} or authentication required")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving trade history: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 5: Get all orders history
    print_test_header("Getting Order History")
    try:
        # Get orders for the past week
        end_time = int(time.time() * 1000)
        start_time = end_time - (7 * 24 * 60 * 60 * 1000)  # 7 days ago
        
        all_orders = client.get_all_orders(TEST_SYMBOL, start_time=start_time, end_time=end_time, limit=10)
        
        if all_orders:
            logger.info(f"{Fore.GREEN}Retrieved {len(all_orders)} orders from history for {TEST_SYMBOL}")
            logger.info("Recent order history:")
            
            for i, order in enumerate(all_orders[:5]):  # Show up to 5 orders
                order_time = datetime.fromtimestamp(order.time / 1000).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"  Order {i+1}: {order.side} {order.type} - {order.origQty} at {order.price} (Status: {order.status}, Time: {order_time})")
        else:
            logger.info(f"{Fore.YELLOW}No order history found for {TEST_SYMBOL} or authentication required")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving order history: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 6: Get prevented matches
    print_test_header("Getting Prevented Matches")
    try:
        prevented_matches = client.get_prevented_matches(TEST_SYMBOL, limit=10)
        
        if prevented_matches:
            logger.info(f"{Fore.GREEN}Retrieved {len(prevented_matches)} prevented matches for {TEST_SYMBOL}")
            logger.info("Recent prevented matches:")
            
            for i, match in enumerate(prevented_matches[:5]):  # Show up to 5 matches
                match_time = datetime.fromtimestamp(match.transactTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
                logger.info(f"  Match {i+1}: Price {match.price}, Mode: {match.selfTradePreventionMode} (Time: {match_time})")
        else:
            logger.info(f"{Fore.YELLOW}No prevented matches found for {TEST_SYMBOL} or authentication required")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving prevented matches: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 7: Cancel Order Simulation
    print_test_header("Cancel Order Simulation (No Actual Cancellation)")
    logger.info("This test would demonstrate order cancellation functionality")
    logger.info(f"{Fore.YELLOW}For safety, we're not actually cancelling any orders during diagnostics")
    logger.info("To cancel orders, you would use:")
    logger.info("  client.cancel_order(symbol, order_id) - for a single order")
    logger.info("  client.cancel_all_orders(symbol) - for all orders on a symbol")
    
    # Test 8: Cancel-Replace Simulation
    print_test_header("Cancel-Replace Order Simulation (No Actual Orders)")
    logger.info("This test would demonstrate cancel-replace functionality")
    logger.info(f"{Fore.YELLOW}For safety, we're not actually replacing any orders during diagnostics")
    logger.info("To replace an order, you would use:")
    logger.info("  client.cancel_replace_order(symbol, cancel_replace_mode, side, type, cancel_order_id)")
    
    # Summary
    logger.info("\nOrder API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting open orders")
    logger.info("2. Getting order rate limits")
    logger.info("3. Testing order creation API (no actual orders)")
    logger.info("4. Getting trade history")
    logger.info("5. Getting order history")
    logger.info("6. Getting prevented matches")
    logger.info("7. Cancel order simulation (no actual cancellation)")
    logger.info("8. Cancel-replace simulation (no actual orders)")
    
    logger.info(f"\n{Fore.YELLOW}Note: This diagnostic only tested read-only operations and API connectivity.")
    logger.info(f"{Fore.YELLOW}No orders were placed, canceled, or modified during this test.")
    logger.info(f"{Fore.YELLOW}To enable full testing, provide valid API credentials with trading permissions.")
    
    logger.info("\nOrder API diagnostic completed. Check the logs above for any errors.")

if __name__ == "__main__":
    main()