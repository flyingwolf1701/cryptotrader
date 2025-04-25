"""
Charts Layout for CryptoTrader

This module provides a layout for the Charts View tab.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.config import get_logger
from src.services.binance.restAPI import MarketOperations
from src.gui.components.chart_widget import ChartWidget
from src.gui.components.watchlist import WatchlistWidget

logger = get_logger(__name__)

class ChartsLayout(ttk.Frame):
    """Layout for the Charts View tab."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Initialize API clients
        self.market_client = MarketOperations()
        
        # Create UI elements
        self.setup_ui()
        
        # Current selected symbol
        self.current_symbol = "BTCUSDT"
        
        logger.info("Charts layout initialized")
    
    def setup_ui(self):
        """Set up the user interface components for chart viewing."""
        # Configure grid
        self.columnconfigure(0, weight=1)  # Left column (watchlist)
        self.columnconfigure(1, weight=3)  # Right column (charts)
        self.rowconfigure(0, weight=1)     # Single row
        
        # Left side: Compact watchlist
        self.watchlist_frame = ttk.LabelFrame(self, text="Symbols")
        self.watchlist_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.watchlist = WatchlistWidget(self.watchlist_frame, self.market_client)
        self.watchlist.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right side: Chart area with controls
        self.chart_frame = ttk.LabelFrame(self, text="Market Chart")
        self.chart_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # Timeframe selector at the top
        self.controls_frame = ttk.Frame(self.chart_frame)
        self.controls_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.controls_frame, text="Timeframe:").pack(side=tk.LEFT, padx=5)
        
        self.timeframe_var = tk.StringVar(value="1h")
        self.timeframe_combo = ttk.Combobox(
            self.controls_frame,
            textvariable=self.timeframe_var,
            values=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            width=5
        )
        self.timeframe_combo.pack(side=tk.LEFT, padx=5)
        self.timeframe_combo.bind("<<ComboboxSelected>>", self.on_timeframe_changed)
        
        # Refresh button
        self.refresh_btn = ttk.Button(
            self.controls_frame, 
            text="Refresh", 
            command=self.refresh_chart
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Chart widget
        self.chart = ChartWidget(self.chart_frame, self.market_client)
        self.chart.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Wire up components
        self.watchlist.symbol_selected_callback = self.on_symbol_selected
        
        # Load initial symbols
        self.load_initial_symbols()
    
    def load_initial_symbols(self):
        """Load initial symbols for the watchlist."""
        default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT"]
        self.watchlist.set_available_symbols(default_symbols)
        
        # Add default symbols to watchlist
        for symbol in default_symbols:
            self.watchlist.add_symbol(symbol)
    
    def on_symbol_selected(self, symbol):
        """Handle symbol selection from watchlist."""
        self.current_symbol = symbol
        self.chart.symbol_changed(symbol)
        logger.info(f"Selected {symbol} in charts view")
    
    def on_timeframe_changed(self, event):
        """Handle timeframe change event."""
        timeframe = self.timeframe_var.get()
        self.chart.timeframe_changed(timeframe)
        logger.info(f"Changed timeframe to {timeframe}")
    
    def refresh_chart(self):
        """Refresh the current chart."""
        self.chart.refresh_chart()
        logger.info(f"Refreshed chart for {self.current_symbol}")
    
    def update_components(self):
        """Update all components in the layout."""
        try:
            # Update watchlist prices
            self.watchlist.update_prices()
        except Exception as e:
            logger.error(f"Error updating watchlist in charts view: {str(e)}")