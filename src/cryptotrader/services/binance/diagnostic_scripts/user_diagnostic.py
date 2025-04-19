"""
Binance User API Diagnostic Script
----------------------------------
Tests the Binance User API client to verify connectivity and information retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/user_diagnostic.py
"""

import sys
import traceback
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.user_api import UserOperations

logger = get_logger(__name__)

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance User client...")
    client = UserOperations()  # No need to pass API credentials
    
    # Test 1: Get account information
    print_test_header("Getting account information")
    try:
        account = client.get_account()
        if account and account.assets:
            logger.info(f"{Fore.GREEN}Account information retrieved successfully")
            # Print assets with non-zero balances
            non_zero_assets = {asset: data for asset, data in account.assets.items() 
                             if float(data.free) > 0 or float(data.locked) > 0}
            
            if non_zero_assets:
                logger.info("Assets with non-zero balance:")
                for asset, data in non_zero_assets.items():
                    logger.info(f"  {asset}: Free={data.free}, Locked={data.locked}")
            else:
                logger.info("No assets with non-zero balance found")
        else:
            logger.warning(f"{Fore.YELLOW}No account data retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving account information: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 2: Get account status
    print_test_header("Getting account status")
    try:
        status = client.get_account_status()
        if status:
            logger.info(f"Account status: {status.get('msg', 'Unknown')}")
            logger.info(f"Success: {status.get('success', False)}")
        else:
            logger.warning(f"{Fore.YELLOW}No account status retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving account status: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 3: Get API trading status
    print_test_header("Getting API trading status")
    try:
        trading_status = client.get_api_trading_status()
        if trading_status and trading_status.get('success'):
            status_details = trading_status.get('status', {})
            logger.info(f"API trading locked: {status_details.get('isLocked', False)}")
            logger.info(f"Update time: {status_details.get('updateTime', 0)}")
            
            # Get some indicators if available
            indicators = status_details.get('indicators', {})
            for symbol, indicator_list in indicators.items():
                logger.info(f"Indicators for {symbol}:")
                for indicator in indicator_list:
                    logger.info(f"  {indicator.get('i')}: Value={indicator.get('v')}, Trigger={indicator.get('t')}")
        else:
            logger.warning(f"{Fore.YELLOW}No API trading status retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving API trading status: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 4: Get trading fee
    print_test_header("Getting trading fee for BTC/USDT")
    try:
        fees = client.get_trade_fee(symbol="BTCUSDT")
        if fees and len(fees) > 0:
            for fee in fees:
                logger.info(f"Symbol: {fee.get('symbol')}")
                logger.info(f"  Maker commission: {fee.get('makerCommission')}")
                logger.info(f"  Taker commission: {fee.get('takerCommission')}")
        else:
            logger.warning(f"{Fore.YELLOW}No trading fee data retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving trading fee: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 5: Get trading volume
    print_test_header("Getting past 30 days trading volume")
    try:
        volume = client.get_trading_volume()
        if volume:
            logger.info(f"Past 30 days trading volume: {volume.get('past30DaysTradingVolume', 'Unknown')}")
        else:
            logger.warning(f"{Fore.YELLOW}No trading volume data retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving trading volume: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 6: Get asset distribution history
    print_test_header("Getting asset distribution history")
    try:
        distribution = client.get_asset_distribution_history(limit=5)
        if distribution and distribution.get('success'):
            distributions = distribution.get('results', [])
            logger.info(f"Retrieved {len(distributions)} asset distributions")
            
            for i, dist in enumerate(distributions[:3]):  # Show first 3
                logger.info(f"Distribution {i+1}:")
                logger.info(f"  Asset: {dist.get('asset', 'Unknown')}")
                logger.info(f"  Amount: {dist.get('amount', 'Unknown')}")
                logger.info(f"  Category: {dist.get('category', 'Unknown')}")
                logger.info(f"  Time: {dist.get('time', 'Unknown')}")
        else:
            logger.warning(f"{Fore.YELLOW}No asset distribution history retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving asset distribution history: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Summary
    logger.info("\nUser API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting account information")
    logger.info("2. Getting account status")
    logger.info("3. Getting API trading status")
    logger.info("4. Getting trading fee for BTC/USDT")
    logger.info("5. Getting past 30 days trading volume")
    logger.info("6. Getting asset distribution history")
    
    logger.info("\nNote: Some operations may fail if your API key doesn't have sufficient permissions")
    logger.info("or if you're using public-only access.")
    
    logger.info("\nUser API diagnostic completed. Check the logs above for any errors.")

if __name__ == "__main__":
    main()