# File: src/gui/main_layout.py
"""
Main Application Layout

Organizes different tabs: Watchlist, Trading, Trade History.
"""

import tkinter as tk
from tkinter import ttk

from config import get_logger
from src.gui.components.ui.watchlist_widget import WatchlistWidget
from src.gui.components.ui.trade_history_widget import TradeHistoryWidget

logger = get_logger(__name__)


class MainLayout(ttk.Notebook):
    """Main layout organizing different functional tabs."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        self.parent = parent
        self._init_tabs()
        self._init_layouts()

    def _init_tabs(self):
        """Initialize tabs."""
        self.watchlist_tab = ttk.Frame(self)
        self.trading_tab = ttk.Frame(self)
        self.trade_history_tab = ttk.Frame(self)

        self.add(self.watchlist_tab, text="Watchlist")
        self.add(self.trading_tab, text="Trading")
        self.add(self.trade_history_tab, text="Trade History")

    def _init_layouts(self):
        """Initialize layouts inside each tab."""
        self._setup_watchlist_tab()
        self._setup_trading_tab()
        self._setup_trade_history_tab()

    def _setup_watchlist_tab(self):
        """Set up the Watchlist tab."""
        self.watchlist_widget = WatchlistWidget(self.watchlist_tab)
        self.watchlist_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _setup_trading_tab(self):
        """Set up the Trading tab (placeholder for now)."""
        label = ttk.Label(self.trading_tab, text="Trading functionality coming soon.")
        label.pack(padx=20, pady=20)

    def _setup_trade_history_tab(self):
        """Set up the Trade History tab."""
        self.trade_history_widget = TradeHistoryWidget(self.trade_history_tab)
        self.trade_history_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
