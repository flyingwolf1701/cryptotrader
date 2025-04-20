"""
Binance OTC API Diagnostic Script
--------------------------------
Tests the Binance OTC (Over-The-Counter) API client to verify connectivity and functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/otc_diagnostic.py
"""

import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.otc_api import OtcOperations
from cryptotrader.services.binance.models.otc_models import OtcOrderStatus

logger = get_logger(__name__)

# Test constants
TEST_FROM_COIN = "BTC"
TEST_TO_COIN = "USDT"
TEST_REQUEST_AMOUNT = 0.1  # Small amount for testing

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance OTC client...")
    client = OtcOperations()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get supported coin pairs
    print_test_header("Getting Supported Coin Pairs")
    try:
        coin_pairs = client.get_coin_pairs()
        
        if coin_pairs:
            logger.info(f"{Fore.GREEN}Retrieved {len(coin_pairs)} supported OTC coin pairs")
            
            # Show some examples
            logger.info("Sample coin pairs:")
            for i, pair in enumerate(coin_pairs[:3]):  # Show up to 3 pairs
                logger.info(f"  Pair {i+1}: {pair.fromCoin} -> {pair.toCoin}")
                logger.info(f"    Min amount: {pair.fromCoinMinAmount} {pair.fromCoin} or {pair.toCoinMinAmount} {pair.toCoin}")
                logger.info(f"    Max amount: {pair.fromCoinMaxAmount} {pair.fromCoin} or {pair.toCoinMaxAmount} {pair.toCoin}")
        else:
            logger.info(f"{Fore.YELLOW}No coin pairs retrieved or authentication required")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving supported coin pairs: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 2: Request for Quote simulation
    print_test_header("Requesting OTC Quote (Simulation)")
    try:
        logger.info(f"Would request a quote for trading {TEST_REQUEST_AMOUNT} {TEST_FROM_COIN} to {TEST_TO_COIN}")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually requesting a quote during diagnostic")
        
        # Explain the request
        logger.info("\nA quote request would require:")
        logger.info(f"  - From Coin: {TEST_FROM_COIN}")
        logger.info(f"  - To Coin: {TEST_TO_COIN}")
        logger.info(f"  - Request Coin: {TEST_FROM_COIN}")
        logger.info(f"  - Request Amount: {TEST_REQUEST_AMOUNT}")
        
        # Try to make request if API key is available (will likely fail without valid credentials)
        logger.info("\nAttempting to request an actual quote (will likely fail without valid API credentials)...")
        try:
            quote = client.request_quote(
                from_coin=TEST_FROM_COIN,
                to_coin=TEST_TO_COIN,
                request_coin=TEST_FROM_COIN,
                request_amount=TEST_REQUEST_AMOUNT
            )
            
            if quote:
                logger.info(f"{Fore.GREEN}Successfully retrieved quote")
                logger.info(f"  Symbol: {quote.symbol}")
                logger.info(f"  Ratio: {quote.ratio}")
                logger.info(f"  From Amount: {quote.fromAmount} {TEST_FROM_COIN}")
                logger.info(f"  To Amount: {quote.toAmount} {TEST_TO_COIN}")
                logger.info(f"  Valid until: {datetime.fromtimestamp(quote.validTimestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logger.warning(f"{Fore.YELLOW}Failed to retrieve quote - API credentials might be missing or invalid")
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not request quote: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in quote request simulation: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 3: Place Order simulation
    print_test_header("Placing OTC Order (Simulation)")
    try:
        logger.info(f"Would place an OTC order using a previously obtained quote ID")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually placing any orders during diagnostic")
        
        # Explain the process
        logger.info("\nAn OTC order requires:")
        logger.info("  1. First getting a quote using the request_quote method")
        logger.info("  2. Using the returned quote ID to place the actual order")
        logger.info("  3. OTC orders execute at the quoted price rather than market price")
        
        logger.info("\nOrder placement workflow:")
        logger.info("  - Call client.place_order(quote_id)")
        logger.info("  - The returned order will have status: PROCESS, ACCEPT_SUCCESS, SUCCESS, or FAIL")
        logger.info("  - You can then check the order status using client.get_order(order_id)")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in order placement simulation: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 4: Get Order simulation
    print_test_header("Getting OTC Order (Simulation)")
    try:
        logger.info(f"Would retrieve details for a specific OTC order")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually retrieving orders during diagnostic")
        
        # Explain the process
        logger.info("\nTo retrieve an order:")
        logger.info("  - Call client.get_order(order_id)")
        logger.info("  - This returns detailed information about the order including status, amounts, and ratios")
        
        # Try to make request with a sample order ID (will fail)
        sample_order_id = "10002349"  # This is just for example
        logger.info(f"\nAttempting to query order {sample_order_id} (will likely fail without valid credentials)...")
        try:
            order = client.get_order(sample_order_id)
            
            if order:
                logger.info(f"{Fore.GREEN}Successfully retrieved order")
                logger.info(f"  Order ID: {order.orderId}")
                logger.info(f"  Status: {order.orderStatus}")
                logger.info(f"  From: {order.fromAmount} {order.fromCoin}")
                logger.info(f"  To: {order.toAmount} {order.toCoin}")
                logger.info(f"  Ratio: {order.ratio}")
            else:
                logger.warning(f"{Fore.YELLOW}Failed to retrieve order - API credentials might be missing or invalid")
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not retrieve order: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in get order simulation: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 5: List Orders simulation
    print_test_header("Listing OTC Orders (Simulation)")
    try:
        logger.info(f"Would retrieve a list of OTC orders")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually retrieving order lists during diagnostic")
        
        # Explain the process
        logger.info("\nTo list orders with filtering options:")
        logger.info("  - Call client.get_orders()")
        logger.info("  - Can filter by order_id, from_coin, to_coin, time period, etc.")
        logger.info("  - Pagination supported with page and limit parameters")
        
        # Try to make request (will likely fail without valid credentials)
        logger.info("\nAttempting to list recent orders (will likely fail without valid credentials)...")
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago
            
            orders = client.get_orders(
                start_time=start_time,
                end_time=end_time,
                limit=10
            )
            
            if orders:
                logger.info(f"{Fore.GREEN}Successfully retrieved orders list")
                logger.info(f"  Total orders: {orders.total}")
                
                if orders.rows:
                    logger.info("  Recent orders:")
                    for i, order in enumerate(orders.rows[:3]):  # Show up to 3 orders
                        order_time = datetime.fromtimestamp(order.createTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"    Order {i+1}: {order.fromCoin} -> {order.toCoin} (Status: {order.orderStatus}, Time: {order_time})")
                else:
                    logger.info("  No orders found in the specified time period")
            else:
                logger.warning(f"{Fore.YELLOW}Failed to retrieve orders list - API credentials might be missing or invalid")
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not retrieve orders list: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in list orders simulation: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 6: Get OCBS Orders simulation
    print_test_header("Listing OCBS Orders (Simulation)")
    try:
        logger.info(f"Would retrieve a list of OCBS orders")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually retrieving OCBS order lists during diagnostic")
        
        # Explain the process
        logger.info("\nTo list OCBS orders with filtering options:")
        logger.info("  - Call client.get_ocbs_orders()")
        logger.info("  - Can filter by order_id, time period, etc.")
        logger.info("  - Pagination supported with page and limit parameters")
        logger.info("  - OCBS orders include fee information (feeCoin, feeAmount)")
        
        # Try to make request (will likely fail without valid credentials)
        logger.info("\nAttempting to list OCBS orders (will likely fail without valid credentials)...")
        try:
            end_time = int(time.time() * 1000)
            start_time = end_time - (24 * 60 * 60 * 1000)  # 24 hours ago
            
            ocbs_orders = client.get_ocbs_orders(
                start_time=start_time,
                end_time=end_time,
                limit=10
            )
            
            if ocbs_orders:
                logger.info(f"{Fore.GREEN}Successfully retrieved OCBS orders list")
                logger.info(f"  Total orders: {ocbs_orders.total}")
                
                if ocbs_orders.dataList:
                    logger.info("  Recent OCBS orders:")
                    for i, order in enumerate(ocbs_orders.dataList[:3]):  # Show up to 3 orders
                        order_time = datetime.fromtimestamp(order.createTime / 1000).strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f"    Order {i+1}: {order.fromCoin} -> {order.toCoin} (Status: {order.orderStatus}, Time: {order_time})")
                        logger.info(f"      Fee: {order.feeAmount} {order.feeCoin}")
                else:
                    logger.info("  No OCBS orders found in the specified time period")
            else:
                logger.warning(f"{Fore.YELLOW}Failed to retrieve OCBS orders list - API credentials might be missing or invalid")
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not retrieve OCBS orders list: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in list OCBS orders simulation: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Summary
    logger.info("\nOTC API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting supported coin pairs")
    logger.info("2. Requesting OTC Quote (simulation)")
    logger.info("3. Placing OTC Order (simulation)")
    logger.info("4. Getting OTC Order (simulation)")
    logger.info("5. Listing OTC Orders (simulation)")
    logger.info("6. Listing OCBS Orders (simulation)")
    
    logger.info(f"\n{Fore.YELLOW}Note: Most OTC operations require valid API credentials with OTC trading permissions.")
    logger.info(f"{Fore.YELLOW}This diagnostic primarily tested API connectivity and some read operations.")
    
    logger.info("\nOTC API diagnostic completed. Check the logs above for any errors.")

if __name__ == "__main__":
    main()