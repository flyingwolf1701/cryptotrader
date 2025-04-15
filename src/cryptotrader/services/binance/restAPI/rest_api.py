"""
Binance REST API Client

This module provides a client for interacting with the Binance REST API.
It builds on the base operations infrastructure to provide a comprehensive set
of methods for accessing Binance API endpoints.

Key features:
- Market data retrieval (prices, trades, order books, etc.)
- Account information and balance retrieval
- Order placement and management
- Exchange information

Each method is designed to map directly to a specific Binance API endpoint,
with appropriate parameter handling and response transformation.
"""

import json
import time
from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.base_operations import BinanceAPIRequest
from cryptotrader.services.binance.models.base_models import (
    PriceData, Candle,
    AccountBalance, SymbolInfo, RateLimitType,
    SystemStatus, Trade, AggTrade, 
    OrderBook, TickerPrice, AvgPrice, 
    PriceStatsMini, PriceStats, RollingWindowStatsMini, 
    RollingWindowStats
)

logger = get_logger(__name__)

class RestClient:
    """
    Binance REST API client implementation.
    
    Provides methods for interacting with various Binance API endpoints,
    with automatic response parsing and error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize the REST client.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
    
    def request(self, method: str, endpoint: str, 
               limit_type: Optional[RateLimitType] = None,
               weight: int = 1) -> BinanceAPIRequest:
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
            method=method, 
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight
        )
    
    #
    # Account endpoints - Require authentication
    #
    
    def get_balance(self) -> Optional[AccountBalance]:
        """
        Get account information including balances.
        
        Weight: 10
        
        Returns:
            AccountBalance object with asset balances
        """
        response = self.request("GET", "/api/v3/account", weight=10).requires_auth(True).execute()
        if response:
            return AccountBalance.from_api_response(response)
        return None
    
    #
    # System endpoints - No authentication needed
    #
    
    def get_server_time(self) -> int:
        """
        Get current server time from Binance API.
        
        Weight: 1
        
        Returns:
            Server time in milliseconds
        """
        response = self.request("GET", "/api/v3/time").requires_auth(False).execute()
        if response:
            return response["serverTime"]
        return int(time.time() * 1000)  # Fallback to local time
    
    def get_system_status(self) -> SystemStatus:
        """
        Get system status.
        
        Weight: 1
        
        Returns:
            SystemStatus object (0: normal, 1: maintenance)
        """
        response = self.request("GET", "/sapi/v1/system/status").requires_auth(False).execute()
        if response:
            return SystemStatus(status_code=response.get("status", -1))
        return SystemStatus(status_code=-1)  # Unknown status
    
    #
    # Market data endpoints - No authentication needed
    #
    
    def get_exchange_info(self, symbol: Optional[str] = None,
                        symbols: Optional[List[str]] = None,
                        permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange information.
        
        Weight: 1 for a single symbol, 10 for all symbols
        
        Args:
            symbol: Single symbol to get info for
            symbols: Multiple symbols to get info for
            permissions: Permissions to filter by (e.g. ["SPOT"])
            
        Returns:
            Dictionary containing exchange information
        """
        request = self.request("GET", "/api/v3/exchangeInfo").requires_auth(False)
        
        if symbol:
            request.with_query_params(symbol=symbol)
        elif symbols:
            symbols_str = json.dumps(symbols)
            request.with_query_params(symbols=symbols_str)
        elif permissions:
            permissions_str = json.dumps(permissions)
            request.with_query_params(permissions=permissions_str)
        
        response = request.execute()
        return response if response else {}
    
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """
        Get information for a specific symbol.
        
        Weight: 1
        
        Args:
            symbol: The symbol to get information for (e.g. "BTCUSDT")
            
        Returns:
            SymbolInfo object with symbol details, or None if not found
        """
        exchange_info = self.get_exchange_info(symbol=symbol)
        if 'symbols' in exchange_info and exchange_info['symbols']:
            symbol_data = exchange_info['symbols'][0]
            return SymbolInfo.from_api_response(symbol_data)
        return None
    
    def get_self_trade_prevention_modes(self) -> Dict[str, Any]:
        """
        Get self-trade prevention modes from exchange info.
        
        Weight: 1
        
        Returns:
            Dictionary with default and allowed modes
        """
        exchange_info = self.get_exchange_info()
        if 'selfTradePreventionModes' in exchange_info:
            stp_modes = {'allowed': exchange_info['selfTradePreventionModes']}
            if 'defaultSelfTradePreventionMode' in exchange_info:
                stp_modes['default'] = exchange_info['defaultSelfTradePreventionMode']
            return stp_modes
        return {'default': 'NONE', 'allowed': []}
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """
        Get available trading symbols.
        
        Weight: 10
        
        Returns:
            List of available trading symbols
        """
        client = RestClient()
        response = client.request("GET", "/api/v3/exchangeInfo").requires_auth(False).execute()
        
        symbols = []
        if response and 'symbols' in response:
            symbols = [s['symbol'] for s in response['symbols'] 
                    if s['status'] == 'TRADING']
        return symbols
    
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        """
        Get current bid/ask prices for a symbol.
        
        Weight: 1
        
        Args:
            symbol: The symbol to get prices for (e.g. "BTCUSDT")
            
        Returns:
            PriceData object with bid and ask prices, or None if not available
        """
        response = self.request("GET", "/api/v3/ticker/bookTicker").requires_auth(False) \
            .with_query_params(symbol=symbol) \
            .execute()
            
        if response:
            return PriceData(
                bid=float(response['bidPrice']), 
                ask=float(response['askPrice'])
            )
        return None
    
    def get_historical_candles(self, symbol: str, interval: str, 
                             limit: int = 500, 
                             start_time: Optional[int] = None,
                             end_time: Optional[int] = None) -> List[Candle]:
        """
        Get historical candlestick data.
        
        Weight: 1
        
        Args:
            symbol: Symbol to get candles for (e.g. "BTCUSDT")
            interval: Candle interval (e.g. "1m", "1h", "1d")
            limit: Number of candles to return (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of Candle objects
        """
        request = self.request("GET", "/api/v3/klines").requires_auth(False) \
            .with_query_params(
                symbol=symbol,
                interval=interval,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        if start_time:
            request.with_query_params(startTime=start_time)
        if end_time:
            request.with_query_params(endTime=end_time)
            
        response = request.execute()
        
        candles = []
        if response:
            for candle_data in response:
                candles.append(Candle(
                    timestamp=candle_data[0],
                    open_price=float(candle_data[1]),
                    high_price=float(candle_data[2]),
                    low_price=float(candle_data[3]),
                    close_price=float(candle_data[4]),
                    volume=float(candle_data[5]),
                    quote_volume=float(candle_data[7])
                ))
                
        return candles
        
    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Trade]:
        """
        Get recent trades for a symbol.
        
        Weight: 1
        
        Args:
            symbol: Symbol to get trades for (e.g. "BTCUSDT")
            limit: Number of trades to return (default 500, max 1000)
            
        Returns:
            List of Trade objects
        """
        response = self.request("GET", "/api/v3/trades").requires_auth(False) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            ) \
            .execute()
            
        trades = []
        if response is not None:
            for trade_data in response:
                trades.append(Trade.from_api_response(trade_data))
        
        return trades
    
    def get_historical_trades(self, symbol: str, limit: int = 500, from_id: Optional[int] = None) -> List[Trade]:
        """
        Get older trades for a symbol.
        
        Weight: 5
        
        Note: This endpoint requires API key in the request header
        
        Args:
            symbol: Symbol to get trades for (e.g. "BTCUSDT")
            limit: Number of trades to return (default 500, max 1000)
            from_id: TradeId to fetch from (optional)
            
        Returns:
            List of Trade objects
        """
        request = self.request("GET", "/api/v3/historicalTrades", RateLimitType.REQUEST_WEIGHT, 5) \
            .requires_auth(True) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        if from_id is not None:
            request.with_query_params(fromId=from_id)
            
        response = request.execute()
            
        trades = []
        if response is not None:
            for trade_data in response:
                trades.append(Trade.from_api_response(trade_data))
        
        return trades
    
    def get_aggregate_trades(self, symbol: str, limit: int = 500, from_id: Optional[int] = None,
                        start_time: Optional[int] = None, end_time: Optional[int] = None) -> List[AggTrade]:
        """
        Get compressed, aggregate trades. Trades that fill at the same time, from the same order, 
        with the same price, will have the quantity aggregated.
        
        Weight: 1
        
        Args:
            symbol: Symbol to get trades for (e.g. "BTCUSDT")
            limit: Number of trades to return (default 500, max 1000)
            from_id: ID to get aggregate trades from INCLUSIVE (optional)
            start_time: Timestamp in ms to get aggregate trades from INCLUSIVE (optional)
            end_time: Timestamp in ms to get aggregate trades until INCLUSIVE (optional)
            
        Note:
            If fromId, startTime, and endTime are not sent, the most recent aggregate trades will be returned
            
        Returns:
            List of AggTrade objects
        """
        request = self.request("GET", "/api/v3/aggTrades").requires_auth(False) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        # Add optional parameters
        if from_id is not None:
            request.with_query_params(fromId=from_id)
        if start_time is not None:
            request.with_query_params(startTime=start_time)
        if end_time is not None:
            request.with_query_params(endTime=end_time)
            
        response = request.execute()
            
        agg_trades = []
        if response is not None:
            for trade_data in response:
                agg_trades.append(AggTrade.from_api_response(trade_data))
        
        return agg_trades
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Optional[OrderBook]:
        """
        Get order book (market depth) for a symbol.
        
        Weight: Adjusted based on the limit:
        - 1-100: weight=1
        - 101-500: weight=5
        - 501-1000: weight=10
        - 1001-5000: weight=50
        
        Args:
            symbol: Symbol to get order book for (e.g. "BTCUSDT")
            limit: Number of price levels to return. Default 100; max 5000.
                If limit > 5000, the response will truncate to 5000.
            
        Returns:
            OrderBook object with bids and asks, or None if request fails
        """
        # Adjust weight based on limit
        weight = 1
        if limit > 100:
            weight = 5
        if limit > 500:
            weight = 10
        if limit > 1000:
            weight = 50
            
        response = self.request("GET", "/api/v3/depth", weight=weight).requires_auth(False) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 5000)  # Ensure limit doesn't exceed API max
            ) \
            .execute()
            
        if response is not None:
            return OrderBook.from_api_response(response)
        
        return None
    
    def get_ticker_price(self, symbol: Optional[str] = None) -> Union[TickerPrice, List[TickerPrice], None]:
        """
        Get live ticker price for a symbol or for all symbols.
        
        Weight: 
        - When symbol is provided: 1
        - When symbol is omitted: 2
        
        Args:
            symbol: Symbol to get price for (e.g. "BTCUSDT").
                If None, prices for all symbols will be returned.
            
        Returns:
            TickerPrice object if symbol is provided, or list of TickerPrice objects for all symbols
        """
        # Adjust weight based on parameters
        weight = 1
        if symbol is None:
            weight = 2
            
        request = self.request("GET", "/api/v3/ticker/price", weight=weight).requires_auth(False)
        
        if symbol is not None:
            request.with_query_params(symbol=symbol)
            
        response = request.execute()
        
        if response is None:
            return None
            
        if isinstance(response, list):
            return [TickerPrice.from_api_response(item) for item in response]
        else:
            return TickerPrice.from_api_response(response)
    
    def get_avg_price(self, symbol: str) -> Optional[AvgPrice]:
        """
        Get current average price for a symbol.
        
        Weight: 1
        
        Args:
            symbol: Symbol to get average price for (e.g. "BTCUSDT")
            
        Returns:
            AvgPrice object with average price information
        """
        response = self.request("GET", "/api/v3/avgPrice").requires_auth(False) \
            .with_query_params(symbol=symbol) \
            .execute()
            
        if response is not None:
            return AvgPrice.from_api_response(response)
        
        return None
    
    def get_24h_stats(self, symbol: Optional[str] = None, symbols: Optional[List[str]] = None, 
                    type: Optional[str] = None) -> Union[Union[PriceStats, PriceStatsMini], 
                                                      List[Union[PriceStats, PriceStatsMini]], None]:
        """
        Get 24-hour price change statistics for a symbol, multiple symbols, or all symbols.
        
        Weight:
        - When symbol is provided: 1
        - When symbol is omitted: 40
        - When symbols are provided: 
        - 1-20 symbols: 1
        - 21-100 symbols: 20
        - 101 or more symbols: 40
        
        Args:
            symbol: Symbol to get statistics for (e.g. "BTCUSDT")
            symbols: List of symbols to get statistics for. Cannot be used with 'symbol'.
            type: Response type ("FULL" or "MINI").
                  MINI omits fields: priceChangePercent, weightedAvgPrice, 
                  bidPrice, bidQty, askPrice, askQty, lastQty
            
        Returns:
            PriceStats/PriceStatsMini object or list of objects
        """
        # Adjust weight based on parameters
        weight = 1
        if symbol is None and symbols is None:
            weight = 40
        elif symbols is not None:
            symbols_count = len(symbols)
            if symbols_count > 100:
                weight = 40
            elif symbols_count > 20:
                weight = 20
            
        request = self.request("GET", "/api/v3/ticker/24hr", weight=weight).requires_auth(False)
        
        if symbol is not None:
            request.with_query_params(symbol=symbol)
        elif symbols is not None:
            # Format the symbols parameter correctly for Binance API
            # The API requires a JSON array as a string
            symbols_str = json.dumps(symbols)
            request.with_query_params(symbols=symbols_str)
            
        if type is not None:
            request.with_query_params(type=type)
            
        response = request.execute()
        
        if response is None:
            return None
            
        # Determine which model to use based on the type parameter
        is_mini = type == "MINI"
        model_class = PriceStatsMini if is_mini else PriceStats
            
        if isinstance(response, list):
            return [model_class.from_api_response(item) for item in response]
        else:
            return model_class.from_api_response(response)
    
    def get_rolling_window_stats(self, symbol: str, window_size: Optional[str] = None, 
                            type: Optional[str] = None) -> Optional[Union[RollingWindowStats, RollingWindowStatsMini]]:
        """
        Get price change statistics within a requested window of time.
        
        Weight: 2 for each requested symbol
        
        Args:
            symbol: Symbol to get statistics for (e.g. "BTCUSDT")
            window_size: Size of the rolling window. Default 1d if not provided.
                        Supported values:
                        - "1m", "2m" ... "59m" for minutes
                        - "1h", "2h" ... "23h" for hours
                        - "1d" ... "7d" for days
                        Units cannot be combined (e.g. "1d2h" is not allowed)
            type: Response type ("FULL" or "MINI").
                MINI omits fields: priceChangePercent, weightedAvgPrice
            
        Returns:
            RollingWindowStats/RollingWindowStatsMini object with price statistics
        """
        weight = 2
        
        request = self.request("GET", "/api/v3/ticker", weight=weight).requires_auth(False)
        request.with_query_params(symbol=symbol)
            
        if window_size is not None:
            request.with_query_params(windowSize=window_size)
            
        if type is not None:
            request.with_query_params(type=type)
            
        response = request.execute()
        
        if response is None:
            return None
            
        # Determine which model to use based on the type parameter
        is_mini = type == "MINI"
        model_class = RollingWindowStatsMini if is_mini else RollingWindowStats
            
        return model_class.from_api_response(response)