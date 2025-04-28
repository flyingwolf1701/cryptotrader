"""
Binance API Module

This module provides a comprehensive client for interacting with the Binance API,
including market data, trading operations, and system information.
"""

# Import base operations
# from .services.binance.restAPI.base_operations import BinanceAPIRequest

# Import API operation classes
from services.binance.restAPI.market_api import MarketOperations
from services.binance.restAPI.order_api import OrderOperations
from services.binance.restAPI.systemApi import SystemOperations
from services.binance.restAPI.userApi import UserOperations
from services.binance.restAPI.subaccount_api import SubAccountOperations
from services.binance.restAPI.otc_api import OtcOperations
from services.binance.restAPI.walletApi import WalletOperations
from services.binance.restAPI.staking_api import StakingOperations

__all__ = [
    # Client classes
    # 'BinanceAPIRequest',
    "MarketOperations",
    "OrderOperations",
    "SystemOperations",
    "UserOperations",
    "SubAccountOperations",
    "OtcOperations",
    "WalletOperations",
    "StakingOperations",
    # API Functions with endpoint paths in comments
    "getServerTime",  # GET /api/v3/time
    "getSystemStatus",  # GET /sapi/v1/system/status
    "getExchangeInfo",  # GET /api/v3/exchangeInfo
    "get_symbol_info",  # Uses GET /api/v3/exchangeInfo
    "get_symbols",  # Uses GET /api/v3/exchangeInfo
    "get_self_trade_prevention_modes",  # Uses GET /api/v3/exchangeInfo
    "get_bid_ask",  # GET /api/v3/ticker/bookTicker
    "get_historical_candles",  # GET /api/v3/klines
    "get_recent_trades_rest",  # GET /api/v3/trades
    "get_historical_trades_rest",  # GET /api/v3/historicalTrades
    "get_aggregate_trades_rest",  # GET /api/v3/aggTrades
    "get_order_book_rest",  # GET /api/v3/depth
    "get_ticker_price",  # GET /api/v3/ticker/price
    "get_avg_price",  # GET /api/v3/avgPrice
    "get_24h_stats",  # GET /api/v3/ticker/24hr
    "get_rolling_window_stats",  # GET /api/v3/ticker
    "place_spot_order",  # POST /api/v3/order
    "test_new_order",  # POST /api/v3/order/test
    "cancel_order",  # DELETE /api/v3/order
    "cancel_all_orders",  # DELETE /api/v3/openOrders
    "get_order_status",  # GET /api/v3/order
    "get_open_orders",  # GET /api/v3/openOrders
    "get_all_orders",  # GET /api/v3/allOrders
    "get_order_rate_limits",  # GET /api/v3/rateLimit/order
    "get_my_trades",  # GET /api/v3/myTrades
    "cancel_replace_order",  # POST /api/v3/order/cancelReplace
    "get_prevented_matches",  # GET /api/v3/myPreventedMatches
    "getAccountRest",  # GET /api/v3/account
    "getAccountRestStatus",  # GET /sapi/v3/accountStatus
    "getApiTradingStatus",  # GET /sapi/v3/apiTradingStatus
    "getAssetDistributionHistory",  # GET /sapi/v1/asset/assetDistributionHistory
    "getTradeFee",  # GET /sapi/v1/asset/query/trading-fee
    "getTradingVolume",  # GET /sapi/v1/asset/query/trading-volume
    "get_subaccount_list",  # GET /sapi/v3/sub-account/list
    "get_subaccount_transfer_history",  # GET /sapi/v3/sub-account/transfer/history
    "execute_subaccount_transfer",  # POST /sapi/v3/sub-account/transfer
    "get_subaccount_assets",  # GET /sapi/v3/sub-account/assets
    "get_master_account_total_value",  # GET /sapi/v1/sub-account/spotSummary
    "get_subaccount_status_list",  # GET /sapi/v1/sub-account/status
    # OCO Order Functions with endpoint paths in comments
    "place_oco_order",  # POST /api/v3/order/oco
    "get_oco_order",  # GET /api/v3/orderList
    "get_all_oco_orders",  # GET /api/v3/allOrderList
    "get_open_oco_orders",  # GET /api/v3/openOrderList
    "cancel_oco_order",  # DELETE /api/v3/orderList
    # OTC Functions with endpoint paths in comments
    "get_coin_pairs",  # GET /sapi/v1/otc/coinPairs
    "request_quote",  # POST /sapi/v1/otc/quotes
    "place_otc_order",  # POST /sapi/v1/otc/orders
    "get_order",  # GET /sapi/v1/otc/orders/{orderId}
    "get_orders",  # GET /sapi/v1/otc/orders
    "get_ocbs_orders",  # GET /sapi/v1/ocbs/orders
    # Wallet Functions with endpoint paths in comments
    "getAssetDetails",  # GET /sapi/v1/capital/config/getall
    "withdrawFiat",  # POST /sapi/v1/fiatpayment/withdraw/apply
    "withdrawCrypto",  # POST /sapi/v1/capital/withdraw/apply
    "getCryptoWithdrawHistory",  # GET /sapi/v1/capital/withdraw/history
    "getFiatWithdrawHistory",  # GET /sapi/v1/fiatpayment/query/withdraw/history
    "getDepositAddress",  # GET /sapi/v1/capital/deposit/address
    "getCryptoDepositHistory",  # GET /sapi/v1/capital/deposit/hisrec
    "getFiatDepositHistory",  # GET /sapi/v1/fiatpayment/query/deposit/history
    "getAubaccountDepositAddress",  # GET /sapi/v1/capital/sub-account/deposit/address
    "getSubaccountDepositHistory",  # GET /sapi/v1/capital/sub-account/deposit/history
    # Staking Functions with endpoint paths in comments
    "get_staking_asset_info",  # GET /sapi/v1/staking/asset
    "stake",  # POST /sapi/v1/staking/stake
    "unstake",  # POST /sapi/v1/staking/unstake
    "get_staking_balance",  # GET /sapi/v1/staking/stakingBalance
    "get_staking_history",  # GET /sapi/v1/staking/history
    "get_staking_rewards_history",  # GET /sapi/v1/staking/stakingRewardsHistory
]
