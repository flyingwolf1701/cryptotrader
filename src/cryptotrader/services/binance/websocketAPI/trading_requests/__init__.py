"""
Binance WebSocket API Trading Requests Module

This module provides a comprehensive set of functions for executing trading operations
via the Binance WebSocket API. It includes functionality for placing, canceling, and 
querying orders, as well as managing OCO (One-Cancels-the-Other) orders.
"""

# Order creation/modification
from cryptotrader.services.binance.websocketAPI.trading_requests.place_new_order import (
    place_new_order,
    process_place_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.test_new_order import (
    test_new_order,
    process_test_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.replace_order import (
    replace_order,
    process_replace_order_response
)

# Order retrieval
from cryptotrader.services.binance.websocketAPI.trading_requests.query_order import (
    query_order,
    process_query_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.current_open_orders import (
    get_current_open_orders,
    process_open_orders_response
)

# Order cancellation
from cryptotrader.services.binance.websocketAPI.trading_requests.cancel_order import (
    cancel_order,
    process_cancel_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.cancel_open_orders import (
    cancel_open_orders,
    process_cancel_open_orders_response
)

# OCO order operations
from cryptotrader.services.binance.websocketAPI.trading_requests.create_new_oco_order import (
    create_new_oco_order,
    process_create_oco_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.get_oco_order import (
    get_oco_order,
    process_get_oco_order_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.get_open_oco_orders import (
    get_open_oco_orders,
    process_open_oco_orders_response
)
from cryptotrader.services.binance.websocketAPI.trading_requests.cancel_oco_order import (
    cancel_oco_order,
    process_cancel_oco_order_response
)

__all__ = [
    # Order creation/modification
    'place_new_order',
    'process_place_order_response',
    'test_new_order',
    'process_test_order_response',
    'replace_order',
    'process_replace_order_response',
    
    # Order retrieval
    'query_order',
    'process_query_order_response',
    'get_current_open_orders',
    'process_open_orders_response',
    
    # Order cancellation
    'cancel_order',
    'process_cancel_order_response',
    'cancel_open_orders',
    'process_cancel_open_orders_response',
    
    # OCO order operations
    'create_new_oco_order',
    'process_create_oco_order_response',
    'get_oco_order',
    'process_get_oco_order_response',
    'get_open_oco_orders',
    'process_open_oco_orders_response',
    'cancel_oco_order',
    'process_cancel_oco_order_response'
]