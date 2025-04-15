"""
Binance REST API Order Operations

This module provides order management functionality for the Binance API.
It includes functions for:
- Placing new orders
- Canceling existing orders
- Checking order status
- Retrieving order history
- Getting open orders
- Managing trades
- Cancel-replace operations
- Querying self-trade prevention matches

These functions handle trading operations via the Binance API.
"""

from typing import Dict, List, Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.models import (
    OrderRequest, OrderStatusResponse, RateLimitType
)

logger = get_logger(__name__)

class OrderOperations:
    """
    Binance REST API order operations.
    
    Provides methods for managing orders via the Binance API.
    """
    
    def __init__(self, request_builder):
        """
        Initialize order operations with a request builder function.
        
        Args:
            request_builder: Function to create API requests
        """
        self.request = request_builder
    
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
            .requires_auth(True) \
            .with_query_params(**params) \
            .execute()
            
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def test_new_order(self, order_request: Union[OrderRequest, Dict[str, Any]]) -> bool:
        """
        Test new order creation without actually placing an order.
        
        Weight: 1
        
        Args:
            order_request: The order details as OrderRequest object or dictionary
            
        Returns:
            True if test was successful, False otherwise
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
        
        response = self.request("POST", "/api/v3/order/test", RateLimitType.REQUEST_WEIGHT, 1) \
            .requires_auth(True) \
            .with_query_params(**params) \
            .execute()
            
        # Test order endpoint returns empty dict on success
        return response is not None
    
    def cancel_order(self, symbol: str, order_id: Optional[int] = None, 
                client_order_id: Optional[str] = None,
                new_client_order_id: Optional[str] = None,
                cancel_restrictions: Optional[str] = None) -> Optional[OrderStatusResponse]:
        """
        Cancel an existing order.
        
        Weight: 1
        
        Args:
            symbol: The symbol for the order (e.g. "BTCUSDT")
            order_id: The order ID assigned by Binance
            client_order_id: The client order ID if used when placing the order
            new_client_order_id: Used to uniquely identify this cancel
            cancel_restrictions: Conditions for cancellation (ONLY_NEW, ONLY_PARTIALLY_FILLED)
            
        Returns:
            OrderStatusResponse object with order status details, or None if failed
        """
        request = self.request("DELETE", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 1) \
            .requires_auth(True) \
            .with_query_params(symbol=symbol)
            
        if order_id:
            request.with_query_params(orderId=order_id)
        elif client_order_id:
            request.with_query_params(origClientOrderId=client_order_id)
        else:
            logger.error("Either order_id or client_order_id must be provided to cancel an order")
            return None
            
        if new_client_order_id:
            request.with_query_params(newClientOrderId=new_client_order_id)
            
        if cancel_restrictions:
            request.with_query_params(cancelRestrictions=cancel_restrictions)
            
        response = request.execute()
        
        if response:
            return OrderStatusResponse.from_api_response(response)
        return None
    
    def cancel_all_orders(self, symbol: str) -> List[OrderStatusResponse]:
        """
        Cancel all active orders on a symbol.
        
        Weight: 1
        
        Args:
            symbol: The symbol to cancel all orders for (e.g. "BTCUSDT")
            
        Returns:
            List of OrderStatusResponse objects for each canceled order
        """
        response = self.request("DELETE", "/api/v3/openOrders", RateLimitType.REQUEST_WEIGHT, 1) \
            .requires_auth(True) \
            .with_query_params(symbol=symbol) \
            .execute()
            
        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []
    
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
        request = self.request("GET", "/api/v3/order", RateLimitType.REQUEST_WEIGHT, 2) \
            .requires_auth(True) \
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
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[OrderStatusResponse]:
        """
        Get all open orders on a symbol or all symbols.
        
        Weight: 
        - 3 for a single symbol
        - 40 when the symbol parameter is omitted
        
        Args:
            symbol: Optional symbol to get open orders for (e.g. "BTCUSDT")
                  If None, gets orders for all symbols
            
        Returns:
            List of OrderStatusResponse objects with open order details
        """
        # Adjust weight based on parameters
        weight = 3
        if symbol is None:
            weight = 40
            
        request = self.request("GET", "/api/v3/openOrders", RateLimitType.REQUEST_WEIGHT, weight) \
            .requires_auth(True)
            
        if symbol:
            request.with_query_params(symbol=symbol)
            
        response = request.execute()
        
        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []
    
    def get_all_orders(self, symbol: str, order_id: Optional[int] = None,
                     start_time: Optional[int] = None, end_time: Optional[int] = None,
                     limit: int = 500) -> List[OrderStatusResponse]:
        """
        Get all orders (active, canceled, or filled) for a specific symbol.
        
        Weight: 10
        
        Args:
            symbol: The symbol to get orders for (e.g. "BTCUSDT")
            order_id: If specified, gets orders >= this order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Maximum number of orders to return (default 500, max 1000)
            
        Returns:
            List of OrderStatusResponse objects with order details
        """
        request = self.request("GET", "/api/v3/allOrders", RateLimitType.REQUEST_WEIGHT, 10) \
            .requires_auth(True) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        if order_id:
            request.with_query_params(orderId=order_id)
            
        if start_time:
            request.with_query_params(startTime=start_time)
            
        if end_time:
            request.with_query_params(endTime=end_time)
            
        response = request.execute()
        
        if response:
            return [OrderStatusResponse.from_api_response(order) for order in response]
        return []
    
    def get_order_rate_limits(self) -> List[Dict[str, Any]]:
        """
        Get the current order rate limits for all time intervals.
        
        Weight: 20
        
        Returns:
            List of rate limit information
        """
        response = self.request("GET", "/api/v3/rateLimit/order", RateLimitType.REQUEST_WEIGHT, 20) \
            .requires_auth(True) \
            .execute()
            
        return response if response else []
    
    def get_my_trades(self, symbol: str, order_id: Optional[int] = None,
                    start_time: Optional[int] = None, end_time: Optional[int] = None,
                    from_id: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get trades for a specific symbol.
        
        Weight: 10
        
        Args:
            symbol: The symbol to get trades for (e.g. "BTCUSDT")
            order_id: If specified, get trades for this order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            from_id: TradeId to fetch from (gets trades >= from_id)
            limit: Maximum number of trades to return (default 500, max 1000)
            
        Returns:
            List of trade information
        """
        request = self.request("GET", "/api/v3/myTrades", RateLimitType.REQUEST_WEIGHT, 10) \
            .requires_auth(True) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        if order_id:
            request.with_query_params(orderId=order_id)
            
        if start_time:
            request.with_query_params(startTime=start_time)
            
        if end_time:
            request.with_query_params(endTime=end_time)
            
        if from_id:
            request.with_query_params(fromId=from_id)
            
        response = request.execute()
        
        return response if response else []
    
    def cancel_replace_order(self, symbol: str, cancel_replace_mode: str, 
                           side: str, type: str, 
                           cancel_order_id: Optional[int] = None,
                           cancel_client_order_id: Optional[str] = None,
                           **kwargs) -> Dict[str, Any]:
        """
        Cancel an existing order and place a new one.
        
        Weight: 1
        
        Args:
            symbol: The trading pair (e.g., "BTCUSDT")
            cancel_replace_mode: How to handle failures (STOP_ON_FAILURE or ALLOW_FAILURE)
            side: Order side (BUY or SELL)
            type: Order type (LIMIT, MARKET, etc.)
            cancel_order_id: ID of the order to cancel
            cancel_client_order_id: Client order ID of the order to cancel
            **kwargs: Additional parameters for the new order
            
        Returns:
            Response containing cancellation and new order status
        """
        if not cancel_order_id and not cancel_client_order_id:
            logger.error("Either cancel_order_id or cancel_client_order_id must be provided")
            return {}
            
        params = {
            'symbol': symbol,
            'cancelReplaceMode': cancel_replace_mode,
            'side': side,
            'type': type
        }
        
        if cancel_order_id:
            params['cancelOrderId'] = cancel_order_id
        elif cancel_client_order_id:
            params['cancelOrigClientOrderId'] = cancel_client_order_id
            
        # Add any other parameters
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value
                
        response = self.request("POST", "/api/v3/order/cancelReplace", RateLimitType.REQUEST_WEIGHT, 1) \
            .requires_auth(True) \
            .with_query_params(**params) \
            .execute()
            
        return response if response else {}
    
    def get_prevented_matches(self, symbol: str, prevented_match_id: Optional[int] = None,
                            order_id: Optional[int] = None, 
                            from_prevented_match_id: Optional[int] = None,
                            limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get orders that were expired because of self-trade prevention.
        
        Weight: 
        - 1 for invalid symbol
        - 1 when querying by preventedMatchId
        - 10 when querying by orderId
        
        Args:
            symbol: The symbol to get prevented matches for
            prevented_match_id: Specific prevented match ID to query
            order_id: Filter by order ID
            from_prevented_match_id: Get matches from this ID onwards
            limit: Maximum number of matches to return (default 500, max 1000)
            
        Returns:
            List of prevented match information
        """
        request = self.request("GET", "/api/v3/myPreventedMatches", RateLimitType.REQUEST_WEIGHT, 10) \
            .requires_auth(True) \
            .with_query_params(
                symbol=symbol,
                limit=min(limit, 1000)  # Ensure limit doesn't exceed API max
            )
            
        if prevented_match_id:
            request.with_query_params(preventedMatchId=prevented_match_id)
            
        if order_id:
            request.with_query_params(orderId=order_id)
            
        if from_prevented_match_id:
            request.with_query_params(fromPreventedMatchId=from_prevented_match_id)
            
        response = request.execute()
        
        return response if response else []