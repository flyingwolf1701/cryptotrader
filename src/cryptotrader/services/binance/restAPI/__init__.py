"""
Binance API Module

This module provides a comprehensive client for interacting with the Binance API,
including market data, trading operations, and system information.
"""

# Import base operations
# from .services.binance.restAPI.base_operations import BinanceAPIRequest

# Import API operation classes
from cryptotrader.services.binance.restAPI.marketApi import MarketOperations
from cryptotrader.services.binance.restAPI.orderApi import OrderOperations
from cryptotrader.services.binance.restAPI.systemApi import SystemOperations
from cryptotrader.services.binance.restAPI.userApi import UserOperations
from cryptotrader.services.binance.restAPI.subaccountApi import SubAccountOperations
from cryptotrader.services.binance.restAPI.otcApi import OtcOperations
from cryptotrader.services.binance.restAPI.walletApi import WalletOperations
from cryptotrader.services.binance.restAPI.stakingApi import StakingOperations

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
    "getBidAsk",  # GET /api/v3/ticker/bookTicker
    "getHistoricalCandles",  # GET /api/v3/klines
    "getRecentTradesRest",  # GET /api/v3/trades
    "getHistoricalTradesRest",  # GET /api/v3/historicalTrades
    "getAggregateTradesRest",  # GET /api/v3/aggTrades
    "getOrderBookRest",  # GET /api/v3/depth
    "getTickerPrice",  # GET /api/v3/ticker/price
    "getAvgPriceRest",  # GET /api/v3/avgPrice
    "get24hStats",  # GET /api/v3/ticker/24hr
    "getRollingWindowStatsRest",  # GET /api/v3/ticker
    "placeSpotOrder",  # POST /api/v3/order
    "testNewOrderRest",  # POST /api/v3/order/test
    "cancelOrderRest",  # DELETE /api/v3/order
    "cancel_all_orders",  # DELETE /api/v3/openOrders
    "get_order_status",  # GET /api/v3/order
    "get_open_orders",  # GET /api/v3/openOrders
    "get_all_orders",  # GET /api/v3/allOrders
    "getOrderRateLimitsRest",  # GET /api/v3/rateLimit/order
    "get_my_trades",  # GET /api/v3/myTrades
    "cancel_replace_order",  # POST /api/v3/order/cancelReplace
    "getPreventedMatchesRest",  # GET /api/v3/myPreventedMatches
    "getAccountRest",  # GET /api/v3/account
    "getAccountRestStatus",  # GET /sapi/v3/accountStatus
    "getApiTradingStatus",  # GET /sapi/v3/apiTradingStatus
    "getAssetDistributionHistory",  # GET /sapi/v1/asset/assetDistributionHistory
    "getTradeFee",  # GET /sapi/v1/asset/query/trading-fee
    "getTradingVolume",  # GET /sapi/v1/asset/query/trading-volume
    "getSubaccountList",  # GET /sapi/v3/sub-account/list
    "getSubaccountTransferHistory",  # GET /sapi/v3/sub-account/transfer/history
    "executeSubaccountTransfer",  # POST /sapi/v3/sub-account/transfer
    "getSubaccountAssets",  # GET /sapi/v3/sub-account/assets
    "getMasterAccountTotalValue",  # GET /sapi/v1/sub-account/spotSummary
    "getSubaccountStatusList",  # GET /sapi/v1/sub-account/status
    # OCO Order Functions with endpoint paths in comments
    "placeOcoOrder",  # POST /api/v3/order/oco
    "getOcoOrderRest",  # GET /api/v3/orderList
    "getAllOcoOrders",  # GET /api/v3/allOrderList
    "getOpenOcoOrdersRest",  # GET /api/v3/openOrderList
    "cancel_oco_order",  # DELETE /api/v3/orderList
    # OTC Functions with endpoint paths in comments
    "getCoinPairs",  # GET /sapi/v1/otc/coinPairs
    "request_quote",  # POST /sapi/v1/otc/quotes
    "placeOtcOrder",  # POST /sapi/v1/otc/orders
    "get_order",  # GET /sapi/v1/otc/orders/{orderId}
    "get_orders",  # GET /sapi/v1/otc/orders
    "getOcbsOrders",  # GET /sapi/v1/ocbs/orders
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
    "getStakingAssetInfo",  # GET /sapi/v1/staking/asset
    "stake",  # POST /sapi/v1/staking/stake
    "unstake",  # POST /sapi/v1/staking/unstake
    "getStakingBalance",  # GET /sapi/v1/staking/stakingBalance
    "getStakingHistory",  # GET /sapi/v1/staking/history
    "getStakingRewardsHistory",  # GET /sapi/v1/staking/stakingRewardsHistory
]
