"""
Binance OTC API Client

This module provides a client for interacting with the Binance OTC (Over-The-Counter) API endpoints.
It includes functionality for:
- Getting supported coin pairs
- Requesting quotes for trades
- Placing OTC orders
- Querying OTC orders
- Querying OCBS orders

These endpoints provide OTC trading functionality for large traders who want to execute
trades outside of the regular exchange order book.
"""

import json
from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.baseOperations import BinanceAPIRequest
from cryptotrader.services.binance.models import (
    OtcCoinPair,
    OtcQuote,
    OtcOrderResponse,
    OtcOrderDetail,
    OtcOrdersResponse,
    OcbsOrdersResponse,
    RateLimitType,
)

logger = get_logger(__name__)


class OtcOperations:
    """
    Binance OTC operations API client implementation.

    Provides methods for over-the-counter trading operations including
    getting coin pairs, requesting quotes, and placing orders.
    """

    def __init__(self):
        """Initialize the OTC operations client."""
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

    def getCoinPairs(
        self, from_coin: Optional[str] = None, to_coin: Optional[str] = None
    ) -> List[OtcCoinPair]:
        """
        Get supported OTC coin pairs.

        GET /sapi/v1/otc/coinPairs
        Weight: 1

        Args:
            from_coin: Filter by from coin name, e.g. BTC, SHIB
            to_coin: Filter by to coin name, e.g. USDT, KSHIB

        Returns:
            List of OtcCoinPair objects
        """
        request = self.request(
            "GET", "/sapi/v1/otc/coinPairs", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if from_coin:
            request.withQueryParams(fromCoin=from_coin)
        if to_coin:
            request.withQueryParams(toCoin=to_coin)

        response = request.execute()

        coin_pairs = []
        if response:
            for pair_data in response:
                coin_pairs.append(OtcCoinPair.from_api_response(pair_data))

        return coin_pairs

    def request_quote(
        self,
        from_coin: str,
        to_coin: str,
        request_coin: str,
        request_amount: Union[str, float],
    ) -> Optional[OtcQuote]:
        """
        Request a quote for an OTC trade.

        POST /sapi/v1/otc/quotes
        Weight: 1

        Args:
            from_coin: From coin name, e.g. SHIB
            to_coin: To coin name, e.g. KSHIB
            request_coin: Request coin name, e.g. SHIB
            request_amount: Amount of request coin, e.g. 50000

        Returns:
            OtcQuote object with the quote details, or None if the request failed
        """
        response = (
            self.request("POST", "/sapi/v1/otc/quotes", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(True)
            .withQueryParams(
                fromCoin=from_coin,
                toCoin=to_coin,
                requestCoin=request_coin,
                requestAmount=str(request_amount),
            )
            .execute()
        )

        if response:
            return OtcQuote.from_api_response(response)
        return None

    def placeOtcOrder(self, quote_id: str) -> Optional[OtcOrderResponse]:
        """
        Place an OTC trade order using a quote.

        POST /sapi/v1/otc/orders
        Weight: 1

        Args:
            quote_id: Quote ID from a previous quote request

        Returns:
            OtcOrderResponse object with the order details, or None if the request failed
        """
        response = (
            self.request("POST", "/sapi/v1/otc/orders", RateLimitType.REQUEST_WEIGHT, 1)
            .requiresAuth(True)
            .withQueryParams(quoteId=quote_id)
            .execute()
        )

        if response:
            return OtcOrderResponse.from_api_response(response)
        return None

    def getOtcOrder(self, order_id: str) -> Optional[OtcOrderDetail]:
        """
        Get details of a specific OTC order.

        GET /sapi/v1/otc/orders/{orderId}
        Weight: 1

        Args:
            order_id: Order ID to lookup

        Returns:
            OtcOrderDetail object with the order details, or None if the request failed
        """
        response = (
            self.request(
                "GET",
                f"/sapi/v1/otc/orders/{order_id}",
                RateLimitType.REQUEST_WEIGHT,
                1,
            )
            .requiresAuth(True)
            .execute()
        )

        if response:
            return OtcOrderDetail.from_api_response(response)
        return None

    def getOtcOrders(
        self,
        order_id: Optional[str] = None,
        from_coin: Optional[str] = None,
        to_coin: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[OtcOrdersResponse]:
        """
        Get OTC trade orders by condition.

        GET /sapi/v1/otc/orders
        Weight: 1

        Args:
            order_id: Filter by order ID
            from_coin: Filter by from coin name, e.g. BTC, KSHIB
            to_coin: Filter by to coin name, e.g. USDT, SHIB
            start_time: Start timestamp
            end_time: End timestamp
            page: Set the number of pages, default: 1
            limit: Number of records per page, default: 10, max: 100

        Returns:
            OtcOrdersResponse object with the orders list, or None if the request failed
        """
        request = self.request(
            "GET", "/sapi/v1/otc/orders", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if order_id:
            request.withQueryParams(orderId=order_id)
        if from_coin:
            request.withQueryParams(fromCoin=from_coin)
        if to_coin:
            request.withQueryParams(toCoin=to_coin)
        if start_time:
            request.withQueryParams(startTime=start_time)
        if end_time:
            request.withQueryParams(endTime=end_time)
        if page:
            request.withQueryParams(page=page)
        if limit:
            request.withQueryParams(
                limit=min(limit, 100)
            )  # Ensure limit doesn't exceed API max

        response = request.execute()

        if response:
            return OtcOrdersResponse.from_api_response(response)
        return None

    def getOcbsOrders(
        self,
        order_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> Optional[OcbsOrdersResponse]:
        """
        Get OCBS trade orders by condition.

        GET /sapi/v1/ocbs/orders
        Weight: 1

        Args:
            order_id: Filter by order ID
            start_time: Start timestamp
            end_time: End timestamp
            page: Set the number of pages, default: 1
            limit: Number of records per page, default: 10, max: 100

        Returns:
            OcbsOrdersResponse object with the orders list, or None if the request failed
        """
        request = self.request(
            "GET", "/sapi/v1/ocbs/orders", RateLimitType.REQUEST_WEIGHT, 1
        ).requiresAuth(True)

        if order_id:
            request.withQueryParams(orderId=order_id)
        if start_time:
            request.withQueryParams(startTime=start_time)
        if end_time:
            request.withQueryParams(endTime=end_time)
        if page:
            request.withQueryParams(page=page)
        if limit:
            request.withQueryParams(
                limit=min(limit, 100)
            )  # Ensure limit doesn't exceed API max

        response = request.execute()

        if response:
            return OcbsOrdersResponse.from_api_response(response)
        return None
