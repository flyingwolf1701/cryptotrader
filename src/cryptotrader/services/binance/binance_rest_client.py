"""
Binance REST API Client

This module provides a robust client for interacting with the Binance REST API.
It handles authentication, rate limiting, and request retries according to Binance's specifications.

Key features:
- Automatic signature generation for authenticated endpoints
- Comprehensive rate limit tracking and throttling
- Response header processing for rate limit management
- Exponential backoff and retry mechanism
- Support for all major Binance REST API endpoints
- System status monitoring
- Self-trade prevention mode support

The client maintains state between requests to optimize rate limit usage and
provides detailed logging for debugging API interactions.

Usage:
    client = RestClient(api_key, api_secret)
    
    # Market data
    btc_price = client.get_bid_ask("BTCUSDT")
    
    # Account data (authenticated)
    balance = client.get_balance()
    
    # Trading (authenticated)
    order = client.place_order(OrderRequest(...))
"""

import httpx
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Union, Tuple

from cryptotrader.services.binance.binance_models import (
    PriceData, BinanceEndpoints, OrderRequest, Candle,
    AccountBalance, OrderStatusResponse, SymbolInfo,
    RateLimit, RateLimitType, RateLimitInterval, OrderType, 
    TimeInForce, OrderSide, KlineInterval,
    SystemStatus, SelfTradePreventionMode
)

from cryptotrader.config import get_logger
logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter for Binance API"""
    
    def __init__(self):
        self.rate_limits: List[RateLimit] = []
        self.request_counts: Dict[Tuple[RateLimitType, RateLimitInterval, int], List[float]] = {}
        self.order_counts: Dict[str, int] = {}  # Track order counts for different intervals
        
    def update_rate_limits(self, rate_limits: List[Dict[str, Any]]):
        """Update rate limits from exchange info"""
        self.rate_limits = []
        for limit in rate_limits:
            self.rate_limits.append(RateLimit(
                rate_limit_type=RateLimitType(limit['rateLimitType']),
                interval=RateLimitInterval(limit['interval']),
                interval_num=limit['intervalNum'],
                limit=limit['limit']
            ))
        logger.debug(f"Updated rate limits: {self.rate_limits}")
    
    def update_counts_from_headers(self, headers: Dict[str, str]):
        """Update rate limit counts from response headers"""
        current_time = time.time()
        
        # Process weight headers (X-MBX-USED-WEIGHT-*)
        for header, value in headers.items():
            if header.startswith('X-MBX-USED-WEIGHT-'):
                # Extract interval info from header: X-MBX-USED-WEIGHT-(intervalNum)(intervalLetter)
                interval_info = header.replace('X-MBX-USED-WEIGHT-', '')
                if len(interval_info) >= 2:
                    # Extract interval number and letter
                    interval_num = int(interval_info[:-1])
                    interval_letter = interval_info[-1]
                    
                    # Map interval letter to RateLimitInterval
                    if interval_letter == 'S':
                        interval = RateLimitInterval.SECOND
                    elif interval_letter == 'M':
                        interval = RateLimitInterval.MINUTE
                    elif interval_letter == 'D':
                        interval = RateLimitInterval.DAY
                    else:
                        continue  # Unknown interval
                    
                    logger.debug(f"Current {interval.value} weight usage: {value}")
            
            # Process order count headers (X-MBX-ORDER-COUNT-*)
            elif header.startswith('X-MBX-ORDER-COUNT-'):
                # Extract interval info from header
                interval_info = header.replace('X-MBX-ORDER-COUNT-', '')
                self.order_counts[interval_info] = int(value)
                logger.debug(f"Current order count for {interval_info}: {value}")
    
    def check_rate_limit(self, limit_type: RateLimitType, weight: int = 1) -> bool:
        """Check if request can be executed without hitting rate limit"""
        current_time = time.time()
        
        for rate_limit in self.rate_limits:
            if rate_limit.rate_limit_type != limit_type:
                continue
                
            # Get time window for this rate limit
            if rate_limit.interval == RateLimitInterval.SECOND:
                window_seconds = rate_limit.interval_num
            elif rate_limit.interval == RateLimitInterval.MINUTE:
                window_seconds = rate_limit.interval_num * 60
            elif rate_limit.interval == RateLimitInterval.DAY:
                window_seconds = rate_limit.interval_num * 86400
            else:
                continue
                
            # Create key for this rate limit
            key = (rate_limit.rate_limit_type, rate_limit.interval, rate_limit.interval_num)
            
            # Initialize request counts if not exists
            if key not in self.request_counts:
                self.request_counts[key] = []
                
            # Remove timestamps outside window
            self.request_counts[key] = [ts for ts in self.request_counts[key] 
                                     if current_time - ts < window_seconds]
                
            # Check if adding this request would exceed limit
            if len(self.request_counts[key]) + weight > rate_limit.limit:
                logger.warning(
                    f"Rate limit would be exceeded: {rate_limit.rate_limit_type} "
                    f"limit of {rate_limit.limit} per {rate_limit.interval_num} "
                    f"{rate_limit.interval}(s)"
                )
                return False
        
        return True
    
    def record_request(self, limit_type: RateLimitType, weight: int = 1):
        """Record a request for rate limiting purposes"""
        current_time = time.time()
        
        for rate_limit in self.rate_limits:
            if rate_limit.rate_limit_type != limit_type:
                continue
                
            # Create key for this rate limit
            key = (rate_limit.rate_limit_type, rate_limit.interval, rate_limit.interval_num)
            
            # Initialize request counts if not exists
            if key not in self.request_counts:
                self.request_counts[key] = []
                
            # Add timestamps for this request
            for _ in range(weight):
                self.request_counts[key].append(current_time)
                
    def get_rate_limit_usage(self):
        """Get current rate limit usage information"""
        usage = {}
        current_time = time.time()
        
        for key, timestamps in self.request_counts.items():
            limit_type, interval, interval_num = key
            
            # Remove timestamps outside window
            if interval == RateLimitInterval.SECOND:
                window_seconds = interval_num
            elif interval == RateLimitInterval.MINUTE:
                window_seconds = interval_num * 60
            elif interval == RateLimitInterval.DAY:
                window_seconds = interval_num * 86400
            else:
                continue
                
            # Update counts removing expired entries
            active_timestamps = [ts for ts in timestamps if current_time - ts < window_seconds]
            self.request_counts[key] = active_timestamps
            
            # Calculate usage
            usage_key = f"{limit_type.value}_{interval_num}{interval.value[0]}"
            usage[usage_key] = len(active_timestamps)
            
        return usage


class BinanceAPIRequest:
    """Handles API request preparation and execution"""
    
    def __init__(self, client, method, endpoint, limit_type=RateLimitType.REQUEST_WEIGHT, weight=1):
        self.client = client
        self.method = method
        self.endpoint = endpoint
        self.query_params = {}
        self.body_params = {}
        self.limit_type = limit_type
        self.weight = weight
        self.max_retries = 3
        self.retry_delay = 1  # Starting retry delay in seconds
        
    def with_query_params(self, **params):
        """Add query parameters"""
        self.query_params.update(params)
        return self
        
    def with_body_params(self, **params):
        """Add body parameters"""
        self.body_params.update(params)
        return self
    
    def with_timestamp(self):
        """Add timestamp to request"""
        timestamp = int(time.time() * 1000)
        
        # Add timestamp to appropriate location based on request type
        if self.method == "GET" or self.method == "DELETE" or not self.body_params:
            self.query_params['timestamp'] = timestamp
        else:
            self.body_params['timestamp'] = timestamp
            
        return self
    
    def sign(self):
        """Add signature to request"""
        # Combine all parameters for signing
        all_params = {**self.query_params, **self.body_params}
        
        # Generate signature
        signature = self.client.generate_signature(all_params)
        
        # Add signature to query parameters
        self.query_params['signature'] = signature
        
        return self
    
    def execute(self):
        """Execute the request and return the response"""
        url = f"{self.client.base_url}{self.endpoint}"
        
        for retry_count in range(self.max_retries):
            # Check rate limit
            if not self.client.rate_limiter.check_rate_limit(self.limit_type, self.weight):
                logger.warning(f"Request would exceed rate limit for {self.limit_type}. Waiting...")
                time.sleep(self.retry_delay)  # Backoff strategy
                self.retry_delay *= 2  # Exponential backoff
                
                # Check again after waiting
                if not self.client.rate_limiter.check_rate_limit(self.limit_type, self.weight):
                    logger.error(f"Still exceeding rate limit after waiting. Request aborted.")
                    return None
        
            try:
                if self.method == "GET":
                    response = self.client.http.get(url, params=self.query_params, headers=self.client.headers)
                elif self.method == "POST":
                    if not self.body_params:
                        response = self.client.http.post(url, params=self.query_params, headers=self.client.headers)
                    else:
                        response = self.client.http.post(
                            url, 
                            params=self.query_params, 
                            data=self.body_params, 
                            headers=self.client.headers
                        )
                elif self.method == "DELETE":
                    response = self.client.http.delete(url, params=self.query_params, headers=self.client.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {self.method}")
                    
                response.raise_for_status()
                
                # Record the request for rate limiting
                self.client.rate_limiter.record_request(self.limit_type, self.weight)
                
                # Update counts from headers
                self.client.rate_limiter.update_counts_from_headers(response.headers)
                
                return response.json()
                
            except httpx.HTTPStatusError as e:
                # Handle specific error codes
                if e.response.status_code == 429:
                    logger.error("Rate limit exceeded!")
                    # Extract retry-after if available
                    retry_after = int(e.response.headers.get('Retry-After', self.retry_delay))
                    logger.info(f"Retry after {retry_after} seconds")
                    
                    if retry_count < self.max_retries - 1:
                        logger.info(f"Retrying in {retry_after} seconds (attempt {retry_count + 1}/{self.max_retries})")
                        time.sleep(retry_after)
                        continue
                    
                    return {"error": "Rate limit exceeded", "retry_after": retry_after}
                elif e.response.status_code == 418:
                    logger.error("IP has been auto-banned for repeated violations!")
                    retry_after = int(e.response.headers.get('Retry-After', 300))  # Default to 5 minutes
                    logger.info(f"IP banned. Retry after {retry_after} seconds")
                    
                    if retry_count < self.max_retries - 1:
                        logger.info(f"Retrying in {retry_after} seconds (attempt {retry_count + 1}/{self.max_retries})")
                        time.sleep(retry_after)
                        continue
                        
                    return {"error": "IP banned", "retry_after": retry_after}
                
                logger.error(
                    "Error while making %s request to %s: %s (error code %s)", 
                    self.method, self.endpoint, e.response.text, e.response.status_code
                )
                return None
            except httpx.RequestError as e:
                logger.error(
                    "Request error while making %s request to %s: %s", 
                    self.method, self.endpoint, str(e)
                )
                
                if retry_count < self.max_retries - 1:
                    backoff_time = self.retry_delay * (2 ** retry_count)  # Exponential backoff
                    logger.info(f"Retrying in {backoff_time} seconds (attempt {retry_count + 1}/{self.max_retries})")
                    time.sleep(backoff_time)
                    continue
                    
                return None


class RestClient:
    """Binance REST API client"""
    
    def __init__(self, public_key: str, secret_key: str):
        # Initialize endpoints
        endpoints = BinanceEndpoints()
        self.base_url = endpoints.base_url
        
        # API credentials
        self.public_key = public_key
        self.secret_key = secret_key
        self.headers = {'X-MBX-APIKEY': public_key}
        
        # State
        self.prices: Dict[str, PriceData] = {}
        self.exchange_info = None
        self.self_trade_prevention_modes = []
        self.default_self_trade_prevention_mode = None
        
        # Rate limiter
        self.rate_limiter = RateLimiter()
        
        # HTTP client
        self.http = httpx.Client(timeout=30.0)
        
        # Initialize rate limits - fetch exchange info
        self._init_exchange_info()
        
        logger.info("Binance REST Client successfully initialized")
    
    def _init_exchange_info(self):
        """Initialize exchange info and rate limits"""
        try:
            response = self.request("GET", "/api/v3/exchangeInfo").execute()
            if response:
                self.exchange_info = response
                if 'rateLimits' in response:
                    self.rate_limiter.update_rate_limits(response['rateLimits'])
                    logger.info("Rate limits initialized")
                    
                # Process self-trade prevention modes
                if 'defaultSelfTradePreventionMode' in response:
                    self.default_self_trade_prevention_mode = response['defaultSelfTradePreventionMode']
                    
                if 'allowedSelfTradePreventionModes' in response:
                    self.self_trade_prevention_modes = response['allowedSelfTradePreventionModes']
                    
                logger.info(f"Self-trade prevention: Default={self.default_self_trade_prevention_mode}, "
                           f"Allowed={self.self_trade_prevention_modes}")
        except Exception as e:
            logger.warning(f"Error initializing exchange info: {e}")
    
    def generate_signature(self, data):
        """Generate HMAC-SHA256 signature for API authentication"""
        return hmac.new(
            self.secret_key.encode(),
            urlencode(data).encode(),
            hashlib.sha256
        ).hexdigest()
    
    def request(self, method, endpoint, limit_type=RateLimitType.REQUEST_WEIGHT, weight=1):
        """Create a new API request builder"""
        return BinanceAPIRequest(self, method, endpoint, limit_type, weight)
    
    def get_bid_ask(self, symbol: str) -> Optional[PriceData]:
        """Get current bid/ask prices for a symbol"""
        response = self.request("GET", "/api/v3/ticker/bookTicker") \
            .with_query_params(symbol=symbol) \
            .execute()
            
        if response is not None:
            price_data = PriceData(
                bid=float(response['bidPrice']),
                ask=float(response['askPrice'])
            )
            self.prices[symbol] = price_data
            return price_data
        
        return self.prices.get(symbol)
    
    def get_balance(self) -> AccountBalance:
        """Get account balance information"""
        response = self.request("GET", "/api/v3/account", weight=10) \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response is not None:
            return AccountBalance.from_api_response(response)
        
        return AccountBalance(assets={})
    
    def place_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> Optional[OrderStatusResponse]:
        """Place a new order"""
        # Determine weight based on order type
        weight = 1
        
        # Create a request builder
        request = self.request("POST", "/api/v3/order", RateLimitType.ORDERS, weight)
        
        # Process OrderRequest object
        if isinstance(order_request, OrderRequest):
            # Convert enums to strings for API
            side = order_request.side.value if isinstance(order_request.side, OrderSide) else order_request.side
            order_type = order_request.order_type.value if isinstance(order_request.order_type, OrderType) else order_request.order_type
            
            # Add query parameters
            params = {
                "symbol": order_request.symbol,
                "side": side,
                "type": order_type,
                "quantity": order_request.quantity
            }
            
            # Add conditional parameters
            if order_request.price is not None:
                params["price"] = order_request.price
                
            if order_request.time_in_force is not None:
                time_in_force = order_request.time_in_force.value if isinstance(order_request.time_in_force, TimeInForce) else order_request.time_in_force
                params["timeInForce"] = time_in_force
                
            if order_request.stop_price is not None:
                params["stopPrice"] = order_request.stop_price
                
            if order_request.iceberg_qty is not None:
                params["icebergQty"] = order_request.iceberg_qty
                
            if order_request.new_client_order_id is not None:
                params["newClientOrderId"] = order_request.new_client_order_id
                
            # Add self-trade prevention mode if specified
            if hasattr(order_request, 'self_trade_prevention_mode') and order_request.self_trade_prevention_mode:
                params["selfTradePreventionMode"] = order_request.self_trade_prevention_mode
                
            request.with_query_params(**params)
        else:
            # Handle dictionary input
            request.with_query_params(**order_request)
        
        # Add timestamp and signature, then execute
        response = request.with_timestamp().sign().execute()
        
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, 
                   client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """Cancel an existing order"""
        request = self.request("DELETE", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 1) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
            
        response = request.with_timestamp().sign().execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def get_order_status(self, symbol: str, order_id: Optional[int] = None, 
                       client_order_id: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """Get status of an existing order"""
        request = self.request("GET", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 2) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            raise ValueError("Either order_id or client_order_id must be provided")
            
        response = request.with_timestamp().sign().execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def get_historical_candles(self, symbol: str, interval: str, 
                              limit: int = 500, 
                              start_time: Optional[int] = None,
                              end_time: Optional[int] = None) -> List[Candle]:
        """
        Get historical candlestick data
        
        Args:
            symbol: Symbol to get candles for (e.g. "BTCUSDT")
            interval: Candle interval (e.g. "1m", "1h", "1d")
            limit: Number of candles to return (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of Candle objects
        """
        # Validate interval
        valid_intervals = [interval.value for interval in KlineInterval]
        if interval not in valid_intervals:
            logger.warning(f"Invalid interval: {interval}. Using 1h instead.")
            interval = "1h"
            
        # Adjust request weight based on limit
        weight = 1
        if limit > 100:
            weight = 2
        if limit > 500:
            weight = 5
            
        # Build request
        request = self.request("GET", "/api/v3/klines", RateLimitType.REQUEST_WEIGHT, weight) \
            .with_query_params(
                symbol=symbol,
                interval=interval,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        # Add optional parameters
        if start_time:
            request.with_query_params(startTime=start_time)
        if end_time:
            request.with_query_params(endTime=end_time)
            
        response = request.execute()
        candles = []
        
        if response is not None:
            for c in response:
                candle = Candle(
                    timestamp=int(c[0]),
                    open_price=float(c[1]),
                    high_price=float(c[2]),
                    low_price=float(c[3]),
                    close_price=float(c[4]),
                    volume=float(c[5]),
                    quote_volume=float(c[7])
                )
                candles.append(candle)
        
        return candles
    
    def get_exchange_info(self, symbol: Optional[str] = None, 
                     symbols: Optional[List[str]] = None,
                     permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get exchange information
        
        Args:
            symbol: Single symbol to get info for
            symbols: Multiple symbols to get info for
            permissions: Permissions to filter by (e.g. ["SPOT"])
            
        Returns:
            Exchange information dictionary
        """
        # TODO: Implement proper URL encoding for multi-symbol requests
        # The Binance API expects a specific format for the 'symbols' parameter that our current
        # implementation struggles with. The current workaround is to fetch all symbols and filter
        # client-side, which is less efficient but more reliable.
        # 
        # Future improvement:
        # - Research exact format required by Binance API for array parameters
        # - Implement proper encoding that matches Binance's expectations
        # - Add test cases to verify the encoding works consistently
        
        # Create request with the optional parameters
        request = self.request("GET", "/api/v3/exchangeInfo", weight=10)
        
        if symbol:
            request.with_query_params(symbol=symbol)
        elif symbols:
            # Use a single symbol approach if the multi-symbol approach fails
            if len(symbols) == 1:
                request.with_query_params(symbol=symbols[0])
            else:
                logger.warning(
                    "Using inefficient workaround for multi-symbol exchange info request. "
                    f"Fetching all symbols and filtering for {len(symbols)} symbols client-side. "
                    "This may impact performance if called frequently."
                )
                
                # Get full exchange info and filter manually
                response = request.execute()
                
                if response and 'symbols' in response:
                    # Filter symbols
                    filtered_symbols = [s for s in response['symbols'] if s['symbol'] in symbols]
                    
                    # Create a filtered response
                    filtered_response = {**response}
                    filtered_response['symbols'] = filtered_symbols
                    
                    self.exchange_info = filtered_response
                    
                    # Update self-trade prevention modes
                    if 'defaultSelfTradePreventionMode' in response:
                        self.default_self_trade_prevention_mode = response['defaultSelfTradePreventionMode']
                        
                    if 'allowedSelfTradePreventionModes' in response:
                        self.self_trade_prevention_modes = response['allowedSelfTradePreventionModes']
                    
                    return filtered_response
                
                return self.exchange_info or {}
                
        elif permissions:
            # Just use a simple permission string for now
            if len(permissions) == 1:
                request.with_query_params(permissions=permissions[0])
            else:
                logger.warning(
                    "Using inefficient workaround for multi-permission exchange info request. "
                    "Fetching all exchange info without filtering."
                )
                
                # Get full exchange info and return as is
                response = request.execute()
                
                if response:
                    self.exchange_info = response
                    
                    # Update self-trade prevention modes
                    if 'defaultSelfTradePreventionMode' in response:
                        self.default_self_trade_prevention_mode = response['defaultSelfTradePreventionMode']
                        
                    if 'allowedSelfTradePreventionModes' in response:
                        self.self_trade_prevention_modes = response['allowedSelfTradePreventionModes']
                
                return self.exchange_info or {}
        
        # Execute the request (for cases other than multi-symbol handling)
        response = request.execute()
        
        if response:
            self.exchange_info = response
            
            # Update self-trade prevention modes
            if 'defaultSelfTradePreventionMode' in response:
                self.default_self_trade_prevention_mode = response['defaultSelfTradePreventionMode']
                
            if 'allowedSelfTradePreventionModes' in response:
                self.self_trade_prevention_modes = response['allowedSelfTradePreventionModes']
        
        return self.exchange_info or {}
    
    def get_symbol_info(self, symbol: str) -> Optional[SymbolInfo]:
        """Get information for a specific symbol"""
        # Use the more efficient direct API call for a single symbol
        exchange_info = self.get_exchange_info(symbol=symbol)
        
        if 'symbols' in exchange_info:
            for symbol_data in exchange_info['symbols']:
                if symbol_data['symbol'] == symbol:
                    return SymbolInfo.from_api_response(symbol_data)
        
        return None
    
    def get_system_status(self) -> SystemStatus:
        """
        Get system status
        
        Returns:
            SystemStatus object with status code (0: normal, 1: maintenance)
        """
        response = self.request("GET", "/sapi/v1/system/status") \
            .with_timestamp() \
            .sign() \
            .execute()
            
        if response is not None and 'status' in response:
            return SystemStatus(status_code=response['status'])
        
        # Default to unknown status if API call fails
        return SystemStatus(status_code=-1)
    
    def get_self_trade_prevention_modes(self) -> Dict[str, Any]:
        """
        Get self-trade prevention modes from exchange info
        
        Returns:
            Dictionary with default and allowed modes
        """
        # Ensure exchange info is loaded
        if not self.exchange_info:
            self.get_exchange_info()
            
        return {
            "default": self.default_self_trade_prevention_mode,
            "allowed": self.self_trade_prevention_modes
        }
    
    @staticmethod
    def get_symbols_binance() -> List[str]:
        """Get available trading symbols"""
        try:
            with httpx.Client() as client:
                response = client.get("https://api.binance.us/api/v3/exchangeInfo")
                response.raise_for_status()
                
                symbols = []
                for symbol_data in response.json()['symbols']:
                    # Only include TRADING symbols
                    if symbol_data['status'] == 'TRADING':
                        symbols.append(symbol_data['symbol'])
                return symbols
        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger.error(f"Error fetching Binance symbols: {e}")
            return []
    
    def get_server_time(self) -> int:
        """Get current server time"""
        response = self.request("GET", "/api/v3/time").execute()
        if response and 'serverTime' in response:
            return int(response['serverTime'])
        return int(time.time() * 1000)
    
    def check_server_time(self) -> int:
        """Check time difference between local and server time"""
        local_time = int(time.time() * 1000)
        server_time = self.get_server_time()
        diff = abs(local_time - server_time)
        
        if diff > 1000:  # More than 1 second difference
            logger.warning(f"Time drift detected: {diff}ms difference between local and server time")
        
        return diff
    
    def __del__(self):
        """Cleanup resources when instance is being destroyed"""
        if hasattr(self, 'http') and self.http:
            self.http.close()