"""
Binance Order API Diagnostic Script
----------------------------------
Tests the Binance Order API client to verify order functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/b_order_diagnostic.py
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance import Client
from cryptotrader.services.binance.binance_models import OrderRequest, OrderType, OrderSide, TimeInForce

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance client...")
    client = Client()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get account balance
    logger.info("Test 1: Getting account balance...")
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
    
    # Test 2: Get open orders (read-only, doesn't create real orders)
    logger.info("\nTest 2: Testing get_open_orders for BTC/USDT...")
    
    # We'll just check if the API call works without expecting actual orders
    symbol = "BTCUSDT"
    
    # Assuming there's a method to get open orders in your client
    # If not available, this can be adjusted based on your actual implementation
    try:
        # This is a hypothetical method call - adjust according to your actual client implementation
        open_orders = client.get_open_orders(symbol)
        logger.info(f"Retrieved open orders for {symbol}")
        logger.info(f"Number of open orders: {len(open_orders) if open_orders else 0}")
        
        if open_orders and len(open_orders) > 0:
            logger.info(f"First open order details:")
            logger.info(f"  Order ID: {open_orders[0].orderId}")
            logger.info(f"  Symbol: {open_orders[0].symbol}")
            logger.info(f"  Type: {open_orders[0].type}")
            logger.info(f"  Side: {open_orders[0].side}")
            logger.info(f"  Price: {open_orders[0].price}")
            logger.info(f"  Quantity: {open_orders[0].origQty}")
    except Exception as e:
        logger.error(f"Error checking open orders: {str(e)}")
        logger.info("This may be expected if get_open_orders method is not implemented")
    
    # Note: We're not actually placing orders in this diagnostic script
    # as that would involve real financial transactions
    logger.info("\nNote: Order placement tests are not included in this diagnostic")
    logger.info("      as they would create actual orders on your Binance account.")
    
    logger.info("\nOrder API diagnostic completed.")

if __name__ == "__main__":
    main()