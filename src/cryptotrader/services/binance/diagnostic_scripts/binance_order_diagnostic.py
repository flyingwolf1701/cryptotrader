#!/usr/bin/env python
"""
Binance Order Diagnostic Script
------------------------------
Tests the Binance order operations to verify order functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/binance_order_diagnostic.py

IMPORTANT: This script does not actually place or cancel any orders by default.
           Uncomment the relevant sections only if you want to perform real order operations.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger, Secrets
from cryptotrader.services.binance import Client
from cryptotrader.services.binance.binance_models import OrderRequest, OrderType, OrderSide, TimeInForce

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
    
    # Test 1: Get exchange info for BTC/USDT
    logger.info("\nTest 1: Getting exchange info for BTC/USDT...")
    symbol_info = client.get_symbol_info("BTCUSDT")
    if symbol_info:
        logger.info(f"Symbol: {symbol_info.symbol}")
        logger.info(f"Status: {symbol_info.status}")
        logger.info(f"Base Asset: {symbol_info.baseAsset}")
        logger.info(f"Quote Asset: {symbol_info.quoteAsset}")
        logger.info(f"Base Asset Precision: {symbol_info.baseAssetPrecision}")
        logger.info(f"Quote Precision: {symbol_info.quotePrecision}")
        logger.info(f"Order Types: {[ot for ot in symbol_info.orderTypes]}")
    else:
        logger.error("Failed to retrieve BTC/USDT symbol info")
    
    # Test 2: Get account balance
    logger.info("\nTest 2: Getting account balance...")
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
    
    # Test 3: Prepare a limit order (but don't place it)
    logger.info("\nTest 3: Preparing a limit order for BTC/USDT (simulation only)...")
    
    # Get current price to set a reasonable limit price
    ticker = client.get_ticker_price("BTCUSDT")
    if ticker:
        current_price = float(ticker.price)
        # Set a buy limit price 5% below current price
        limit_price = current_price * 0.95
        logger.info(f"Current BTC/USDT price: ${current_price:.2f}")
        logger.info(f"Would set limit buy price at: ${limit_price:.2f}")
        
        # Create an order request (but don't place it)
        order_request = OrderRequest(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=0.001,  # Minimum BTC amount
            price=limit_price,
            time_in_force=TimeInForce.GTC
        )
        
        logger.info("Order request would be:")
        logger.info(f"  Symbol: {order_request.symbol}")
        logger.info(f"  Side: {order_request.side}")
        logger.info(f"  Type: {order_request.order_type}")
        logger.info(f"  Quantity: {order_request.quantity}")
        logger.info(f"  Price: ${order_request.price:.2f}")
        logger.info(f"  Time in Force: {order_request.time_in_force}")
        
        # To actually place the order, uncomment the following lines:
        # logger.info("Placing order...")
        # order_response = client.place_order(order_request)
        # if order_response:
        #     logger.info(f"Order placed successfully. Order ID: {order_response.orderId}")
        #     
        #     # To check the order status:
        #     # status = client.get_order_status("BTCUSDT", order_id=order_response.orderId)
        #     # logger.info(f"Order status: {status.status if status else 'Unknown'}")
        #     
        #     # To cancel the order:
        #     # logger.info("Cancelling order...")
        #     # cancel_response = client.cancel_order("BTCUSDT", order_id=order_response.orderId)
        #     # if cancel_response:
        #     #     logger.info(f"Order cancelled successfully. Status: {cancel_response.status}")
        # else:
        #     logger.error("Failed to place order")
    else:
        logger.error("Failed to retrieve current BTC/USDT price")
    
    logger.info("\nDiagnostic complete. No actual orders were placed.")

if __name__ == "__main__":
    main()