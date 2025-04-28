```
src/
├── README.md
├── __init__.py
├── _cryptotrader_app_structure.yaml
├── directory_structure.md
├── gui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── chart_widget.py
│   │   ├── demos/
│   │   │   ├── __init__.py
│   │   │   ├── symbol_search_demo.py
│   │   │   ├── trade_history_demo.py
│   │   │   └── watchlist_demo.py
│   │   ├── logging_componenet.py
│   │   ├── logic/
│   │   │   ├── __init__.py
│   │   │   ├── strategy_logic.py
│   │   │   ├── symbol_search_logic.py
│   │   │   ├── trade_history_logic.py
│   │   │   └── watchlist_logic.py
│   │   ├── search_symbol.py
│   │   ├── strategy_component.py
│   │   ├── styles.py
│   │   ├── trades_component.py
│   │   ├── ui/
│   │   │   ├── __init__.py
│   │   │   ├── symbol_search_widget.py
│   │   │   ├── trade_history_widget.py
│   │   │   └── watchlist_widget.py
│   │   └── watchlist_component.py
│   ├── layouts/
│   │   ├── __init__.py
│   │   ├── charts_layout.py
│   │   └── overview_layout.py
│   ├── main_layout.py
│   └── unified_clients/
│       ├── __init__.py
│       ├── bUnifiedDiagnostic.py
│       └── binanceRestUnifiedClient.py
├── main.py
├── notes/
│   ├── brainstorms/
│   │   ├── coin_gecko_notes.md
│   │   └── profit_distribution_ideas.md
│   ├── project_plan/
│   │   ├── epics/
│   │   │   ├── 1_not_yet_started_epics/
│   │   │   ├── 2_in_progress_epics/
│   │   │   │   └── wallet_dashboard_epic.yaml
│   │   │   └── 3_completed_epics/
│   │   ├── pm_instructions.md
│   │   └── project_roadmap.yaml
│   └── prompts/
│       └── api_yaml_prompt.md
├── scripts/
└── services/
    ├── binance/
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
    │   │   ├── _restAPI.yaml
    │   │   ├── _restAPI_design_doc.md
    │   │   ├── base_operations.py
    │   │   ├── diagnostic_scripts/
    │   │   │   ├── binance_websocket_diagnostic.py
    │   │   │   ├── market_diagnostic.py
    │   │   │   ├── order_diagnostic.py
    │   │   │   ├── otc_diagnostic.py
    │   │   │   ├── staking_diagnostic.py
    │   │   │   ├── subaccount_diagnostic.py
    │   │   │   ├── system_diagnostic.py
    │   │   │   ├── user_diagnostic.py
    │   │   │   └── wallet_diagnosis.py
    │   │   ├── market_api.py
    │   │   ├── order_api.py
    │   │   ├── otc_api.py
    │   │   ├── staking_api.py
    │   │   ├── subaccount_api.py
    │   │   ├── systemApi.py
    │   │   ├── user_api.py
    │   │   └── wallet_api.py
    │   └── websockets/
    │       ├── __init__.py
    │       ├── account_requests/
    │       │   ├── __init__.py
    │       │   ├── _account_requests_structure.yaml
    │       │   ├── acct_order_history.py
    │       │   ├── acct_prevented_matches.py
    │       │   ├── acct_trade_history.py
    │       │   ├── get_order_rate_limits.py
    │       │   └── get_user_acct_info.py
    │       ├── base_operations.py
    │       ├── diagnostic_scripts/
    │       │   ├── account_diagnostics/
    │       │   ├── market_diagnostics/
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
    │       │   └── user_stream_diagnostics/
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
    │       │   ├── cancelOrderRest.py
    │       │   ├── create_new_oco_order.py
    │       │   ├── current_open_orders.py
    │       │   ├── getOcoOrderRest.py
    │       │   ├── getOpenOcoOrdersRest.py
    │       │   ├── place_new_order.py
    │       │   ├── query_order.py
    │       │   ├── replace_order.py
    │       │   ├── testNewOrderRest.py
    │       │   └── trading_requests_structure.yaml
    │       ├── user_data_stream_requests/
    │       │   ├── __init__.py
    │       │   ├── ping_user_data_stream.py
    │       │   ├── start_user_data_stream.py
    │       │   ├── stop_user_data_stream.py
    │       │   └── user_data_stream_structure.yaml
    │       ├── wsDesignDoc.md
    │       └── wsStructureDoc.yaml
    └── symbol_service.py
```
