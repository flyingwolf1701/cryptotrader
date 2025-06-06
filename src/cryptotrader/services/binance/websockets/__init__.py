"""
Binance WebSocket API Module

This module provides a comprehensive client for interacting with the Binance WebSocket API,
including market data, trading operations, and system information.
"""

# Import base operations
from cryptotrader.services.binance.websockets.baseOperations import (
    BinanceWebSocketConnection,
    SecurityType,
)

# Import market data request operations
from cryptotrader.services.binance.websockets.market_data_requests.order_book import (
    get_order_book_ws,
    process_order_book_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.recent_trades import (
    get_recent_trades_ws,
    process_recent_trades_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.historical_trades import (
    get_historical_trades_ws,
    process_historical_trades_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.klines import (
    get_klines_ws,
    process_klines_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.aggregate_trades import (
    get_aggregate_trades_ws,
    process_aggregate_trades_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.symbol_price_ticker import (
    get_price_ticker,
    process_price_ticker_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.symbol_order_book_ticker import (
    get_book_ticker,
    process_book_ticker_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.ticker_price_24h import (
    get_24h_ticker,
    process_24h_ticker_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.rolling_window_price import (
    getRollingWindowStatsWS,
    process_rolling_window_response,
)
from cryptotrader.services.binance.websockets.market_data_requests.current_average_price import (
    getAvgPriceWS,
    process_avg_price_response,
)

# Import trading request operations
from cryptotrader.services.binance.websockets.trading_requests.place_new_order import (
    place_new_order,
    process_place_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.testNewOrderWS import (
    testNewOrderWS,
    process_test_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.replace_order import (
    replace_order,
    process_replace_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.query_order import (
    query_order,
    process_query_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.current_open_orders import (
    get_current_open_orders,
    process_open_orders_response,
)
from cryptotrader.services.binance.websockets.trading_requests.cancelOrderWS import (
    cancelOrderWS,
    process_cancel_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.cancel_open_orders import (
    cancel_open_orders,
    process_cancel_open_orders_response,
)
from cryptotrader.services.binance.websockets.trading_requests.create_new_oco_order import (
    create_new_oco_order,
    process_create_oco_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.getOcoOrderWS import (
    getOcoOrderWS,
    process_get_oco_order_response,
)
from cryptotrader.services.binance.websockets.trading_requests.getOpenOcoOrdersWS import (
    getOpenOcoOrdersWS,
    process_open_oco_orders_response,
)
from cryptotrader.services.binance.websockets.trading_requests.cancel_oco_order import (
    cancel_oco_order,
    process_cancel_oco_order_response,
)

# Import account request operations
from cryptotrader.services.binance.websockets.accountRequests.getUserAcctInfo import (
    getAccountWS,
    processAccountInfoResponse,
)
from cryptotrader.services.binance.websockets.accountRequests.getOrderRateLimits import (
    getOrderRateLimitsWS,
    processOrderRateLimitsResponse,
)
from cryptotrader.services.binance.websockets.accountRequests.acctOrderHistory import (
    getOrderHistoryWS,
    process_order_history_response,
)
from cryptotrader.services.binance.websockets.trading_requests.acct_oco_history import (
    get_oco_history,
    process_oco_history_response,
)
from cryptotrader.services.binance.websockets.accountRequests.acctTradeHistory import (
    getTradeHistoryWS,
    processTradeHistoryResponse,
)
from cryptotrader.services.binance.websockets.accountRequests.acctPreventedMatches import (
    getPreventedMatchesWS,
    processPreventedMatchesResponse,
)

# Import user data stream request operations
from cryptotrader.services.binance.websockets.userDataStreamRequests.startUserDataStream import (
    startUserDataStream,
    processStartUserDataStreamResponse,
)
from cryptotrader.services.binance.websockets.userDataStreamRequests.pingUserDataStream import (
    pingUserDataStream,
    processPingUserDataStream,
)
from cryptotrader.services.binance.websockets.userDataStreamRequests.stopUserDataStream import (
    stopUserDataStream,
    processStopUserDataStreamResponse,
)

# Import stream management classes
from cryptotrader.services.binance.websockets.streams.websocket_stream_manager import (
    BinanceStreamManager,
    createMarketStream,
)
from cryptotrader.services.binance.websockets.streams.user_data_stream import (
    UserDataStream,
)

__all__ = [
    # Base operations
    "BinanceWebSocketConnection",
    "SecurityType",
    # Market data requests
    "get_order_book_ws",
    "process_order_book_response",
    "get_recent_trades_ws",
    "process_recent_trades_response",
    "get_historical_trades_ws",
    "process_historical_trades_response",
    "get_klines_ws",
    "process_klines_response",
    "get_aggregate_trades_ws",
    "process_aggregate_trades_response",
    "get_price_ticker",
    "process_price_ticker_response",
    "get_book_ticker",
    "process_book_ticker_response",
    "get_24h_ticker",
    "process_24h_ticker_response",
    "getRollingWindowStatsWS",
    "process_rolling_window_response",
    "getAvgPriceWS",
    "process_avg_price_response",
    # Trading requests
    "place_new_order",
    "process_place_order_response",
    "testNewOrderWS",
    "process_test_order_response",
    "replace_order",
    "process_replace_order_response",
    "query_order",
    "process_query_order_response",
    "get_current_open_orders",
    "process_open_orders_response",
    "cancelOrderWS",
    "process_cancel_order_response",
    "cancel_open_orders",
    "process_cancel_open_orders_response",
    "create_new_oco_order",
    "process_create_oco_order_response",
    "getOcoOrderWS",
    "process_get_oco_order_response",
    "getOpenOcoOrdersWS",
    "process_open_oco_orders_response",
    "cancel_oco_order",
    "process_cancel_oco_order_response",
    # Account requests
    "getAccountWS",
    "processAccountInfoResponse",
    "getOrderRateLimitsWS",
    "processOrderRateLimitsResponse",
    "getOrderHistoryWS",
    "process_order_history_response",
    "get_oco_history",
    "process_oco_history_response",
    "getTradeHistoryWS",
    "processTradeHistoryResponse",
    "getPreventedMatchesWS",
    "processPreventedMatchesResponse",
    # User data stream requests
    "startUserDataStream",
    "processStartUserDataStreamResponse",
    "pingUserDataStream",
    "process_pingUserDataStreamResponse",
    "stopUserDataStream",
    "processStopUserDataStreamResponse",
    # Stream management
    "BinanceStreamManager",
    "createMarketStream",
    "UserDataStream",
]
