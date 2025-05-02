"""
CryptoTrader Application with Complete Tab Structure

This module initializes the application with all tabs requested,
applying the dark theme styling from the styles component.
"""

import tkinter as tk
from tkinter import ttk

# Import centralized configuration and styling
from config import get_logger
from cryptotrader.gui.components.styles import Colors, apply_theme
from cryptotrader.gui.layouts.overview_layout import OverviewLayout
from cryptotrader.gui.components.watchlist_component import WatchlistWidget

# Set up logging through the centralized system
logger = get_logger(__name__)


class MainLayout(tk.Tk):
    """Main window for the application with all required tabs."""

    def __init__(self):
        super().__init__()

        # Setup window
        self.title("CryptoTrader Dashboard")
        self.geometry("1024x768")

        # Apply custom theme using the existing styling module
        self.fonts = apply_theme(self)

        # Create main container with notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs for different views in the specified order
        self.overview_tab = ttk.Frame(self.notebook)
        self.watchlist_tab = ttk.Frame(self.notebook)
        self.market_tab = ttk.Frame(self.notebook)
        self.trading_tab = ttk.Frame(self.notebook)
        self.logging_tab = ttk.Frame(self.notebook)
        self.strategy_tab = ttk.Frame(self.notebook)
        self.charts_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)

        # Add tabs to notebook in the specified order
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.watchlist_tab, text="Watchlist")
        self.notebook.add(self.market_tab, text="Market View")
        self.notebook.add(self.trading_tab, text="Trading View")
        self.notebook.add(self.logging_tab, text="Logging")
        self.notebook.add(self.strategy_tab, text="Strategy")
        self.notebook.add(self.charts_tab, text="Charts")
        self.notebook.add(self.settings_tab, text="Settings")

        # Add content to each tab
        self._setup_overview_tab()
        self._setup_watchlist_tab()
        self._setup_placeholder_tab(self.market_tab, "Market View")
        self._setup_placeholder_tab(self.trading_tab, "Trading View")
        self._setup_placeholder_tab(self.logging_tab, "Logging")
        self._setup_placeholder_tab(self.strategy_tab, "Strategy")
        self._setup_placeholder_tab(self.charts_tab, "Charts")
        self._setup_placeholder_tab(self.settings_tab, "Settings")

        logger.info("Main layout initialized with all tabs")

    def _setup_placeholder_tab(self, tab, tab_name):
        """Helper method to set up basic content for a tab."""
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(
            frame,
            text=f"{tab_name} Content Will Be Added Here",
            font=self.fonts["large"],
        )
        label.pack(pady=50)

        button = ttk.Button(
            frame,
            text=f"{tab_name} Action",
            command=lambda: logger.info(f"{tab_name} button clicked"),
        )
        button.pack(pady=10)

        logger.info(f"{tab_name} tab initialized with placeholder")

    def _setup_overview_tab(self):
        """Set up the Overview tab with the OverviewLayout."""
        # Create the overview layout and pack it to fill the tab
        self.overview_layout = OverviewLayout(self.overview_tab, self.fonts)
        self.overview_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Overview tab initialized with grid layout")

    def _setup_watchlist_tab(self):
        """Set up the Watchlist tab with the WatchlistWidget."""
        # Create and configure the watchlist widget
        self.watchlist_widget = WatchlistWidget(self.watchlist_tab)
        self.watchlist_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Set available symbols
        available_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT"]
        self.watchlist_widget.set_available_symbols(available_symbols)

        logger.info("Watchlist tab initialized")
    
    def _setup_trading_tab(self):
        """Set up the Trading tab (placeholder)."""
        # TODO: Hook TradingWidget here when ready
        label = ttk.Label(self.trading_tab, text="Trading functionality coming soon.")
        label.pack(padx=20, pady=20)

    def _setup_trade_history_tab(self):
        """Set up the Trade History tab."""
        from cryptotrader.gui.components.ui.trade_history_widget import TradeHistoryWidget

        self.trade_history_widget = TradeHistoryWidget(self.trade_history_tab)
        self.trade_history_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


def main():
    """Application entry point."""
    # Log application startup
    logger.info("Starting CryptoTrader Dashboard")

    # Create and show the main window
    window = MainLayout()

    # Start the event loop
    window.mainloop()


if __name__ == "__main__":
    main()
