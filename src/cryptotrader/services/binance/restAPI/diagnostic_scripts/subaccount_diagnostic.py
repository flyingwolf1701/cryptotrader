"""
Binance Sub-Account API Diagnostic Script
----------------------------------------
Tests the Binance Sub-Account API client to verify connectivity and functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/subaccount_diagnostic.py
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
from cryptotrader.services.binance.restAPI import SubAccountOperations

logger = get_logger(__name__)

def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")

def main():
    logger.info(f"Added {project_root} to Python path")
    
    logger.info("Initializing Binance Sub-Account client...")
    client = SubAccountOperations()  # No need to pass API credentials
    
    # Test 1: Get sub-account list
    print_test_header("Getting sub-account list")
    try:
        subaccount_list = client.get_subaccount_list()
        if subaccount_list and subaccount_list.get('success'):
            sub_accounts = subaccount_list.get('subAccounts', [])
            logger.info(f"{Fore.GREEN}Retrieved {len(sub_accounts)} sub-accounts")
            
            if sub_accounts:
                logger.info("First sub-account details:")
                first_account = sub_accounts[0]
                logger.info(f"  Email: {first_account.get('email')}")
                logger.info(f"  Status: {first_account.get('status')}")
                logger.info(f"  Activated: {first_account.get('activated')}")
                logger.info(f"  Create Time: {first_account.get('createTime')}")
            else:
                logger.info("No sub-accounts found")
        else:
            logger.warning(f"{Fore.YELLOW}No sub-account list retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving sub-account list: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 2: Get sub-account transfer history
    print_test_header("Getting sub-account transfer history")
    try:
        transfer_history = client.get_subaccount_transfer_history()
        if transfer_history and transfer_history.get('success'):
            transfers = transfer_history.get('transfers', [])
            logger.info(f"{Fore.GREEN}Retrieved {len(transfers)} transfer records")
            
            if transfers:
                logger.info("Recent transfer details:")
                recent_transfer = transfers[0]
                logger.info(f"  Asset: {recent_transfer.get('asset')}")
                logger.info(f"  From: {recent_transfer.get('from')}")
                logger.info(f"  To: {recent_transfer.get('to')}")
                logger.info(f"  Quantity: {recent_transfer.get('qty')}")
                logger.info(f"  Time: {recent_transfer.get('time')}")
            else:
                logger.info("No transfer records found")
        else:
            logger.warning(f"{Fore.YELLOW}No transfer history retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving sub-account transfer history: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Note about sub-account tests requiring specific emails
    logger.info(f"\n{Fore.YELLOW}Note: The following tests require specific sub-account emails.")
    logger.info(f"{Fore.YELLOW}Since these are specific to your account, tests will show errors without valid email addresses.")
    logger.info(f"{Fore.YELLOW}This is expected behavior without valid email addresses.")
    
    # Test 3: Get sub-account assets (would require a valid email)
    print_test_header("Getting sub-account assets")
    try:
        # Using a placeholder email - this will likely fail
        assets = client.get_subaccount_assets(email="example@example.com")
        if assets and assets.get('success'):
            balances = assets.get('balances', [])
            logger.info(f"{Fore.GREEN}Retrieved {len(balances)} asset balances")
            
            if balances:
                logger.info("Asset balances:")
                for balance in balances[:5]:  # Show first 5 only
                    logger.info(f"  {balance.get('asset')}: Free={balance.get('free')}, Locked={balance.get('locked')}")
            else:
                logger.info("No asset balances found")
        else:
            logger.warning(f"{Fore.YELLOW}No sub-account assets retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving sub-account assets: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 4: Get master account total value
    print_test_header("Getting master account total value")
    try:
        total_value = client.get_master_account_total_value()
        if total_value:
            logger.info(f"Master account total asset: {total_value.get('masterAccountTotalAsset', 'Unknown')}")
            logger.info(f"Total count: {total_value.get('totalCount', 'Unknown')}")
            
            sub_user_assets = total_value.get('spotSubUserAssetBtcVoList', [])
            if sub_user_assets:
                logger.info("Sub-account assets:")
                for sub_asset in sub_user_assets[:5]:  # Show first 5 only
                    logger.info(f"  {sub_asset.get('email')}: Total Asset={sub_asset.get('totalAsset')}")
            else:
                logger.info("No sub-account asset information found")
        else:
            logger.warning(f"{Fore.YELLOW}No master account total value retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving master account total value: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Test 5: Get sub-account status list (would require a valid email)
    print_test_header("Getting sub-account status list")
    try:
        # Using a placeholder email - this will likely fail
        status_list = client.get_subaccount_status_list(email="example@example.com")
        if status_list:
            logger.info(f"{Fore.GREEN}Retrieved {len(status_list)} status records")
            
            if len(status_list) > 0:
                logger.info("Status details:")
                for status in status_list[:5]:  # Show first 5 only
                    logger.info(f"  Email: {status.get('email')}")
                    logger.info(f"  Is User Active: {status.get('isUserActive')}")
                    logger.info(f"  Is Margin Enabled: {status.get('isMarginEnabled')}")
                    logger.info(f"  Is Sub User Enabled: {status.get('isSubUserEnabled')}")
            else:
                logger.info("No status records found")
        else:
            logger.warning(f"{Fore.YELLOW}No sub-account status list retrieved or empty response")
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving sub-account status list: {str(e)}")
        logger.debug(traceback.format_exc())
    
    # Note about transfer execution
    logger.info(f"\n{Fore.YELLOW}Note: The execute_subaccount_transfer method is not tested")
    logger.info(f"{Fore.YELLOW}as it would involve actual asset transfers.")
    
    # Summary
    logger.info("\nSub-Account API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting sub-account list")
    logger.info("2. Getting sub-account transfer history")
    logger.info("3. Getting sub-account assets (using placeholder email)")
    logger.info("4. Getting master account total value")
    logger.info("5. Getting sub-account status list (using placeholder email)")
    
    logger.info("\nNote: Tests 3 and 5 are expected to fail without valid sub-account emails.")
    logger.info("These tests are included to demonstrate the API functionality but require")
    logger.info("valid sub-account emails to work properly.")
    
    logger.info("\nSub-Account API diagnostic completed. Check the logs above for any errors.")

if __name__ == "__main__":
    main()