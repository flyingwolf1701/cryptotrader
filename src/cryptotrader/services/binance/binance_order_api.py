"""
Binance REST API Order Operations

This module provides order management functionality for the Binance API.
It includes functions for:
- Placing new orders
- Canceling existing orders
- Checking order status

These functions are extracted from the main RestClient to modularize the codebase.
"""

from typing import Dict,  Optional, Any, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.binance_models import (
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