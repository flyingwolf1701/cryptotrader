```
cryptotrader/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── log_config.py
│   └── secrets.py
├── gui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chart_widget.py
│   │   ├── demos/
│   │   │   ├── __init__.py
│   │   │   ├── demo_logging_widget.py
│   │   │   ├── demo_strategy_widget.py
│   │   │   ├── demo_trade_history.py
│   │   │   ├── trade_history_demo.py
│   │   │   └── watchlist_demo.py
│   │   ├── logging_componenet.py
│   │   ├── logic/
│   │   │   ├── __init__.py
│   │   │   ├── logging_logic.py
│   │   │   ├── strategy_logic.py
│   │   │   ├── trade_history_logic.py
│   │   │   └── watchlist_logic.py
│   │   ├── search_symbol.py
│   │   ├── strategy_component.py
│   │   ├── styles.py
│   │   ├── trades_component.py
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── logging_widget.py
│   │       ├── strategy_widget.py
│   │       ├── trade_history_widget.py
│   │       └── watchlist_widget.py
│   ├── layouts/
│   │   ├── __init__.py
│   │   ├── charts_layout.py
│   │   └── overview_layout.py
│   └── main_layout.py
├── main.py
└── services/
    ├── __init__.py
    ├── binance/
    │   ├── __init__.py
    │   ├── binance_file_graph.md
    │   ├── binance_overview.yaml
    │   ├── instructions.md
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── _models_structure.yaml
    │   │   ├── base_models.py
    │   │   ├── market_models.py
    │   │   ├── order_models.py
    │   │   ├── otc_models.py
    │   │   ├── staking_models.py
    │   │   ├── user_models.py
    │   │   └── wallet_models.py
    │   ├── restAPI/
    │   │   ├── __init__.py
    │   │   ├── _restAPI_design_doc.md
    │   │   ├── baseOperations.py
    │   │   ├── diagnostic_scripts/
    │   │   │   ├── __init__.py
    │   │   │   ├── binance_websocket_diagnostic.py
    │   │   │   ├── market_diagnostic.py
    │   │   │   ├── order_diagnostic.py
    │   │   │   ├── otc_diagnostic.py
    │   │   │   ├── staking_diagnostic.py
    │   │   │   ├── subaccount_diagnostic.py
    │   │   │   ├── system_diagnostic.py
    │   │   │   ├── user_diagnostic.py
    │   │   │   └── wallet_diagnosis.py
    │   │   ├── marketApi.py
    │   │   ├── orderApi.py
    │   │   ├── otcApi.py
    │   │   ├── stakingApi.py
    │   │   ├── subaccountApi.py
    │   │   ├── systemApi.py
    │   │   ├── userApi.py
    │   │   └── walletApi.py
    │   └── websockets/
    │       ├── __init__.py
    │       ├── accountRequests/
    │       │   ├── __init__.py
    │       │   ├── _account_requests_structure.yaml
    │       │   ├── acctOrderHistory.py
    │       │   ├── acctPreventedMatches.py
    │       │   ├── acctTradeHistory.py
    │       │   ├── getOrderRateLimits.py
    │       │   └── getUserAcctInfo.py
    │       ├── baseOperations.py
    │       ├── diagnostic_scripts/
    │       │   ├── __init__.py
    │       │   ├── account_diagnostics/
    │       │   │   └── __init__.py
    │       │   ├── market_diagnostics/
    │       │   │   ├── __init__.py
    │       │   │   ├── aggregate_trades_diagnostic.py
    │       │   │   ├── current_average_price.py
    │       │   │   ├── historical_trades_diagnostic.py
    │       │   │   ├── klines_diagnostic.py
    │       │   │   ├── order_book_diagnostic.py
    │       │   │   ├── recent_trades_diagnostic.py
    │       │   │   ├── rolling_window_price.py
    │       │   │   ├── symbol_order_book_ticker.py
    │       │   │   ├── symbol_price_ticker.py
    │       │   │   └── ticker_price_24h.py
    │       │   ├── trade_diagnostics/
    │       │   │   └── __init__.py
    │       │   └── user_stream_diagnostics/
    │       │       └── __init__.py
    │       ├── market_data_requests/
    │       │   ├── __init__.py
    │       │   ├── _market_data_structure.yaml
    │       │   ├── aggregate_trades.py
    │       │   ├── current_average_price.py
    │       │   ├── historical_trades.py
    │       │   ├── klines.py
    │       │   ├── order_book.py
    │       │   ├── recent_trades.py
    │       │   ├── rolling_window_price.py
    │       │   ├── symbol_order_book_ticker.py
    │       │   ├── symbol_price_ticker.py
    │       │   └── ticker_price_24h.py
    │       ├── streams/
    │       │   ├── __init__.py
    │       │   ├── streams_structure.yaml
    │       │   ├── user_data_stream.py
    │       │   └── websocket_stream_manager.py
    │       ├── trading_requests/
    │       │   ├── __init__.py
    │       │   ├── acct_oco_history.py
    │       │   ├── cancel_oco_order.py
    │       │   ├── cancel_open_orders.py
    │       │   ├── cancel_order.py
    │       │   ├── create_new_oco_order.py
    │       │   ├── current_open_orders.py
    │       │   ├── get_oco_order.py
    │       │   ├── get_open_oco_orders.py
    │       │   ├── place_new_order.py
    │       │   ├── query_order.py
    │       │   ├── replace_order.py
    │       │   ├── test_new_order.py
    │       │   └── trading_requests_structure.yaml
    │       ├── userDataStreamRequests/
    │       │   ├── __init__.py
    │       │   ├── pingUserDataStream.py
    │       │   ├── startUserDataStream.py
    │       │   ├── stopUserDataStream.py
    │       │   └── user_data_stream_structure.yaml
    │       ├── wsDesignDoc.md
    │       └── wsStructureDoc.yaml
    └── unified_clients/
        ├── __init__.py
        ├── binanceRestUnifiedClient.py
        └── bUnifiedDiagnostic.py
```