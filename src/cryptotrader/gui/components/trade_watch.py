"""
CryptoTrader GUI Components

This package contains UI components used in the CryptoTrader application.
"""

from src.cryptotrader.gui.components.watchlist import WatchlistWidget
from src.cryptotrader.gui.components.chart_widget import ChartWidget
from src.cryptotrader.gui.components.logging_panel import LoggingPanel
from src.cryptotrader.gui.components.strategy_panel import StrategyPanel, StrategyParametersDialog
from src.cryptotrader.gui.components.trades_watch import TradesWatch
from src.cryptotrader.gui.components.styles import Colors, Fonts, apply_theme, create_table, create_button

__all__ = [
    'WatchlistWidget',
    'ChartWidget',
    'LoggingPanel',
    'StrategyPanel',
    'StrategyParametersDialog',
    'TradesWatch',
    'Colors',
    'Fonts',
    'apply_theme',
    'create_table',
    'create_button'
]