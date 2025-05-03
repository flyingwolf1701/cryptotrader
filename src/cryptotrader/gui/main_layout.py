#!/usr/bin/env python3
"""
Main layout for the CryptoTrader application with complete tab structure.
"""

import tkinter as tk
from tkinter import ttk

from cryptotrader.config import get_logger
from cryptotrader.gui.components.styles import apply_theme
from cryptotrader.gui.layouts.overview_layout import OverviewLayout
from cryptotrader.gui.components.ui.watchlist_widget import WatchlistWidget

# Initialize logger for this module
logger = get_logger(__name__)

class MainLayout(tk.Tk):
    """Main window for the application with all required tabs."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("CryptoTrader Dashboard")
        self.geometry("1024x768")

        # Apply theme
        self.fonts = apply_theme(self)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define tabs
        tabs = [
            ("Overview", ttk.Frame(self.notebook)),
            ("Watchlist", ttk.Frame(self.notebook)),
            ("Market View", ttk.Frame(self.notebook)),
            ("Trading View", ttk.Frame(self.notebook)),
            ("Logging", ttk.Frame(self.notebook)),
            ("Strategy", ttk.Frame(self.notebook)),
            ("Charts", ttk.Frame(self.notebook)),
            ("Settings", ttk.Frame(self.notebook)),
        ]
        for name, frame in tabs:
            setattr(self, f"{name.lower().replace(' ', '_')}_tab", frame)
            self.notebook.add(frame, text=name)

        # Populate tabs
        self._setup_overview_tab()
        self._setup_watchlist_tab()
        for name in ["Market View", "Trading View", "Logging", "Strategy", "Charts", "Settings"]:
            tab = getattr(self, f"{name.lower().replace(' ', '_')}_tab")
            self._setup_placeholder_tab(tab, name)

        logger.info("Main layout initialized with all tabs")

    def _setup_placeholder_tab(self, tab, title):
        """Add placeholder content for tabs not yet implemented."""
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        label = ttk.Label(frame, text=f"{title} Content Will Be Added Here", font=self.fonts.get("large"))
        label.pack(pady=50)
        ttk.Button(frame, text=f"{title} Action", command=lambda: logger.info(f"{title} button clicked")).pack(pady=10)

    def _setup_overview_tab(self):
        """Initialize the Overview tab with the grid overview layout."""
        tab = self.overview_tab
        layout = OverviewLayout(tab, self.fonts)
        layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Overview tab initialized with grid layout")

    def _setup_watchlist_tab(self):
        """Initialize the Watchlist tab with the watchlist widget."""
        tab = self.watchlist_tab
        widget = WatchlistWidget(tab)
        widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Watchlist tab initialized")


def main():
    """Application entry point."""
    logger.info("Starting CryptoTrader Dashboard")
    window = MainLayout()
    window.mainloop()

if __name__ == "__main__":
    main()
