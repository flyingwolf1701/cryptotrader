"""
Binance System API Diagnostic Script
-----------------------------------
Tests the Binance System API client to verify connectivity and system information.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/system_diagnostic.py
"""

import sys
from pathlib import Path
import time
import traceback
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI import SystemOperations

logger = get_logger(__name__)

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance System client...")
    client = SystemOperations()  # No need to pass API credentials
    
    # Test 1: Get server time
    print_test_header("Getting server time")
    try:
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = abs(server_time - local_time)
        
        server_time_fmt = datetime.fromtimestamp(server_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        local_time_fmt = datetime.fromtimestamp(local_time / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"Server time: {server_time} ({server_time_fmt})")
        logger.info(f"Local time:  {local_time} ({local_time_fmt})")
        logger.info(f"Time difference: {time_diff} ms")
        
        if time_diff > 1000:
            logger.warning(f"{Fore.YELLOW}Time difference is greater than 1 second! This may cause issues with signed requests.")
        else:
            logger.info(f"{Fore.GREEN}Time synchronization is good (under 1 second difference).")
    except Exception as e:
        logger.error(f"Error retrieving server time: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 2: Get system status
    print_test_header("Checking system status")
    try:
        system_status = client.get_system_status()
        logger.info(f"System status: {system_status.status_description} (code: {system_status.status_code})")
        
        if system_status.is_normal:
            logger.info(f"{Fore.GREEN}Binance system is operating normally.")
        elif system_status.is_maintenance:
            logger.warning(f"{Fore.YELLOW}Binance system is under maintenance!")
        else:
            logger.error(f"{Fore.RED}Unknown system status!")
    except Exception as e:
        logger.error(f"Error retrieving system status: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 3: Get available symbols
    print_test_header("Getting available trading symbols")
    try:
        symbols = client.get_symbols()
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
    except Exception as e:
        logger.error(f"Error retrieving trading symbols: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 4: Get exchange information for a specific symbol
    print_test_header("Getting exchange info for BTC/USDT")
    try:
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
    except Exception as e:
        logger.error(f"Error retrieving symbol information: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 5: Get self-trade prevention modes
    print_test_header("Getting self-trade prevention modes")
    try:
        stp_modes = client.get_self_trade_prevention_modes()
        if stp_modes:
            logger.info(f"Default self-trade prevention mode: {stp_modes.get('default', 'None')}")
            logger.info(f"Allowed modes: {', '.join(stp_modes.get('allowed', []))}")
        else:
            logger.error("Failed to retrieve self-trade prevention modes")
    except Exception as e:
        logger.error(f"Error retrieving self-trade prevention modes: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 6: Get full exchange information
    print_test_header("Getting complete exchange information")
    try:
        exchange_info = client.get_exchange_info()
        if exchange_info:
            logger.info(f"Exchange has {len(exchange_info.get('symbols', []))} trading pairs")
            logger.info(f"Exchange timezone: {exchange_info.get('timezone', 'Unknown')}")
            
            # Get rate limits if available
            if 'rateLimits' in exchange_info:
                logger.info(f"Rate limits configured: {len(exchange_info['rateLimits'])}")
                for i, limit in enumerate(exchange_info['rateLimits'][:3]):  # Show first 3 limits
                    limit_type = limit.get('rateLimitType', 'Unknown')
                    interval = limit.get('interval', 'Unknown')
                    limit_val = limit.get('limit', 0)
                    logger.info(f"  Limit {i+1}: {limit_type} - {limit_val} per {interval}")
        else:
            logger.error("Failed to retrieve exchange information")
    except Exception as e:
        logger.error(f"Error retrieving exchange information: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Summary
    logger.info("\nSystem API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting server time")
    logger.info("2. Checking system status")
    logger.info("3. Getting available trading symbols")
    logger.info("4. Getting exchange info for BTC/USDT")
    logger.info("5. Getting self-trade prevention modes")
    logger.info("6. Getting complete exchange information")
    
    logger.info("\nSystem API diagnostic completed. Check the logs above for any errors.")

if __name__ == "__main__":
    main()