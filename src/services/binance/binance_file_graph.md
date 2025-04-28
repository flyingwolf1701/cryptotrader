Complete Binance Service Package Structure
src/cryptotrader/services/binance/
├── **init**.py # Main package exports
│
├── models/ # Data models
│ ├── **init**.py # Exports all models
│ ├── base_models.py # Core models used across APIs
│ ├── order_models.py # Order-specific models
│ ├── market_models.py # Market data models
│ ├── user_models.py # User account models
│ ├── wallet_models.py # Wallet operation models
│ ├── otc_models.py # OTC trading models
│ ├── staking_models.py # Staking operation models
│ └── websocket_models.py # WebSocket-specific models
│
├── restAPI/ # REST API implementation
│ ├── **init**.py # Exports clients
│ ├── \_restAPI.yaml # API documentation in YAML format
│ ├── \_restAPI_design_doc.md # Design documentation for REST API
│ ├── base_operations.py # Core request functionality
│ ├── systemApi.py # System information operations
│ ├── market_api.py # Market data operations
│ ├── order_api.py # Order operations
│ ├── user_api.py # User account operations
│ ├── wallet_api.py # Wallet operations
│ ├── subaccount_api.py # Sub-account management
│ ├── otc_api.py # OTC trading operations
│ └── staking_api.py # Staking operations
│
├── websocketAPI/ # WebSocket API implementation
│ ├── **init**.py # Main package exports
│ ├── wsDesignDoc.md # Design documentation for WebSocket API
│ ├── wsStructureDoc.yaml # API structure documentation in YAML format
│ ├── base_operations.py # Core WebSocket functionality
│ │
│ ├── account_requests/ # Account data operations
│ │ ├── **init**.py # Package exports
│ │ ├── account_requests_structure.yaml # YAML documentation
│ │ ├── acct_oco_history.py # OCO order history requests
│ │ ├── acct_order_history.py # Order history requests
│ │ ├── acct_prevented_matches.py # Self-trade prevention matches
│ │ ├── acct_trade_history.py # Trade history requests
│ │ ├── get_order_rate_limits.py # Order rate limit requests
│ │ └── get_user_acct_info.py # Account information requests
│ │
│ ├── market_data_requests/ # Market data operations
│ │ ├── **init**.py # Package exports
│ │ ├── market_data_structure.yaml # YAML documentation
│ │ ├── aggregate_trades.py # Aggregate trade requests
│ │ ├── current_average_price.py # Average price requests
│ │ ├── historical_trades.py # Historical trade requests
│ │ ├── klines.py # Kline/candlestick requests
│ │ ├── order_book.py # Order book requests
│ │ ├── recent_trades.py # Recent trade requests
│ │ ├── rolling_window_price.py # Rolling window price stats
│ │ ├── symbol_order_book_ticker.py # Order book ticker requests
│ │ ├── symbol_price_ticker.py # Symbol price ticker requests
│ │ └── ticker_price_24h.py # 24h price statistics requests
│ │
│ ├── trading_requests/ # Trading operations
│ │ ├── **init**.py # Package exports
│ │ ├── trading_requests_structure.yaml # YAML documentation
│ │ ├── cancel_oco_order.py # Cancel OCO order requests
│ │ ├── cancel_open_orders.py # Cancel open orders requests
│ │ ├── cancelOrderRest.py # Cancel order requests
│ │ ├── create_new_oco_order.py # Create OCO order requests
│ │ ├── current_open_orders.py # Get open orders requests
│ │ ├── getOcoOrderRest.py # Get OCO order details
│ │ ├── getOpenOcoOrdersRest.py # Get open OCO orders requests
│ │ ├── place_new_order.py # Place order requests
│ │ ├── query_order.py # Query order details requests
│ │ ├── replace_order.py # Replace order requests
│ │ └── testNewOrderRest.py # Test order placement requests
│ │
│ ├── user_data_stream_requests/ # User data stream operations
│ │ ├── **init**.py # Package exports
│ │ ├── user_data_stream_structure.yaml # YAML documentation
│ │ ├── ping_user_data_stream.py # Ping user data stream requests
│ │ ├── start_user_data_stream.py # Start user data stream requests
│ │ └── stop_user_data_stream.py # Stop user data stream requests
│ │
│ └── streams/ # Real-time data streams
│ ├── **init**.py # Package exports
│ ├── streams_structure.yaml # YAML documentation
│ ├── websocket_stream_manager.py # Stream connection management
│ ├── user_data_stream.py # User data stream handler
│ ├── market_stream.py # Market data stream handler
│ ├── stream_parser.py # Stream data parsing utilities
│ └── stream_buffer.py # Buffer for stream data
│
├── diagnostic_scripts/ # Diagnostic/testing scripts
│ ├── rest_diagnostics/ # REST API diagnostics
│ │ ├── system_diagnostic.py # Tests system API functionality
│ │ ├── market_diagnostic.py # Tests market API functionality
│ │ ├── order_diagnostic.py # Tests order API functionality
│ │ ├── user_diagnostic.py # Tests user API functionality
│ │ ├── wallet_diagnostic.py # Tests wallet API functionality
│ │ ├── subaccount_diagnostic.py # Tests sub-account functionality
│ │ ├── otc_diagnostic.py # Tests OTC API functionality
│ │ └── staking_diagnostic.py # Tests staking functionality
│ │
│ └── websocket_diagnostics/ # WebSocket API diagnostics
│ ├── account_diagnostics/ # Account request tests
│ │ ├── acct_order_history_diagnostic.py
│ │ ├── acct_oco_history_diagnostic.py
│ │ └── acct_trade_history_diagnostic.py
│ │
│ ├── market_diagnostics/ # Market data request tests
│ │ ├── order_book_diagnostic.py
│ │ ├── klines_diagnostic.py
│ │ ├── ticker_diagnostic.py
│ │ ├── trades_diagnostic.py
│ │ └── price_ticker_diagnostic.py
│ │
│ ├── trading_diagnostics/ # Trading request tests
│ │ ├── order_placement_diagnostic.py
│ │ ├── order_cancel_diagnostic.py
│ │ └── oco_order_diagnostic.py
│ │
│ ├── user_stream_diagnostics/ # User stream tests
│ │ └── user_data_stream_diagnostic.py
│ │
│ └── stream_diagnostics/ # Stream handling tests
│ ├── market_stream_diagnostic.py
│ └── stream_manager_diagnostic.py
│
└── client.py # High-level client combining REST and WebSocket functionality
