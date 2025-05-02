"""
Overview Layout Component

This module implements a simple grid layout with four panels
for the Overview tab of the CryptoTrader dashboard.
"""

import tkinter as tk
from tkinter import ttk
import logging

from config import get_logger  # Use when integrating with the main app
from gui.components.watchlist_component import WatchlistWidget

# Configure basic logging (use this for standalone testing)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)  # Use this for standalone testing

# Uncomment when integrating with the main app
# logger = get_logger(__name__)


class OverviewLayout(ttk.Frame):
    """A grid layout with four panels for the Overview tab."""

    def __init__(self, parent, fonts):
        super().__init__(parent)
        self.fonts = fonts
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Configure grid layout for the frame
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create four panels
        self.watchlist_panel = self._create_watchlist_panel(0, 0, "Watchlist Panel")
        self.strategy_panel = self._create_panel(0, 1, "Strategy Panel")
        self.logging_panel = self._create_panel(1, 0, "Logging Panel")
        self.trading_panel = self._create_panel(1, 1, "Trading Panel")

        logger.info("Overview layout initialized with four panels")

    # Place holder for panels
    def _create_panel(self, row, column, title):
        """Create a panel with a title and placeholder content."""
        # Create a frame with a border
        panel = ttk.LabelFrame(self, text=title, padding=10)
        panel.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        # Add a placeholder label
        label = ttk.Label(panel, text=f"Content for {title}")
        label.pack(pady=40, padx=40)

        return panel

    def _create_watchlist_panel(self, row, column, title):
        """Create the watchlist panel with the WatchlistWidget."""
        # Create a frame with a border
        panel = ttk.LabelFrame(self, text=title, padding=10)
        panel.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        # Add the watchlist widget (no market_client needed anymore)
        self.watchlist = WatchlistWidget(panel)
        self.watchlist.pack(fill=tk.BOTH, expand=True)

        # Set available symbols
        available_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        self.watchlist.set_available_symbols(available_symbols)

        return panel


# For testing this component individually
def main():
    root = tk.Tk()
    root.title("Overview Layout Test")
    root.geometry("800x600")

    # Set a dark theme for testing
    root.configure(bg="#1e1e1e")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TLabelframe", background="#1e1e1e", foreground="#d4d4d4")
    style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#d4d4d4")
    style.configure("TLabel", background="#1e1e1e", foreground="#d4d4d4")

    # Create and pack the overview layout
    overview = OverviewLayout(root)
    overview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
