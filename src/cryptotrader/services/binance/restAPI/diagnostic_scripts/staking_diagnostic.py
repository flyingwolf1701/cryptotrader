"""
Binance Staking API Diagnostic Script
-----------------------------------
Tests the Binance Staking API client to verify connectivity and functionality.

Usage:
    To run this script from the project root directory:
    python src/cryptotrader/services/binance/diagnostic_scripts/staking_diagnostic.py
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
from cryptotrader.services.binance.restAPI import StakingOperations

logger = get_logger(__name__)

# Test constants
TEST_ASSET = "BNB"  # Common staking asset
TEST_AMOUNT = 0.1  # Small amount for testing


def print_test_header(test_name):
    """Print a test header in cyan color"""
    logger.info(f"\n{Fore.CYAN}Test: {test_name}{Style.RESET_ALL}")


def main():
    logger.info(f"Added {project_root} to Python path")

    logger.info("Initializing Binance Staking client...")
    client = StakingOperations()  # No need to pass API credentials

    # Test 1: Get staking asset information
    print_test_header("Getting Staking Asset Information")
    try:
        staking_assets = client.getStakingAssetInfo(TEST_ASSET)

        if staking_assets:
            logger.info(f"{Fore.GREEN}Retrieved staking information for {TEST_ASSET}")

            for i, asset in enumerate(staking_assets):
                logger.info(f"  Asset Details:")
                logger.info(f"    Staking Asset: {asset.stakingAsset}")
                logger.info(f"    Reward Asset: {asset.rewardAsset}")
                logger.info(f"    APR: {asset.apr}")
                logger.info(f"    APY: {asset.apy}")
                logger.info(f"    Unstaking Period: {asset.unstakingPeriod} hours")
                logger.info(f"    Min Staking Limit: {asset.minStakingLimit}")
                logger.info(f"    Max Staking Limit: {asset.maxStakingLimit}")
                logger.info(f"    Auto Restake: {asset.autoRestake}")
        else:
            logger.info(
                f"{Fore.YELLOW}No staking information retrieved or authentication required"
            )
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving staking asset information: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 2: Stake Asset Simulation
    print_test_header("Stake Asset Simulation (No Actual Staking)")
    try:
        logger.info(f"Would stake {TEST_AMOUNT} {TEST_ASSET}")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually staking during diagnostic")

        # Explain the request
        logger.info("\nA staking request would require:")
        logger.info(f"  - Staking Asset: {TEST_ASSET}")
        logger.info(f"  - Amount: {TEST_AMOUNT}")
        logger.info(f"  - Auto Restake: true (default)")

        # Try to make request if API key is available (will likely fail without valid credentials)
        logger.info(
            "\nAttempting to make a test stake request (will likely fail without valid API credentials)..."
        )
        try:
            staking_result = client.stake(
                staking_asset=TEST_ASSET, amount=TEST_AMOUNT, auto_restake=True
            )

            if staking_result:
                logger.info(f"{Fore.GREEN}Staking request successful")
                logger.info(f"  Result: {staking_result.result}")
                logger.info(f"  Purchase Record ID: {staking_result.purchaseRecordId}")
            else:
                logger.warning(
                    f"{Fore.YELLOW}Staking request failed - API credentials might be missing or invalid"
                )
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not make stake request: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in stake simulation: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 3: Unstake Asset Simulation
    print_test_header("Unstake Asset Simulation (No Actual Unstaking)")
    try:
        logger.info(f"Would unstake {TEST_AMOUNT} {TEST_ASSET}")
        logger.info(f"{Fore.YELLOW}NOTE: Not actually unstaking during diagnostic")

        # Explain the request
        logger.info("\nAn unstaking request would require:")
        logger.info(f"  - Staking Asset: {TEST_ASSET}")
        logger.info(f"  - Amount: {TEST_AMOUNT}")

        # Try to make request if API key is available (will likely fail without valid credentials)
        logger.info(
            "\nAttempting to make a test unstake request (will likely fail without valid API credentials)..."
        )
        try:
            unstaking_result = client.unstake(
                staking_asset=TEST_ASSET, amount=TEST_AMOUNT
            )

            if unstaking_result:
                logger.info(f"{Fore.GREEN}Unstaking request successful")
                logger.info(f"  Result: {unstaking_result.result}")
            else:
                logger.warning(
                    f"{Fore.YELLOW}Unstaking request failed - API credentials might be missing or invalid"
                )
        except Exception as e:
            logger.warning(f"{Fore.YELLOW}Could not make unstake request: {str(e)}")
    except Exception as e:
        logger.error(f"{Fore.RED}Error in unstake simulation: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 4: Get Staking Balance
    print_test_header("Getting Staking Balance")
    try:
        staking_balance = client.getStakingBalance(TEST_ASSET)

        if staking_balance:
            logger.info(f"{Fore.GREEN}Retrieved staking balance for {TEST_ASSET}")
            logger.info(f"  Code: {staking_balance.code}")
            logger.info(f"  Message: {staking_balance.message}")
            logger.info(f"  Success: {staking_balance.success}")
            logger.info(f"  Status: {', '.join(staking_balance.status)}")

            if staking_balance.data:
                for i, balance in enumerate(staking_balance.data):
                    logger.info(f"  Balance {i + 1}:")
                    logger.info(f"    Asset: {balance.asset}")
                    logger.info(f"    Staking Amount: {balance.stakingAmount}")
                    logger.info(f"    Reward Asset: {balance.rewardAsset}")
                    logger.info(f"    APR: {balance.apr}")
                    logger.info(f"    APY: {balance.apy}")
                    logger.info(f"    Auto Restake: {balance.autoRestake}")
            else:
                logger.info(f"  No staking balance data found")
        else:
            logger.info(
                f"{Fore.YELLOW}No staking balance retrieved or authentication required"
            )
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving staking balance: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 5: Get Staking History
    print_test_header("Getting Staking History")
    try:
        # Get staking history for the past 30 days
        end_time = int(time.time() * 1000)
        start_time = end_time - (30 * 24 * 60 * 60 * 1000)  # 30 days ago

        staking_history = client.getStakingHistory(
            asset=TEST_ASSET, start_time=start_time, end_time=end_time, limit=10
        )

        if staking_history:
            logger.info(
                f"{Fore.GREEN}Retrieved {len(staking_history)} staking history records for {TEST_ASSET}"
            )

            for i, record in enumerate(staking_history[:5]):  # Show up to 5 records
                record_time = datetime.fromtimestamp(
                    record.initiatedTime / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"  Record {i + 1}:")
                logger.info(f"    Asset: {record.asset}")
                logger.info(f"    Amount: {record.amount}")
                logger.info(f"    Type: {record.type}")
                logger.info(f"    Time: {record_time}")
                logger.info(f"    Status: {record.status}")
        else:
            logger.info(
                f"{Fore.YELLOW}No staking history retrieved or authentication required"
            )
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving staking history: {str(e)}")
        logger.debug(traceback.format_exc())

    # Test 6: Get Staking Rewards History
    print_test_header("Getting Staking Rewards History")
    try:
        # Get rewards history for the past 30 days
        end_time = int(time.time() * 1000)
        start_time = end_time - (30 * 24 * 60 * 60 * 1000)  # 30 days ago

        rewards_history = client.getStakingRewardsHistory(
            asset=TEST_ASSET, start_time=start_time, end_time=end_time, limit=10
        )

        if rewards_history:
            logger.info(
                f"{Fore.GREEN}Retrieved staking rewards history for {TEST_ASSET}"
            )
            logger.info(f"  Code: {rewards_history.code}")
            logger.info(f"  Message: {rewards_history.message}")
            logger.info(f"  Success: {rewards_history.success}")
            logger.info(f"  Total: {rewards_history.total}")

            if rewards_history.data:
                for i, reward in enumerate(
                    rewards_history.data[:5]
                ):  # Show up to 5 rewards
                    reward_time = datetime.fromtimestamp(reward.time / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    logger.info(f"  Reward {i + 1}:")
                    logger.info(f"    Asset: {reward.asset}")
                    logger.info(f"    Amount: {reward.amount}")
                    logger.info(f"    USD Value: {reward.usdValue}")
                    logger.info(f"    Time: {reward_time}")
                    logger.info(f"    Transaction ID: {reward.tranId}")
                    logger.info(f"    Auto Restaked: {reward.autoRestaked}")
            else:
                logger.info(f"  No rewards data found")
        else:
            logger.info(
                f"{Fore.YELLOW}No staking rewards history retrieved or authentication required"
            )
    except Exception as e:
        logger.error(f"{Fore.RED}Error retrieving staking rewards history: {str(e)}")
        logger.debug(traceback.format_exc())

    # Summary
    logger.info("\nStaking API Diagnostic Summary:")
    logger.info("----------------------------")
    logger.info("The following tests were performed:")
    logger.info("1. Getting staking asset information")
    logger.info("2. Stake asset simulation (no actual staking)")
    logger.info("3. Unstake asset simulation (no actual unstaking)")
    logger.info("4. Getting staking balance")
    logger.info("5. Getting staking history")
    logger.info("6. Getting staking rewards history")

    logger.info(
        f"\n{Fore.YELLOW}Note: Most staking operations require valid API credentials with staking permissions."
    )
    logger.info(
        f"{Fore.YELLOW}This diagnostic primarily tested API connectivity and structure."
    )

    logger.info(
        "\nStaking API diagnostic completed. Check the logs above for any errors."
    )


if __name__ == "__main__":
    main()
