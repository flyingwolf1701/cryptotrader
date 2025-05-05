import tkinter as tk
from tkinter import ttk

from cryptotrader.config import get_logger
from cryptotrader.gui.components.ui.watchlist_widget import WatchlistWidget
from cryptotrader.gui.components.ui.strategy_widget import StrategyWidget
from cryptotrader.gui.components.ui.logging_widget import LoggingWidget
from cryptotrader.gui.components.ui.trade_history_widget import TradeHistoryWidget

# Initialize logger
logger = get_logger(__name__)

class OverviewLayout(ttk.Frame):
    """Grid layout for Overview tab: 2x2 panels with 40/60 width split."""

    def __init__(self, parent, fonts: dict):
        super().__init__(parent)
        self.fonts = fonts
        self._init_grid()
        self._create_panels()

    def _init_grid(self):
        # Two columns: left 40%, right 60%
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        # Two equal-height rows
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _create_panels(self):
        # Watchlist panel (top-left)
        self.watchlist_panel = ttk.LabelFrame(self, text="Watchlist", padding=10)
        self.watchlist_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        WatchlistWidget(self.watchlist_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Watchlist panel initialized")

        # Strategy panel (top-right)
        self.strategy_panel = ttk.LabelFrame(self, text="Strategy", padding=10)
        self.strategy_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        StrategyWidget(self.strategy_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Strategy panel initialized")

        # Logging panel (bottom-left)
        self.logging_panel = ttk.LabelFrame(self, text="Logging", padding=10)
        self.logging_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        LoggingWidget(self.logging_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Logging panel initialized")

        # Trade History panel (bottom-right)
        self.trade_history_panel = ttk.LabelFrame(self, text="Trade History", padding=10)
        self.trade_history_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        TradeHistoryWidget(self.trade_history_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Trade History panel initialized")
