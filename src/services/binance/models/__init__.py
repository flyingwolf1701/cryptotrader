"""
Binance API Models

This package contains all the data models used throughout the Binance API implementation.
"""

# Import from base_models
from .base_models import (
    OrderType, OrderSide, TimeInForce, KlineInterval,
    OrderStatus, SelfTradePreventionMode, SymbolStatus,
    RateLimitType, RateLimitInterval, SystemStatus,
    RateLimit, PriceData, OrderRequest, Candle,
    AccountAsset, AccountBalance, OrderStatusResponse,
    SymbolInfo, Trade, AggTrade, OrderBookEntry, OrderBook,
    TickerPrice, AvgPrice, PriceStatsMini, PriceStats, 
    RollingWindowStatsMini, RollingWindowStats, BinanceEndpoints
)

# Import from order_models
from .order_models import (
    CancelReplaceMode, NewOrderResponseType, CancelRestriction,
    Fill, OrderResponseFull, OrderResponseResult, OrderResponseAck,
    CancelReplaceResponse, OrderTrade, PreventedMatch, RateLimitInfo,
    OcoOrderResponse
)

# Import from otc_models
from .otc_models import (
    OtcOrderStatus, OtcCoinPair, OtcQuote, OtcOrderResponse,
    OtcOrderDetail, OtcOrdersResponse, OcbsOrderDetail, OcbsOrdersResponse
)

# Import from wallet_models
from .wallet_models import (
    WithdrawStatus, DepositStatus, NetworkInfo, AssetDetail,
    FiatWithdrawResponse, CryptoWithdrawResponse, WithdrawHistoryItem,
    FiatWithdrawHistory, DepositAddress, DepositHistoryItem,
    FiatDepositHistory, FiatDepositHistoryItem, FiatWithdrawHistoryItem
)

# Import from staking_models
from .staking_models import (
    StakingTransactionType, StakingTransactionStatus, StakingAssetInfo,
    StakingOperationResult, StakingStakeResult, StakingUnstakeResult,
    StakingBalanceItem, StakingBalanceResponse, StakingHistoryItem,
    StakingRewardItem, StakingRewardsResponse
)

__all__ = [
    # Base Models
    'OrderType', 'OrderSide', 'TimeInForce', 'KlineInterval',
    'OrderStatus', 'SelfTradePreventionMode', 'SymbolStatus',
    'RateLimitType', 'RateLimitInterval', 'SystemStatus',
    'RateLimit', 'PriceData', 'OrderRequest', 'Candle',
    'AccountAsset', 'AccountBalance', 'OrderStatusResponse',
    'SymbolInfo', 'Trade', 'AggTrade', 'OrderBookEntry', 'OrderBook',
    'TickerPrice', 'AvgPrice', 'PriceStatsMini', 'PriceStats', 
    'RollingWindowStatsMini', 'RollingWindowStats', 'BinanceEndpoints',
    
    # Order Models
    'CancelReplaceMode', 'NewOrderResponseType', 'CancelRestriction',
    'Fill', 'OrderResponseFull', 'OrderResponseResult', 'OrderResponseAck',
    'CancelReplaceResponse', 'OrderTrade', 'PreventedMatch', 'RateLimitInfo',
    'OcoOrderResponse',
    
    # OTC Models
    'OtcOrderStatus', 'OtcCoinPair', 'OtcQuote', 'OtcOrderResponse',
    'OtcOrderDetail', 'OtcOrdersResponse', 'OcbsOrderDetail', 'OcbsOrdersResponse',
    
    # Wallet Models
    'WithdrawStatus', 'DepositStatus', 'NetworkInfo', 'AssetDetail',
    'FiatWithdrawResponse', 'CryptoWithdrawResponse', 'WithdrawHistoryItem',
    'FiatWithdrawHistory', 'DepositAddress', 'DepositHistoryItem',
    'FiatDepositHistory', 'FiatDepositHistoryItem', 'FiatWithdrawHistoryItem',
    
    # Staking Models
    'StakingTransactionType', 'StakingTransactionStatus', 'StakingAssetInfo',
    'StakingOperationResult', 'StakingStakeResult', 'StakingUnstakeResult',
    'StakingBalanceItem', 'StakingBalanceResponse', 'StakingHistoryItem',
    'StakingRewardItem', 'StakingRewardsResponse'
]