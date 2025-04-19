"""
Binance WebSocket API Account Requests

This module provides functionality for retrieving account-related information
via the Binance WebSocket API, including account details, order history, trades,
and rate limits.
"""

# Import base operations
from cryptotrader.services.binance.websocketAPI.base_operations import (
    BinanceWebSocketConnection,
    SecurityType
)

# Import account operation functions
from cryptotrader.services.binance.websocketAPI.account_requests.get_user_acct_info import (
    get_account_info,
    process_account_info_response
)

from cryptotrader.services.binance.websocketAPI.account_requests.get_order_rate_limits import (
    get_order_rate_limits,
    process_order_rate_limits_response
)

from cryptotrader.services.binance.websocketAPI.account_requests.acct_order_history import (
    get_order_history,
    process_order_history_response
)

from cryptotrader.services.binance.websocketAPI.account_requests.acct_oco_history import (
    get_oco_history,
    process_oco_history_response
)

from cryptotrader.services.binance.websocketAPI.account_requests.acct_trade_history import (
    get_trade_history,
    process_trade_history_response
)

from cryptotrader.services.binance.websocketAPI.account_requests.acct_prevented_matches import (
    get_prevented_matches,
    process_prevented_matches_response
)

__all__ = [
    # Base operations
    'BinanceWebSocketConnection',
    'SecurityType',
    
    # Account Info
    'get_account_info',
    'process_account_info_response',
    
    # Order Rate Limits
    'get_order_rate_limits',
    'process_order_rate_limits_response',
    
    # Order History
    'get_order_history',
    'process_order_history_response',
    
    # OCO History
    'get_oco_history',
    'process_oco_history_response',
    
    # Trade History
    'get_trade_history',
    'process_trade_history_response',
    
    # Prevented Matches
    'get_prevented_matches',
    'process_prevented_matches_response'
]