"""
Binance REST Order API Diagnostic Script
----------------------------------------
Tests the Binance API order-related endpoints to verify functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/test_scripts/diagnostic_b_rest_order.py

Note:
    This script is for diagnostic purposes only and does not place actual orders.
    It validates that the order endpoints are accessible and responsive.
"""

import sys
from pathlib import Path
import uuid

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
    
    logger.info("Initializing Binance client...")
    client = RestClient(api_key, api_secret)
    
    # Test 1: Check if we can query order status (with a fake order ID)
    logger.info("\nTest 1: Querying non-existent order status...")
    fake_order_id = 12345678
    order_status = client.get_order_status("BTCUSDT", order_id=fake_order_id)
    if order_status is None:
        logger.info("Expected behavior: Order not found (None returned)")
    else:
        logger.warning(f"Unexpected response when querying fake order: {order_status}")
    
    # Test 2: Create an order request object (but don't submit it)
    logger.info("\nTest 2: Creating order request object...")
    # Generate a unique client order ID to avoid conflicts
    client_order_id = f"test_{uuid.uuid4().hex[:16]}"
    
    # Create a limit order request (without actually placing it)
    order_request = OrderRequest(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=0.001,  # Minimal BTC amount
        price=10000.0,   # Very low price (won't execute)
        time_in_force=TimeInForce.GTC,
        new_client_order_id=client_order_id
    )
    
    logger.info(f"Order request created:")
    logger.info(f"  Symbol: {order_request.symbol}")
    logger.info(f"  Side: {order_request.side.value}")
    logger.info(f"  Type: {order_request.order_type.value}")
    logger.info(f"  Quantity: {order_request.quantity}")
    logger.info(f"  Price: {order_request.price}")
    logger.info(f"  TimeInForce: {order_request.time_in_force.value}")
    logger.info(f"  ClientOrderId: {order_request.new_client_order_id}")
    
    logger.info("\nDiagnostic complete. No actual orders were placed.")
    logger.info("To place real orders, implement additional code to call client.place_order()")

if __name__ == "__main__":
    main()