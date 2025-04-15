"""
Binance API Module

This module provides a comprehensive client for interacting with the Binance API,
including market data, trading operations, and system information.
"""

# Import all models from the models package
from .models import (
    # Base models
    OrderType, OrderSide, TimeInForce, KlineInterval,
    OrderStatus, SelfTradePreventionMode, SymbolStatus,
    RateLimitType, RateLimitInterval, SystemStatus,
    RateLimit, PriceData, OrderRequest, Candle,
    AccountAsset, AccountBalance, OrderStatusResponse,
    SymbolInfo, Trade, AggTrade, OrderBookEntry, OrderBook,
    TickerPrice, AvgPrice, PriceStatsMini, PriceStats, 
    RollingWindowStatsMini, RollingWindowStats, BinanceEndpoints,
    
    # Order models
    CancelReplaceMode, NewOrderResponseType, CancelRestriction,
    Fill, OrderResponseFull, OrderResponseResult, OrderResponseAck,
    CancelReplaceResponse, OrderTrade, PreventedMatch, RateLimitInfo
)

# Import client classes
from .general_api import RestClient as Client
from .base_operations import BinanceAPIRequest
from .order_api import OrderOperations

__all__ = [
    # Client classes
    'Client',
    'BinanceAPIRequest',
    'OrderOperations',
    
    # Base models
    'OrderType',
    'OrderSide',
    'TimeInForce',
    'KlineInterval',
    'SymbolStatus',
    'SystemStatus',
    'SelfTradePreventionMode',
    'RateLimitType',
    'RateLimitInterval',
    'RateLimit',
    'PriceData',
    'OrderRequest',
    'Candle',
    'AccountAsset',
    'AccountBalance',
    'OrderStatusResponse',
    'SymbolInfo',
    'Trade',
    'AggTrade',
    'OrderBook',
    'OrderBookEntry',
    'TickerPrice',
    'AvgPrice',
    'PriceStatsMini',
    'PriceStats',
    'RollingWindowStatsMini',
    'RollingWindowStats',
    'BinanceEndpoints',
    
    # Order models
    'CancelReplaceMode',
    'NewOrderResponseType',
    'CancelRestriction',
    'Fill',
    'OrderResponseFull',
    'OrderResponseResult',
    'OrderResponseAck',
    'CancelReplaceResponse',
    'OrderTrade',
    'PreventedMatch',
    'RateLimitInfo'
]