"""
Binance Wallet API Client

This module provides a client for interacting with the Binance wallet-related API endpoints.
It includes functionality for:
- Retrieving asset details and wallet status
- Making withdrawals (fiat and crypto)
- Getting withdrawal history
- Getting deposit addresses
- Retrieving deposit history

These endpoints provide wallet functionality for managing funds on the Binance platform.
"""

from typing import Dict, List, Optional, Any, Union

from config import get_logger
from services.binance.restAPI.base_operations import BinanceAPIRequest
from cryptotrader.services.binance.models import (
    AssetDetail,
    FiatWithdrawResponse,
    CryptoWithdrawResponse,
    WithdrawHistoryItem,
    FiatWithdrawHistory,
    DepositAddress,
    DepositHistoryItem,
    FiatDepositHistory,
    RateLimitType,
)

logger = get_logger(__name__)


class WalletOperations:
    """
    Binance wallet operations API client implementation.

    Provides methods for managing wallet operations including deposits,
    withdrawals, and asset information.
    """

    def __init__(self):
        """Initialize the Wallet operations client."""
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

    def get_asset_details(self, recv_window: Optional[int] = None) -> List[AssetDetail]:
        """
        Get details of all assets including fees, withdrawal limits, and network status.

        GET /sapi/v1/capital/config/getall
        Weight: 1

        Args:
            recv_window: The value cannot be greater than 60000

        Returns:
            List of AssetDetail objects
        """
        request = self.request(
            "GET", "/sapi/v1/capital/config/getall", RateLimitType.REQUEST_WEIGHT, 1
        ).requires_auth(True)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        asset_details = []
        if response:
            for assetData in response:
                asset_details.append(AssetDetail.from_api_response(assetData))

        return asset_details

    def withdraw_fiat(
        self,
        payment_method: str,
        payment_account: str,
        amount: Union[str, float],
        fiat_currency: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[FiatWithdrawResponse]:
        """
        Submit a USD withdraw request via BITGO.

        POST /sapi/v1/fiatpayment/withdraw/apply
        Weight: 1

        Args:
            payment_method: Default value="BITGO"
            payment_account: The account to which the user wants to withdraw funds
            amount: The amount to withdraw
            fiat_currency: Default value="USD"
            recv_window: The value cannot be greater than 60000

        Returns:
            FiatWithdrawResponse object with withdrawal details, or None if the request failed
        """
        request = (
            self.request(
                "POST",
                "/sapi/v1/fiatpayment/withdraw/apply",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requires_auth(True)
            .with_query_params(
                paymentMethod=payment_method,
                paymentAccount=payment_account,
                amount=str(amount),  # Ensure amount is a string
            )
        )

        if fiat_currency:
            request.with_query_params(fiatCurrency=fiat_currency)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        if response:
            return FiatWithdrawResponse.from_api_response(response)
        return None

    def withdraw_crypto(
        self,
        coin: str,
        network: str,
        address: str,
        amount: Union[str, float],
        withdraw_order_id: Optional[str] = None,
        address_tag: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[CryptoWithdrawResponse]:
        """
        Submit a crypto withdrawal request.

        POST /sapi/v1/capital/withdraw/apply
        Weight: 1

        Args:
            coin: The coin to withdraw
            network: Specify the withdrawal network (e.g. 'ERC20' or 'BEP20')
            address: The recipient address
            amount: The amount to withdraw
            withdraw_order_id: Client ID for the withdrawal
            address_tag: Memo for coins like XRP, XMR etc.
            recv_window: The value cannot be greater than 60000

        Returns:
            CryptoWithdrawResponse object with the withdrawal ID, or None if the request failed
        """
        request = (
            self.request(
                "POST",
                "/sapi/v1/capital/withdraw/apply",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requires_auth(True)
            .with_query_params(
                coin=coin,
                network=network,
                address=address,
                amount=str(amount),  # Ensure amount is a string
            )
        )

        if withdraw_order_id:
            request.with_query_params(withdrawOrderId=withdraw_order_id)

        if address_tag:
            request.with_query_params(addressTag=address_tag)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        if response:
            return CryptoWithdrawResponse.from_api_response(response)
        return None

    def get_crypto_withdraw_history(
        self,
        coin: Optional[str] = None,
        withdraw_order_id: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[WithdrawHistoryItem]:
        """
        Get crypto withdrawal history.

        GET /sapi/v1/capital/withdraw/history
        Weight: 1

        Args:
            coin: Filter by coin
            withdraw_order_id: Client ID for the withdrawal
            status: Filter by status (0: email sent, 1: canceled, 2: awaiting approval,
                   3: rejected, 4: processing, 5: failure, 6: completed)
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            offset: Default: 0
            limit: Default: 1000, max: 1000
            recv_window: The value cannot be greater than 60000

        Returns:
            List of WithdrawHistoryItem objects
        """
        request = self.request(
            "GET", "/sapi/v1/capital/withdraw/history", RateLimitType.REQUEST_WEIGHT, 1
        ).requires_auth(True)

        if coin:
            request.with_query_params(coin=coin)

        if withdraw_order_id:
            request.with_query_params(withdrawOrderId=withdraw_order_id)

        if status is not None:
            request.with_query_params(status=status)

        if start_time:
            request.with_query_params(startTime=start_time)

        if end_time:
            request.with_query_params(endTime=end_time)

        if offset is not None:
            request.with_query_params(offset=offset)

        if limit:
            request.with_query_params(
                limit=min(limit, 1000)
            )  # Ensure limit doesn't exceed API max

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        history_items = []
        if response:
            for item_data in response:
                history_items.append(WithdrawHistoryItem.from_api_response(item_data))

        return history_items

    def get_fiat_withdraw_history(
        self,
        fiat_currency: Optional[str] = None,
        order_id: Optional[str] = None,
        offset: Optional[int] = None,
        payment_channel: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[FiatWithdrawHistory]:
        """
        Get fiat (USD) withdrawal history.

        GET /sapi/v1/fiatpayment/query/withdraw/history
        Weight: 1

        Args:
            fiat_currency: Filter by currency
            order_id: Filter by order ID
            offset: Pagination offset
            payment_channel: Filter by payment channel
            payment_method: Filter by payment method
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            recv_window: The value cannot be greater than 60000

        Returns:
            FiatWithdrawHistory object with withdrawal records, or None if the request failed
        """
        request = self.request(
            "GET",
            "/sapi/v1/fiatpayment/query/withdraw/history",
            RateLimitType.REQUEST_WEIGHT,
            1,
        ).requires_auth(True)

        if fiat_currency:
            request.with_query_params(fiatCurrency=fiat_currency)

        if order_id:
            request.with_query_params(orderId=order_id)

        if offset is not None:
            request.with_query_params(offset=offset)

        if payment_channel:
            request.with_query_params(paymentChannel=payment_channel)

        if payment_method:
            request.with_query_params(paymentMethod=payment_method)

        if start_time:
            request.with_query_params(startTime=start_time)

        if end_time:
            request.with_query_params(endTime=end_time)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        if response:
            return FiatWithdrawHistory.from_api_response(response)
        return None

    def get_deposit_address(
        self,
        coin: str,
        network: Optional[str] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[DepositAddress]:
        """
        Get deposit address for a particular crypto asset.

        GET /sapi/v1/capital/deposit/address
        Weight: 1

        Args:
            coin: The coin to get address for
            network: The network to use
            recv_window: The value cannot be greater than 60000

        Returns:
            DepositAddress object with the address details, or None if the request failed
        """
        request = (
            self.request(
                "GET",
                "/sapi/v1/capital/deposit/address",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requires_auth(True)
            .with_query_params(coin=coin)
        )

        if network:
            request.with_query_params(network=network)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        if response:
            return DepositAddress.from_api_response(response)
        return None

    def get_crypto_deposit_history(
        self,
        coin: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> List[DepositHistoryItem]:
        """
        Get crypto deposit history.

        GET /sapi/v1/capital/deposit/hisrec
        Weight: 1

        Args:
            coin: Filter by coin
            status: Filter by status (0: pending, 6: credited but cannot withdraw, 1: success)
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            offset: Default: 0
            limit: Default: 1000, max: 1000
            recv_window: The value cannot be greater than 60000

        Returns:
            List of DepositHistoryItem objects
        """
        request = self.request(
            "GET", "/sapi/v1/capital/deposit/hisrec", RateLimitType.REQUEST_WEIGHT, 1
        ).requires_auth(True)

        if coin:
            request.with_query_params(coin=coin)

        if status is not None:
            request.with_query_params(status=status)

        if start_time:
            request.with_query_params(startTime=start_time)

        if end_time:
            request.with_query_params(endTime=end_time)

        if offset is not None:
            request.with_query_params(offset=offset)

        if limit:
            request.with_query_params(
                limit=min(limit, 1000)
            )  # Ensure limit doesn't exceed API max

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        history_items = []
        if response:
            for item_data in response:
                history_items.append(DepositHistoryItem.from_api_response(item_data))

        return history_items

    def get_fiat_deposit_history(
        self,
        fiat_currency: Optional[str] = None,
        order_id: Optional[str] = None,
        offset: Optional[int] = None,
        payment_channel: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        recv_window: Optional[int] = None,
    ) -> Optional[FiatDepositHistory]:
        """
        Get fiat (USD) deposit history.

        GET /sapi/v1/fiatpayment/query/deposit/history
        Weight: 1

        Args:
            fiat_currency: Filter by currency
            order_id: Filter by order ID
            offset: Pagination offset
            payment_channel: Filter by payment channel
            payment_method: Filter by payment method
            start_time: Start timestamp (default: 90 days from current timestamp)
            end_time: End timestamp (default: present timestamp)
            recv_window: The value cannot be greater than 60000

        Returns:
            FiatDepositHistory object with deposit records, or None if the request failed
        """
        request = self.request(
            "GET",
            "/sapi/v1/fiatpayment/query/deposit/history",
            RateLimitType.REQUEST_WEIGHT,
            1,
        ).requires_auth(True)

        if fiat_currency:
            request.with_query_params(fiatCurrency=fiat_currency)

        if order_id:
            request.with_query_params(orderId=order_id)

        if offset is not None:
            request.with_query_params(offset=offset)

        if payment_channel:
            request.with_query_params(paymentChannel=payment_channel)

        if payment_method:
            request.with_query_params(paymentMethod=payment_method)

        if start_time:
            request.with_query_params(startTime=start_time)

        if end_time:
            request.with_query_params(endTime=end_time)

        if recv_window is not None:
            request.with_query_params(recvWindow=recv_window)

        response = request.execute()

        if response:
            return FiatDepositHistory.from_api_response(response)
        return None

    def get_subaccount_deposit_address(
        self, email: str, coin: str, network: Optional[str] = None
    ) -> Optional[DepositAddress]:
        """
        Get deposit address for a sub-account.

        GET /sapi/v1/capital/sub-account/deposit/address
        Weight: 1

        Args:
            email: Sub-account email
            coin: The coin to get address for
            network: The network to use (if empty, returns the default network)

        Returns:
            DepositAddress object with the address details, or None if the request failed
        """
        request = (
            self.request(
                "GET",
                "/sapi/v1/capital/sub-account/deposit/address",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requires_auth(True)
            .with_query_params(email=email, coin=coin)
        )

        if network:
            request.with_query_params(network=network)

        response = request.execute()

        if response:
            return DepositAddress.from_api_response(response)
        return None

    def get_subaccount_deposit_history(
        self,
        email: str,
        coin: Optional[str] = None,
        status: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[DepositHistoryItem]:
        """
        Get deposit history for a sub-account.

        GET /sapi/v1/capital/sub-account/deposit/history
        Weight: 1

        Args:
            email: Sub-account email
            coin: Filter by coin
            status: Filter by status (0: pending, 6: credited but cannot withdraw, 1: success)
            start_time: Start timestamp
            end_time: End timestamp
            limit: Number of records to return
            offset: Pagination offset

        Returns:
            List of DepositHistoryItem objects
        """
        request = (
            self.request(
                "GET",
                "/sapi/v1/capital/sub-account/deposit/history",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requires_auth(True)
            .with_query_params(email=email)
        )

        if coin:
            request.with_query_params(coin=coin)

        if status is not None:
            request.with_query_params(status=status)

        if start_time:
            request.with_query_params(startTime=start_time)

        if end_time:
            request.with_query_params(endTime=end_time)

        if limit:
            request.with_query_params(limit=limit)

        if offset is not None:
            request.with_query_params(offset=offset)

        response = request.execute()

        history_items = []
        if response:
            for item_data in response:
                history_items.append(DepositHistoryItem.from_api_response(item_data))

        return history_items
