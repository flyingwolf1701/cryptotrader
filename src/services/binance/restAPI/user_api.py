"""
Binance User Account API Client

This module provides a client for interacting with the Binance user account API endpoints.
It includes functionality for:
- Account information retrieval
- Account status checks
- API trading status information
- Asset distribution history
- Trading fee information
- Trading volume retrieval

These endpoints provide information about the user's account, permissions, and trading statistics.
"""

import json
from typing import Dict, List, Optional, Any, Union

from config import get_logger
from services.binance.restAPI.baseOperations import BinanceAPIRequest
from services.binance.models import AccountBalance, RateLimitType

logger = get_logger(__name__)


class UserOperations:
    """
    Binance user account API client implementation.

    Provides methods for retrieving information about the user's account,
    trading status, fee rates, and more.
    """

    def __init__(self):
        """Initialize the User client."""
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

    def get_account(
        self, recv_window: Optional[int] = None
    ) -> Optional[AccountBalance]:
        """
        Get account information including balances.

        GET /api/v3/account
        Weight: 10

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            AccountBalance object with asset balances
        """
        request = self.request("GET", "/api/v3/account", weight=10).requiresAuth(True)

        if recv_window is not None:
            request.withQueryParams(recvWindow=recv_window)

        response = request.execute()
        if response:
            return AccountBalance.from_api_response(response)
        return None

    def get_account_status(
        self, recv_window: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get account status.

        GET /sapi/v3/accountStatus
        Weight: 1

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            Dictionary with account status information
        """
        request = self.request("GET", "/sapi/v3/accountStatus", weight=1).requiresAuth(
            True
        )

        if recv_window is not None:
            request.withQueryParams(recvWindow=recv_window)

        response = request.execute()
        return response

    def get_api_trading_status(
        self, recv_window: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get API trading status.

        GET /sapi/v3/apiTradingStatus
        Weight: 1

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            Dictionary with API trading status information
        """
        request = self.request(
            "GET", "/sapi/v3/apiTradingStatus", weight=1
        ).requiresAuth(True)

        if recv_window is not None:
            request.withQueryParams(recvWindow=recv_window)

        response = request.execute()
        return response

    def get_asset_distribution_history(
        self,
        asset: Optional[str] = None,
        category: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get asset distribution history.

        GET /sapi/v1/asset/assetDistributionHistory
        Weight: 1

        Args:
            asset: Distribution asset
            category: Distribution category (e.g., Market Maker Rebate, MM Streaks Rebate, API Partner Rebate, airdrop)
            start_time: Distribution start time in milliseconds
            end_time: Distribution end time in milliseconds
            limit: Limit rows (default: 20, max: 500)

        Returns:
            Dictionary with asset distribution history information
        """
        request = self.request(
            "GET", "/sapi/v1/asset/assetDistributionHistory", weight=1
        ).requiresAuth(True)

        if asset is not None:
            request.withQueryParams(asset=asset)
        if category is not None:
            request.withQueryParams(category=category)
        if start_time is not None:
            request.withQueryParams(startTime=start_time)
        if end_time is not None:
            request.withQueryParams(endTime=end_time)
        if limit is not None:
            request.withQueryParams(
                limit=min(limit, 500)
            )  # Ensure limit doesn't exceed API max

        response = request.execute()
        return response

    def get_trade_fee(
        self, symbol: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get trading fee information.

        GET /sapi/v1/asset/query/trading-fee
        Weight: 1

        Args:
            symbol: Symbol name, if not specified, will return all

        Returns:
            List of dictionaries with trading fee information
        """
        request = self.request(
            "GET", "/sapi/v1/asset/query/trading-fee", weight=1
        ).requiresAuth(True)

        if symbol is not None:
            request.withQueryParams(symbol=symbol)

        response = request.execute()
        return response

    def get_trading_volume(self) -> Optional[Dict[str, Any]]:
        """
        Get past 30 days trading volume.

        GET /sapi/v1/asset/query/trading-volume
        Weight: 1

        Returns:
            Dictionary with trading volume information
        """
        response = (
            self.request("GET", "/sapi/v1/asset/query/trading-volume", weight=1)
            .requiresAuth(True)
            .execute()
        )
        return response
