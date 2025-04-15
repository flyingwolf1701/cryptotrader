"""
Binance API Module

This module provides a comprehensive client for interacting with the Binance API,
including market data, trading operations, and system information.
"""

# Import base operations
from cryptotrader.services.binance.restAPI.base_operations import BinanceAPIRequest

# Import API operation classes
from cryptotrader.services.binance.restAPI.general_api import GeneralOperations
from cryptotrader.services.binance.restAPI.market_api import MarketOperations
from cryptotrader.services.binance.restAPI.order_api import OrderOperations
from cryptotrader.services.binance.restAPI.system_api import SystemOperations
from cryptotrader.services.binance.restAPI.user_api import UserOperations
from cryptotrader.services.binance.restAPI.subaccount_api import SubAccountOperations

__all__ = [
    # Client classes
    'BinanceAPIRequest',
    'MarketOperations',
    'OrderOperations',
    'GeneralOperations',
    'SystemOperations',
    'UserOperations',
    'SubAccountOperations',
    
    # API Functions with endpoint paths in comments
    'get_balance',           # GET /api/v3/account
    'get_server_time',       # GET /api/v3/time
    'get_system_status',     # GET /sapi/v1/system/status
    'get_exchange_info',     # GET /api/v3/exchangeInfo
    'get_symbol_info',       # Uses GET /api/v3/exchangeInfo
    'get_bid_ask',           # GET /api/v3/ticker/bookTicker
    'get_historical_candles', # GET /api/v3/klines
    'get_recent_trades',     # GET /api/v3/trades
    'get_historical_trades', # GET /api/v3/historicalTrades
    'get_aggregate_trades',  # GET /api/v3/aggTrades
    'get_order_book',        # GET /api/v3/depth
    'get_ticker_price',      # GET /api/v3/ticker/price
    'get_avg_price',         # GET /api/v3/avgPrice
    'get_24h_stats',         # GET /api/v3/ticker/24hr
    'get_rolling_window_stats', # GET /api/v3/ticker
    'place_order',           # POST /api/v3/order
    'test_new_order',        # POST /api/v3/order/test
    'cancel_order',          # DELETE /api/v3/order
    'cancel_all_orders',     # DELETE /api/v3/openOrders
    'get_order_status',      # GET /api/v3/order
    'get_open_orders',       # GET /api/v3/openOrders
    'get_all_orders',        # GET /api/v3/allOrders
    'get_order_rate_limits', # GET /api/v3/rateLimit/order
    'get_my_trades',         # GET /api/v3/myTrades
    'cancel_replace_order',  # POST /api/v3/order/cancelReplace
    'get_prevented_matches', # GET /api/v3/myPreventedMatches
    'get_account',           # GET /api/v3/account
    'get_account_status',    # GET /sapi/v3/accountStatus
    'get_api_trading_status', # GET /sapi/v3/apiTradingStatus
]