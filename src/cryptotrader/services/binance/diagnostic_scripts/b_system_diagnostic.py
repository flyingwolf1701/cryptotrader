"""
Binance System API Diagnostic Script
-----------------------------------
Tests the Binance System API client to verify connectivity and system information.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/b_system_diagnostic.py
"""

import sys
from pathlib import Path
import time
from datetime import datetime

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.binance_system_api import SystemClient

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance System client...")
    client = SystemClient()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get server time
    logger.info("\nTest 1: Getting server time...")
    server_time = client.get_server_time()
    local_time = int(time.time() * 1000)
    time_diff = abs(server_time - local_time)
    
    server_time_fmt = datetime.fromtimestamp(server_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
    local_time_fmt = datetime.fromtimestamp(local_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info(f"Server time: {server_time} ({server_time_fmt})")
    logger.info(f"Local time:  {local_time} ({local_time_fmt})")
    logger.info(f"Time difference: {time_diff} ms")
    
    if time_diff > 1000:
        logger.warning(f"Time difference is greater than 1 second! This may cause issues with signed requests.")
    else:
        logger.info("Time synchronization is good (under 1 second difference).")
    
    # Test 2: Get system status
    logger.info("\nTest 2: Checking system status...")
    system_status = client.get_system_status()
    logger.info(f"System status: {system_status.status_description} (code: {system_status.status_code})")
    
    if system_status.is_normal:
        logger.info("Binance system is operating normally.")
    elif system_status.is_maintenance:
        logger.warning("Binance system is under maintenance!")
    else:
        logger.error("Unknown system status!")
    
    # Test 3: Get available symbols
    logger.info("\nTest 3: Getting available trading symbols...")
    symbols = SystemClient.get_symbols_binance()
    logger.info(f"Retrieved {len(symbols)} trading symbols")
    
    # Show some popular symbols
    popular = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
    available_popular = [s for s in popular if s in symbols]
    logger.info(f"Popular symbols available: {', '.join(available_popular)}")
    
    # Sample of 5 random symbols
    import random
    if len(symbols) >= 5:
        sample = random.sample(symbols, 5)
        logger.info(f"Sample of 5 random symbols: {', '.join(sample)}")
    
    # Test 4: Get exchange information for a specific symbol
    logger.info("\nTest 4: Getting exchange info for BTC/USDT...")
    symbol_info = client.get_symbol_info("BTCUSDT")
    if symbol_info:
        logger.info(f"Symbol: {symbol_info.symbol}")
        logger.info(f"Status: {symbol_info.status}")
        logger.info(f"Base Asset: {symbol_info.baseAsset}")
        logger.info(f"Quote Asset: {symbol_info.quoteAsset}")
        logger.info(f"Base Asset Precision: {symbol_info.baseAssetPrecision}")
        logger.info(f"Quote Precision: {symbol_info.quotePrecision}")
        logger.info(f"Order Types: {', '.join([ot.value for ot in symbol_info.orderTypes])}")
    else:
        logger.error("Failed to retrieve symbol information for BTCUSDT")
    
    # Test 5: Get self-trade prevention modes
    logger.info("\nTest 5: Getting self-trade prevention modes...")
    stp_modes = client.get_self_trade_prevention_modes()
    if stp_modes:
        logger.info(f"Default self-trade prevention mode: {stp_modes.get('default', 'None')}")
        logger.info(f"Allowed modes: {', '.join(stp_modes.get('allowed', []))}")
    else:
        logger.error("Failed to retrieve self-trade prevention modes")
    
    logger.info("\nSystem API diagnostic completed.")

if __name__ == "__main__":
    main()