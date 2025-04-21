"""
CryptoTrader GUI Components

This package contains UI components used in the CryptoTrader application.
"""

from src.cryptotrader.qtGui.components.watchlist import WatchlistWidget
from src.cryptotrader.qtGui.components.chart_widget import ChartWidget
from src.cryptotrader.qtGui.components.logging_panel import LoggingPanel
from src.cryptotrader.qtGui.components.strategy_panel import StrategyPanel
from src.cryptotrader.qtGui.components.trade_history import TradeHistoryWidget
from src.cryptotrader.qtGui.components.styles import apply_dark_theme, Colors, Fonts

__all__ = [
    'WatchlistWidget',
    'ChartWidget',
    'LoggingPanel',
    'StrategyPanel',
    'TradeHistoryWidget',
    'apply_dark_theme',
    'Colors',
    'Fonts'
]