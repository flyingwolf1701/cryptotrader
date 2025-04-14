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

import httpx

from cryptotrader.config import get_logger
from cryptotrader.services.binance.binance_base_operations import BinanceAPIRequest
from cryptotrader.services.binance.binance_models import (
    PriceData, BinanceEndpoints, OrderRequest, Candle,
    AccountBalance, OrderStatusResponse, SymbolInfo,
    RateLimitType, OrderType, TimeInForce, OrderSide,
    SystemStatus, SelfTradePreventionMode,
    Trade, AggTrade, OrderBook, TickerPrice,
    AvgPrice, PriceStatsMini, PriceStats, RollingWindowStatsMini, RollingWindowStats
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
        """
    
    def request(self, method: str, endpoint: str, 
               limit_type: Optional[RateLimitType] = None,
               weight: int = 1) -> BinanceAPIRequest:
        """
        Create a new API request.
        """
        
        return BinanceAPIRequest(
            method=method, 
            endpoint=endpoint,
            limit_type=limit_type,
            weight=weight
        )
    
    #
    # Account endpoints
    #
    
    def get_balance(self) -> Optional[AccountBalance]:
        """
        Get account information including balances.
        
        Weight: 10
        
        Returns:
            AccountBalance object with asset balances
        """
        response = self.request("GET", "/api/v3/account", weight=10).execute()
        if response:
            return AccountBalance.from_api_response(response)
        return None
    
    def place_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> Optional[OrderStatusResponse]:
        """
        Place a new order.
        
        Weight: 1
        
        Args:
            order_request: The order details as OrderRequest object or dictionary
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        # Convert OrderRequest to dictionary if needed
        if isinstance(order_request, OrderRequest):
            params = {
                'symbol': order_request.symbol,
                'side': order_request.side.value,
                'type': order_request.order_type.value,
                'quantity': order_request.quantity
            }
            
            # Add optional parameters
            if order_request.price is not None:
                params['price'] = order_request.price
            
            if order_request.time_in_force is not None:
                params['timeInForce'] = order_request.time_in_force.value
            
            if order_request.stop_price is not None:
                params['stopPrice'] = order_request.stop_price
            
            if order_request.iceberg_qty is not None:
                params['icebergQty'] = order_request.iceberg_qty
                
            if order_request.new_client_order_id is not None:
                params['newClientOrderId'] = order_request.new_client_order_id
                
            if order_request.self_trade_prevention_mode is not None:
                params['selfTradePreventionMode'] = order_request.self_trade_prevention_mode
        else:
            # Already a dictionary
            params = order_request
        
        response = self.request("POST", "/api/v3/order", RateLimitType.ORDERS, 1) \
            .with_query_params(**params) \
            .execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, 
                client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """
        Cancel an existing order.
        
        Weight: 1
        
        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        request = self.request("DELETE", "/api/v3/order") \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            logger.error("Either order_id or client_order_id must be provided to cancel an order")
            return None
            
        response = request.execute()
        
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def get_order_status(self, symbol: str, order_id: Optional[int] = None, 
                    client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """
        Get status of an existing order.
        
        Weight: 2
        
        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        request = self.request("GET", "/api/v3/order", weight=2) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            logger.error("Either order_id or client_order_id must be provided to get order status")
            return None
            
        response = request.execute()
        
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    #
    # System endpoints
    #
    
    def get_server_time(self) -> int:
        """
        Get current server time from Binance API.
        
        Weight: 1
        
        Returns:
            Server time in milliseconds
        """
        response = self.request("GET", "/api/v3/time").execute()
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
        response = self.request("GET", "/sapi/v1/system/status").execute()
        if response:
            return SystemStatus(status_code=response.get("status", -1))
        return SystemStatus(status_code=-1)  # Unknown status
    
    #
    # Market data endpoints
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
        request = self.request("GET", "/api/v3/exchangeInfo")
        
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
        try:
            with httpx.Client() as client:
                response = client.get(f"{BinanceEndpoints.base_url}/api/v3/exchangeInfo", timeout=10)
                if response.status_code == 200:
                    exchange_info = response.json()
                    if 'symbols' in exchange_info:
                        symbols = [s['symbol'] for s in exchange_info['symbols'] 
                                 if s['status'] == 'TRADING']
                        return symbols
            return []
        except Exception as e:
            logger.error(f"Error getting symbols: {str(e)}")
            return []
    
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        """
        Get current bid/ask prices for a symbol.
        
        Weight: 1
        
        Args:
            symbol: The symbol to get prices for (e.g. "BTCUSDT")
            
        Returns:
            PriceData object with bid and ask prices, or None if not available
        """
        response = self.request("GET", "/api/v3/ticker/bookTicker") \
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
        request = self.request("GET", "/api/v3/klines") \
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
        response = self.request("GET", "/api/v3/trades") \
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
        request = self.request("GET", "/api/v3/aggTrades") \
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
            
        response = self.request("GET", "/api/v3/depth", weight=weight) \
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
            
        request = self.request("GET", "/api/v3/ticker/price", weight=weight)
        
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
        response = self.request("GET", "/api/v3/avgPrice") \
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
            
        request = self.request("GET", "/api/v3/ticker/24hr", weight=weight)
        
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
        
        request = self.request("GET", "/api/v3/ticker", weight=weight)
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