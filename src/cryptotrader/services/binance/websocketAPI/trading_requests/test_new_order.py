"""
Binance WebSocket API Test New Order Request

This module provides functionality to test a new order without actually placing it.
It follows the Binance WebSocket API specifications for the 'order.test' endpoint.
"""

from typing import Dict, List, Optional, Any, Callable, Awaitable

from cryptotrader.config import get_logger
from cryptotrader.services.binance.websocketAPI.base_operations import BinanceWebSocketConnection, SecurityType
from cryptotrader.services.binance.models import OrderSide, OrderType, TimeInForce

logger = get_logger(__name__)

async def test_new_order(
    connection: BinanceWebSocketConnection,
    symbol: str,
    side: OrderSide,
    order_type: OrderType,
    quantity: Optional[float] = None,
    quote_order_qty: Optional[float] = None,
    price: Optional[float] = None,
    time_in_force: Optional[TimeInForce] = None,
    stop_price: Optional[float] = None,
    trailing_delta: Optional[int] = None,
    iceberg_qty: Optional[float] = None,
    new_client_order_id: Optional[str] = None,
    self_trade_prevention_mode: Optional[str] = None,
    callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
) -> str:
    """
    Test a new order without actually placing it.
    
    Validates new order parameters and verifies signature but does not send
    the order into the matching engine.
    
    Endpoint: order.test
    Weight: 1
    Security Type: TRADE (Requires API key and signature)
    
    Args:
        connection: Active WebSocket connection
        symbol: Trading symbol (e.g., 'BTCUSDT')
        side: Order side (BUY or SELL)
        order_type: Order type (LIMIT, MARKET, STOP_LOSS, etc.)
        quantity: Order quantity (required for most order types)
        quote_order_qty: Quote order quantity (required for MARKET orders using quote quantity)
        price: Order price (required for LIMIT and LIMIT_MAKER orders)
        time_in_force: Time in force (GTC, IOC, FOK) (required for LIMIT orders)
        stop_price: Stop price (required for STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT)
        trailing_delta: Trailing delta for trailing stop orders
        iceberg_qty: Iceberg quantity for iceberg orders
        new_client_order_id: Client order ID (optional)
        self_trade_prevention_mode: Self trade prevention mode
        callback: Optional callback function for the response
        
    Returns:
        Message ID of the request
        
    Raises:
        ConnectionError: If WebSocket is not connected
        ValueError: If required parameters for the order type are missing
    """
    # Validate required parameters
    if not symbol:
        raise ValueError("Symbol parameter is required")
    
    if not isinstance(side, OrderSide):
        raise ValueError(f"Side must be a valid OrderSide value (BUY or SELL)")
    
    if not isinstance(order_type, OrderType):
        raise ValueError(f"Order type must be a valid OrderType value")
    
    # Validate parameters based on order type
    if order_type == OrderType.LIMIT:
        if price is None:
            raise ValueError("Price is required for LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for LIMIT orders")
        if time_in_force is None:
            raise ValueError("Time in force is required for LIMIT orders")
    
    elif order_type == OrderType.LIMIT_MAKER:
        if price is None:
            raise ValueError("Price is required for LIMIT_MAKER orders")
        if quantity is None:
            raise ValueError("Quantity is required for LIMIT_MAKER orders")
    
    elif order_type == OrderType.MARKET:
        if quantity is None and quote_order_qty is None:
            raise ValueError("Either quantity or quoteOrderQty must be provided for MARKET orders")
    
    elif order_type == OrderType.STOP_LOSS:
        if quantity is None:
            raise ValueError("Quantity is required for STOP_LOSS orders")
        if stop_price is None and trailing_delta is None:
            raise ValueError("Either stopPrice or trailingDelta must be provided for STOP_LOSS orders")
    
    elif order_type == OrderType.STOP_LOSS_LIMIT:
        if price is None:
            raise ValueError("Price is required for STOP_LOSS_LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for STOP_LOSS_LIMIT orders")
        if time_in_force is None:
            raise ValueError("Time in force is required for STOP_LOSS_LIMIT orders")
        if stop_price is None and trailing_delta is None:
            raise ValueError("Either stopPrice or trailingDelta must be provided for STOP_LOSS_LIMIT orders")
    
    elif order_type == OrderType.TAKE_PROFIT:
        if quantity is None:
            raise ValueError("Quantity is required for TAKE_PROFIT orders")
        if stop_price is None and trailing_delta is None:
            raise ValueError("Either stopPrice or trailingDelta must be provided for TAKE_PROFIT orders")
    
    elif order_type == OrderType.TAKE_PROFIT_LIMIT:
        if price is None:
            raise ValueError("Price is required for TAKE_PROFIT_LIMIT orders")
        if quantity is None:
            raise ValueError("Quantity is required for TAKE_PROFIT_LIMIT orders")
        if time_in_force is None:
            raise ValueError("Time in force is required for TAKE_PROFIT_LIMIT orders")
        if stop_price is None and trailing_delta is None:
            raise ValueError("Either stopPrice or trailingDelta must be provided for TAKE_PROFIT_LIMIT orders")
    
    # Validate iceberg orders
    if iceberg_qty is not None and time_in_force != TimeInForce.GTC:
        raise ValueError("Iceberg orders must have timeInForce set to GTC")
    
    # Prepare request parameters
    params = {
        "symbol": symbol,
        "side": side.value,
        "type": order_type.value
    }
    
    # Add optional parameters if provided
    if quantity is not None:
        params["quantity"] = quantity
    
    if quote_order_qty is not None:
        params["quoteOrderQty"] = quote_order_qty
    
    if price is not None:
        params["price"] = price
    
    if time_in_force is not None:
        params["timeInForce"] = time_in_force.value
    
    if stop_price is not None:
        params["stopPrice"] = stop_price
    
    if trailing_delta is not None:
        params["trailingDelta"] = trailing_delta
    
    if iceberg_qty is not None:
        params["icebergQty"] = iceberg_qty
    
    if new_client_order_id is not None:
        params["newClientOrderId"] = new_client_order_id
    
    if self_trade_prevention_mode is not None:
        params["selfTradePreventionMode"] = self_trade_prevention_mode
    
    # Send the request with TRADE security type (requires API key and signature)
    msg_id = await connection.send(
        method="order.test",
        params=params,
        security_type=SecurityType.TRADE
    )
    
    logger.debug(f"Sent test new order request for {symbol} {side.value} {order_type.value} with ID: {msg_id}")
    return msg_id

async def process_test_order_response(response: Dict[str, Any]) -> bool:
    """
    Process the test order response.
    
    Args:
        response: WebSocket response data
        
    Returns:
        True if test was successful, False otherwise
    """
    if not response:
        logger.error("Invalid test order response: empty response")
        return False
    
    if 'status' in response and response['status'] == 200:
        return True
    
    if 'error' in response:
        error = response.get('error', {})
        error_code = error.get('code', 0)
        error_msg = error.get('msg', 'Unknown error')
        logger.error(f"Test order failed with code {error_code}: {error_msg}")
    
    return False