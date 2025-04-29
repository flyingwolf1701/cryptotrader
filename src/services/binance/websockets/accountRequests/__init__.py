"""
Binance WebSocket API Account Requests

This module provides functionality for retrieving account-related information
via the Binance WebSocket API, including account details, order history, trades,
and rate limits.
"""

# Import base operations
from services.binance.websockets.baseOperations import (
    BinanceWebSocketConnection,
    SecurityType,
)

# Import account operation functions
from services.binance.websockets.accountRequests.getUserAcctInfo import (
    getAccountWS,
    processAccountInfoResponse,
)

from services.binance.websockets.accountRequests.getOrderRateLimits import (
    getOrderRateLimitsWS,
    processOrderRateLimitsResponse,
)

from services.binance.websockets.accountRequests.acctOrderHistory import (
    getOrderHistoryWS,
    process_order_history_response,
)

from services.binance.websockets.trading_requests.acct_oco_history import (
    get_oco_history,
    process_oco_history_response,
)

from services.binance.websockets.accountRequests.acctTradeHistory import (
    getTradeHistoryWS,
    processTradeHistoryResponse,
)

from services.binance.websockets.accountRequests.acctPreventedMatches import (
    getPreventedMatchesWS,
    processPreventedMatchesResponse,
)

__all__ = [
    # Base operations
    "BinanceWebSocketConnection",
    "SecurityType",
    # Account Info
    "getAccountWS",
    "processAccountInfoResponse",
    # Order Rate Limits
    "getOrderRateLimitsWS",
    "processOrderRateLimitsResponse",
    # Order History
    "getOrderHistoryWS",
    "process_order_history_response",
    # OCO History
    "get_oco_history",
    "process_oco_history_response",
    # Trade History
    "getTradeHistoryWS",
    "processTradeHistoryResponse",
    # Prevented Matches
    "getPreventedMatchesWS",
    "processPreventedMatchesResponse",
]
