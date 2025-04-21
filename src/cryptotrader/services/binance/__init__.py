"""
Binance API Module

This package provides comprehensive implementations for interacting with 
the Binance cryptocurrency exchange API, including both REST and WebSocket interfaces.

Key components:
- REST API functions for market data, trading, account management, and more
- WebSocket API functions for real-time data and trading operations
- WebSocket streams for continuous market data and account updates
- Strongly-typed data models for all API operations
- Comprehensive error handling and rate limiting
"""

# Import REST API client classes
from cryptotrader.services.binance.restAPI.base_operations import BinanceAPIRequest
from cryptotrader.services.binance.restAPI.market_api import MarketOperations
from cryptotrader.services.binance.restAPI.order_api import OrderOperations
from cryptotrader.services.binance.restAPI.system_api import SystemOperations
from cryptotrader.services.binance.restAPI.user_api import UserOperations
from cryptotrader.services.binance.restAPI.subaccount_api import SubAccountOperations
from cryptotrader.services.binance.restAPI.otc_api import OtcOperations
from cryptotrader.services.binance.restAPI.wallet_api import WalletOperations
from cryptotrader.services.binance.restAPI.staking_api import StakingOperations

# Import REST API components
from cryptotrader.services.binance.restAPI import (
    # System API
    get_server_time,
    get_system_status,
    get_exchange_info,
    get_symbol_info,
    get_symbols,
    get_self_trade_prevention_modes,
    
    # Market API
    get_bid_ask,
    get_historical_candles,
    get_recent_trades,
    get_historical_trades,
    get_aggregate_trades,
    get_order_book,
    get_ticker_price,
    get_avg_price,
    get_24h_stats,
    get_rolling_window_stats,
    
    # Order API
    place_order,
    test_new_order,
    cancel_order,
    cancel_all_orders,
    get_order_status,
    get_open_orders,
    get_all_orders,
    get_order_rate_limits,
    get_my_trades,
    cancel_replace_order,
    get_prevented_matches,
    place_oco_order,
    get_oco_order,
    get_all_oco_orders,
    get_open_oco_orders,
    cancel_oco_order,
    
    # User API
    get_account,
    get_account_status,
    get_api_trading_status,
    get_asset_distribution_history,
    get_trade_fee,
    get_trading_volume,
    
    # Subaccount API
    get_subaccount_list,
    get_subaccount_transfer_history,
    execute_subaccount_transfer,
    get_subaccount_assets,
    get_master_account_total_value,
    get_subaccount_status_list,
    
    # Wallet API
    get_asset_details,
    withdraw_fiat,
    withdraw_crypto,
    get_crypto_withdraw_history,
    get_fiat_withdraw_history,
    get_deposit_address,
    get_crypto_deposit_history,
    get_fiat_deposit_history,
    get_subaccount_deposit_address,
    get_subaccount_deposit_history,
    
    # Staking API
    get_staking_asset_info,
    stake,
    unstake,
    get_staking_balance,
    get_staking_history,
    get_staking_rewards_history,
    
    # OTC API
    get_coin_pairs,
    request_quote,
    get_order,
    get_orders,
    get_ocbs_orders
)

# Import WebSocket API components
from cryptotrader.services.binance.websocketAPI import (
    # Base operations
    BinanceWebSocketConnection,
    
    # Account requests
    get_account_info,
    get_order_rate_limits as ws_get_order_rate_limits,
    get_order_history,
    get_oco_history,
    get_trade_history,
    get_prevented_matches as ws_get_prevented_matches,
    
    # Market data requests
    get_order_book as ws_get_order_book,
    get_recent_trades as ws_get_recent_trades,
    get_historical_trades as ws_get_historical_trades,
    get_klines,
    get_aggregate_trades,
    get_price_ticker,
    get_book_ticker,
    get_24h_ticker,
    get_rolling_window_stats as ws_get_rolling_window_stats,
    get_avg_price as ws_get_avg_price,
    
    # Trading requests
    place_new_order,
    test_new_order as ws_test_new_order,
    cancel_order as ws_cancel_order,
    cancel_open_orders as ws_cancel_open_orders,
    query_order,
    get_current_open_orders,
    replace_order,
    create_new_oco_order,
    get_oco_order as ws_get_oco_order,
    get_open_oco_orders,
    cancel_oco_order as ws_cancel_oco_order,
    
    # User data stream requests
    start_user_data_stream,
    ping_user_data_stream,
    stop_user_data_stream,
    
    # Stream management
    BinanceStreamManager,
    create_market_stream,
    UserDataStream
)

# Import key model classes for direct access
from cryptotrader.services.binance.models import (
    # Base models
    OrderType, OrderSide, TimeInForce, KlineInterval,
    OrderStatus, SymbolStatus, SystemStatus,
    RateLimitType, RateLimitInterval, RateLimit,
    AccountAsset, AccountBalance, OrderStatusResponse,
    SymbolInfo, Trade, AggTrade, OrderBook,
    
    # Order models
    CancelReplaceMode, NewOrderResponseType, CancelRestriction,
    Fill, OrderResponseFull, OrderResponseResult, OrderResponseAck,
    CancelReplaceResponse, OrderTrade, PreventedMatch, RateLimitInfo,
    OcoOrderResponse,
    
    # OTC models
    OtcOrderStatus, OtcCoinPair, OtcQuote, OtcOrderResponse,
    OtcOrderDetail, OtcOrdersResponse, OcbsOrderDetail,
    
    # Wallet models
    WithdrawStatus, DepositStatus, NetworkInfo, AssetDetail,
    FiatWithdrawResponse, CryptoWithdrawResponse, WithdrawHistoryItem,
    DepositAddress, DepositHistoryItem, FiatDepositHistory,
    
    # Staking models
    StakingTransactionType, StakingTransactionStatus, StakingAssetInfo,
    StakingOperationResult, StakingStakeResult, StakingUnstakeResult,
    StakingBalanceItem, StakingBalanceResponse, StakingHistoryItem,
    StakingRewardItem, StakingRewardsResponse
)

__all__ = [
    # REST API client classes
    'BinanceAPIRequest',
    'MarketOperations',
    'OrderOperations',
    'SystemOperations',
    'UserOperations',
    'SubAccountOperations',
    'OtcOperations',
    'WalletOperations',
    'StakingOperations',
    
    # System API
    'get_server_time',
    'get_system_status',
    'get_exchange_info',
    'get_symbol_info',
    'get_symbols',
    'get_self_trade_prevention_modes',
    
    # Market API
    'get_bid_ask',
    'get_historical_candles',
    'get_recent_trades',
    'get_historical_trades',
    'get_aggregate_trades',
    'get_order_book',
    'get_ticker_price',
    'get_avg_price',
    'get_24h_stats',
    'get_rolling_window_stats',
    
    # Order API
    'place_order',
    'test_new_order',
    'cancel_order',
    'cancel_all_orders',
    'get_order_status',
    'get_open_orders',
    'get_all_orders',
    'get_order_rate_limits',
    'get_my_trades',
    'cancel_replace_order',
    'get_prevented_matches',
    'place_oco_order',
    'get_oco_order',
    'get_all_oco_orders',
    'get_open_oco_orders',
    'cancel_oco_order',
    
    # User API
    'get_account',
    'get_account_status',
    'get_api_trading_status',
    'get_asset_distribution_history',
    'get_trade_fee',
    'get_trading_volume',
    
    # Subaccount API
    'get_subaccount_list',
    'get_subaccount_transfer_history',
    'execute_subaccount_transfer',
    'get_subaccount_assets',
    'get_master_account_total_value',
    'get_subaccount_status_list',
    
    # Wallet API
    'get_asset_details',
    'withdraw_fiat',
    'withdraw_crypto',
    'get_crypto_withdraw_history',
    'get_fiat_withdraw_history',
    'get_deposit_address',
    'get_crypto_deposit_history',
    'get_fiat_deposit_history',
    'get_subaccount_deposit_address',
    'get_subaccount_deposit_history',
    
    # Staking API
    'get_staking_asset_info',
    'stake',
    'unstake',
    'get_staking_balance',
    'get_staking_history',
    'get_staking_rewards_history',
    
    # OTC API
    'get_coin_pairs',
    'request_quote',
    'get_order',
    'get_orders',
    'get_ocbs_orders',
    
    # WebSocket API - Base
    'BinanceWebSocketConnection',
    
    # WebSocket API - Account
    'get_account_info',
    'ws_get_order_rate_limits',
    'get_order_history',
    'get_oco_history',
    'get_trade_history',
    'ws_get_prevented_matches',
    
    # WebSocket API - Market
    'ws_get_order_book',
    'ws_get_recent_trades',
    'ws_get_historical_trades',
    'get_klines',
    'get_aggregate_trades',
    'get_price_ticker',
    'get_book_ticker',
    'get_24h_ticker',
    'ws_get_rolling_window_stats',
    'ws_get_avg_price',
    
    # WebSocket API - Trading
    'place_new_order',
    'ws_test_new_order',
    'ws_cancel_order',
    'ws_cancel_open_orders',
    'query_order',
    'get_current_open_orders',
    'replace_order',
    'create_new_oco_order',
    'ws_get_oco_order',
    'get_open_oco_orders',
    'ws_cancel_oco_order',
    
    # WebSocket API - User Data Stream
    'start_user_data_stream',
    'ping_user_data_stream',
    'stop_user_data_stream',
    
    # WebSocket API - Stream Management
    'BinanceStreamManager',
    'create_market_stream',
    'UserDataStream',
    
    # Base Models
    'OrderType', 'OrderSide', 'TimeInForce', 'KlineInterval',
    'OrderStatus', 'SymbolStatus', 'SystemStatus',
    'RateLimitType', 'RateLimitInterval', 'RateLimit',
    'AccountAsset', 'AccountBalance', 'OrderStatusResponse',
    'SymbolInfo', 'Trade', 'AggTrade', 'OrderBook',
    
    # Order Models
    'CancelReplaceMode', 'NewOrderResponseType', 'CancelRestriction',
    'Fill', 'OrderResponseFull', 'OrderResponseResult', 'OrderResponseAck',
    'CancelReplaceResponse', 'OrderTrade', 'PreventedMatch', 'RateLimitInfo',
    'OcoOrderResponse',
    
    # OTC Models
    'OtcOrderStatus', 'OtcCoinPair', 'OtcQuote', 'OtcOrderResponse',
    'OtcOrderDetail', 'OtcOrdersResponse', 'OcbsOrderDetail',
    
    # Wallet Models
    'WithdrawStatus', 'DepositStatus', 'NetworkInfo', 'AssetDetail',
    'FiatWithdrawResponse', 'CryptoWithdrawResponse', 'WithdrawHistoryItem',
    'DepositAddress', 'DepositHistoryItem', 'FiatDepositHistory',
    
    # Staking Models
    'StakingTransactionType', 'StakingTransactionStatus', 'StakingAssetInfo',
    'StakingOperationResult', 'StakingStakeResult', 'StakingUnstakeResult',
    'StakingBalanceItem', 'StakingBalanceResponse', 'StakingHistoryItem',
    'StakingRewardItem', 'StakingRewardsResponse'
]