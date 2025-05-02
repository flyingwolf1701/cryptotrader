"""
Binance Staking API Client

This module provides a client for interacting with the Binance staking API endpoints.
It includes functionality for:
- Getting staking asset information
- Staking and unstaking assets
- Retrieving staking balances
- Getting staking and rewards history

These endpoints provide staking functionality for earning rewards on supported assets.
"""

from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.baseOperations import BinanceAPIRequest
from cryptotrader.services.binance.models import (
    StakingAssetInfo,
    StakingOperationResult,
    StakingStakeResult,
    StakingUnstakeResult,
    StakingBalanceResponse,
    StakingHistoryItem,
    StakingRewardsResponse,
    RateLimitType,
)

logger = get_logger(__name__)


class StakingOperations:
    """
    Binance staking operations API client implementation.

    Provides methods for managing staking operations including asset information,
    staking/unstaking, and retrieving balances and history.
    """

    def __init__(self):
        """Initialize the Staking operations client."""
        pass

    def request(
        self,
        method: str,
        endpoint: str,
        limit_type: Optional[RateLimitType] = None,
        weight: int = 1,
    ) -> BinanceAPIRequest:
        """
        Create a new API request.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            limit_type: Type of rate limit for this request
            weight: Weight of this request for rate limiting

        Returns:
            BinanceAPIRequest object for building and executing the request
        """
        return BinanceAPIRequest(
            method=method, endpoint=endpoint, limit_type=limit_type, weight=weight
        )

    def getStakingAssetInfo(
        self, staking_asset: Optional[str] = None
    ) -> List[StakingAssetInfo]:
        """
        Get staking information for a supported asset (or assets).

        GET /sapi/v1/staking/asset
        Weight: 1

        Args:
            staking_asset: Asset symbol (e.g. BNB). If empty, returns all staking assets

        Returns:
            List of StakingAssetInfo objects
        """
        request = self.request(
            "GET", "/sapi/v1/staking/asset", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if staking_asset:
            request.withQueryParams(stakingAsset=staking_asset)

        response = request.execute()

        asset_info_list = []
        if response:
            for assetData in response:
                asset_info_list.append(StakingAssetInfo.from_api_response(assetData))

        return asset_info_list

    def stake(
        self,
        staking_asset: str,
        amount: Union[str, float],
        auto_restake: Optional[bool] = True,
    ) -> Optional[StakingStakeResult]:
        """
        Stake a supported asset.

        POST /sapi/v1/staking/stake
        Weight: 1

        Args:
            staking_asset: Asset symbol (e.g. BNB)
            amount: Staking amount
            auto_restake: If need auto restaking - default: true

        Returns:
            StakingStakeResult object with the stake result, or None if the request failed
        """
        request = (
            self.request(
                "POST", "/sapi/v1/staking/stake", RateLimitType.REQUEST_WEIGHT, 1
            )
            .requiresAuth(True)
            .withQueryParams(
                stakingAsset=staking_asset,
                amount=str(amount),  # Ensure amount is a string
            )
        )

        # Include autoRestake parameter
        if auto_restake is not None:
            request.withQueryParams(
                autoRestake=str(auto_restake).lower()
            )  # Convert boolean to lowercase string

        response = request.execute()

        if response:
            return StakingStakeResult.from_api_response(response)
        return None

    def unstake(
        self, staking_asset: str, amount: Union[str, float]
    ) -> Optional[StakingUnstakeResult]:
        """
        Unstake a staked asset.

        POST /sapi/v1/staking/unstake
        Weight: 1

        Args:
            staking_asset: Asset symbol (e.g. BNB)
            amount: Unstaking amount

        Returns:
            StakingUnstakeResult object with the unstake result, or None if the request failed
        """
        response = (
            self.request(
                "POST", "/sapi/v1/staking/unstake", RateLimitType.REQUEST_WEIGHT, 1
            )
            .requiresAuth(True)
            .withQueryParams(
                stakingAsset=staking_asset,
                amount=str(amount),  # Ensure amount is a string
            )
            .execute()
        )

        if response:
            return StakingUnstakeResult.from_api_response(response)
        return None

    def getStakingBalance(
        self, asset: Optional[str] = None
    ) -> Optional[StakingBalanceResponse]:
        """
        Get the staking balance for an asset (or assets).

        GET /sapi/v1/staking/stakingBalance
        Weight: 1

        Args:
            asset: Staked asset. If empty, returns all assets with balances.

        Returns:
            StakingBalanceResponse object with balance information, or None if the request failed
        """
        request = self.request(
            "GET", "/sapi/v1/staking/stakingBalance", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if asset:
            request.withQueryParams(asset=asset)

        response = request.execute()

        if response:
            return StakingBalanceResponse.from_api_response(response)
        return None

    def getStakingHistory(
        self,
        asset: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[StakingHistoryItem]:
        """
        Get the staking history of an asset (or assets) within a given time range.

        GET /sapi/v1/staking/history
        Weight: 1

        Args:
            asset: Asset symbol (e.g. BNB). If empty, returns all assets with history
            start_time: UNIX Timestamp
            end_time: UNIX Timestamp
            page: Page number - default: 1
            limit: Default value: 500 (each page contains at most 500 records)

        Returns:
            List of StakingHistoryItem objects
        """
        request = self.request(
            "GET", "/sapi/v1/staking/history", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if asset:
            request.withQueryParams(asset=asset)

        if start_time:
            request.withQueryParams(startTime=start_time)

        if end_time:
            request.withQueryParams(endTime=end_time)

        if page:
            request.withQueryParams(page=page)

        if limit:
            request.withQueryParams(
                limit=min(limit, 500)
            )  # Ensure limit doesn't exceed API max

        response = request.execute()

        history_items = []
        if response:
            for item_data in response:
                history_items.append(StakingHistoryItem.from_api_response(item_data))

        return history_items

    def getStakingRewardsHistory(
        self,
        asset: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[StakingRewardsResponse]:
        """
        Get the staking rewards history for an asset (or assets) within a given time range.

        GET /sapi/v1/staking/stakingRewardsHistory
        Weight: 1

        Args:
            asset: Staked asset. If empty, returns all assets with balances.
            start_time: Start time
            end_time: End time
            page: The transfer history batch number (max 500 records per batch)
            limit: Default value: 500

        Returns:
            StakingRewardsResponse object with rewards history, or None if the request failed
        """
        request = self.request(
            "GET",
            "/sapi/v1/staking/stakingRewardsHistory",
            RateLimitType.REQUEST_WEIGHT,
            1,
        ).requiresAuth(True)

        if asset:
            request.withQueryParams(asset=asset)

        if start_time:
            request.withQueryParams(startTime=start_time)

        if end_time:
            request.withQueryParams(endTime=end_time)

        if page:
            request.withQueryParams(page=page)

        if limit:
            request.withQueryParams(
                limit=min(limit, 500)
            )  # Ensure limit doesn't exceed API max

        response = request.execute()

        if response:
            return StakingRewardsResponse.from_api_response(response)
        return None
