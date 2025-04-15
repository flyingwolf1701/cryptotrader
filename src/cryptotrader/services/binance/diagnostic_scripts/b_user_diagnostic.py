"""
Binance User API Diagnostic Script
----------------------------------
Tests the Binance User API client to verify connectivity and information retrieval.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/b_user_diagnostic.py
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent  # src directory
sys.path.insert(0, str(project_root))

# Import our modules
from cryptotrader.config import get_logger
from cryptotrader.services.binance.binance_user_api import UserClient

logger = get_logger(__name__)

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance User client...")
    client = UserClient()  # No need to pass API credentials, handled by base operations
    
    # Test 1: Get account information
    logger.info("\nTest 1: Getting account information...")
    try:
        account = client.get_account()
        if account and account.assets:
            logger.info("Account information retrieved successfully")
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
            logger.warning("No account data retrieved or empty response")
    except Exception as e:
        logger.error(f"Error retrieving account information: {str(e)}")
    
    # Test 2: Get account status
    logger.info("\nTest 2: Getting account status...")
    try:
        status = client.get_account_status()
        if status:
            logger.info(f"Account status: {status.get('msg', 'Unknown')}")
            logger.info(f"Success: {status.get('success', False)}")
        else:
            logger.warning("No account status retrieved or empty response")
    except Exception as e:
        logger.error(f"Error retrieving account status: {str(e)}")
    
    # Test 3: Get API trading status
    logger.info("\nTest 3: Getting API trading status...")
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
            logger.warning("No API trading status retrieved or empty response")
    except Exception as e:
        logger.error(f"Error retrieving API trading status: {str(e)}")
    
    # Test 4: Get trading fee
    logger.info("\nTest 4: Getting trading fee for BTC/USDT...")
    try:
        fees = client.get_trade_fee(symbol="BTCUSDT")
        if fees and len(fees) > 0:
            for fee in fees:
                logger.info(f"Symbol: {fee.get('symbol')}")
                logger.info(f"  Maker commission: {fee.get('makerCommission')}")
                logger.info(f"  Taker commission: {fee.get('takerCommission')}")
        else:
            logger.warning("No trading fee data retrieved or empty response")
    except Exception as e:
        logger.error(f"Error retrieving trading fee: {str(e)}")
    
    # Test 5: Get trading volume
    logger.info("\nTest 5: Getting past 30 days trading volume...")
    try:
        volume = client.get_trading_volume()
        if volume:
            logger.info(f"Past 30 days trading volume: {volume.get('past30DaysTradingVolume', 'Unknown')}")
        else:
            logger.warning("No trading volume data retrieved or empty response")
    except Exception as e:
        logger.error(f"Error retrieving trading volume: {str(e)}")
    
    logger.info("\nUser API diagnostic completed.")

if __name__ == "__main__":
    main()