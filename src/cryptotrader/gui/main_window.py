"""
CryptoTrader Main Window

This module implements the main application window and coordinates
between different UI components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any

from src.cryptotrader.config import get_logger
from src.cryptotrader.services.binance.restAPI import MarketOperations, SystemOperations

# Import components
from src.cryptotrader.gui.components.watchlist import WatchlistWidget
from src.cryptotrader.gui.components.logging_panel import LoggingPanel
from src.cryptotrader.gui.components.strategy_panel import StrategyPanel
from src.cryptotrader.gui.components.trade_history import TradeHistoryWidget
from src.cryptotrader.gui.components.chart_widget import ChartWidget
from src.cryptotrader.gui.components.styles import Colors, apply_theme

logger = get_logger(__name__)

class MainWindow(tk.Tk):
    """Main application window for the CryptoTrader dashboard."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("CryptoTrader Dashboard")
        self.geometry("1280x800")
        
        # Apply custom theme
        self.fonts = apply_theme(self)
        
        # Initialize API clients
        self.market_client = MarketOperations()
        self.system_client = SystemOperations()
        
        # Create UI elements
        self.setup_ui()
        
        # Setup update timer for live data
        self.after(1500, self._update_ui)
        
        # Load initial data
        self.load_initial_data()
        
        logger.info("CryptoTrader Dashboard initialized")
    
    def setup_ui(self) -> None:
        """Set up the user interface components with a cleaner layout."""
        # Configure root window
        self.configure(bg=Colors.BACKGROUND)
        
        # Create left and right frames directly (like in the example)
        self._left_frame = ttk.Frame(self)
        self._left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self._right_frame = ttk.Frame(self)
        self._right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side components - stacked vertically
        self.watchlist = WatchlistWidget(self._left_frame, self.market_client)
        self.watchlist.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.logging_panel = LoggingPanel(self._left_frame)
        self.logging_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Right side components - stacked vertically
        self.strategy_panel = StrategyPanel(self._right_frame, self.market_client)
        self.strategy_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.trade_history = TradeHistoryWidget(self._right_frame)
        self.trade_history.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Wire up event handlers
        self.strategy_panel.log_callback = self.logging_panel.add_log
        self.watchlist.symbol_selected_callback = self.on_symbol_selected
        
        # Add mock trades for demo purposes
        self.trade_history.add_mock_trades()
    
    def on_symbol_selected(self, symbol):
        """Handle symbol selection from watchlist."""
        # Open chart in a new window
        self.open_chart_window(symbol)
    
    def open_chart_window(self, symbol):
        """Open a chart in a separate window."""
        chart_window = tk.Toplevel(self)
        chart_window.title(f"Chart: {symbol}")
        chart_window.geometry("800x600")
        chart_window.configure(bg=Colors.BACKGROUND)
        
        # Apply theme to the new window
        apply_theme(chart_window)
        
        # Create chart widget in the new window
        chart = ChartWidget(chart_window, self.market_client)
        chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Set the symbol
        chart.symbol_changed(symbol)
    
    def load_initial_data(self):
        """Load initial data for the dashboard components."""
        try:
            # Load exchange info and available symbols
            exchange_info = self.system_client.get_exchange_info()
            
            if exchange_info and 'symbols' in exchange_info:
                symbols = [symbol['symbol'] for symbol in exchange_info['symbols']
                          if symbol.get('status') == 'TRADING']
                
                if symbols:
                    # Set available symbols in components
                    self.watchlist.set_available_symbols(symbols)
                    self.strategy_panel.set_available_symbols(symbols)
                    
                    # Add default symbols to watchlist
                    default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                    for symbol in default_symbols:
                        if symbol in symbols:
                            self.watchlist.add_symbol(symbol)
                    
                    logger.info(f"Loaded {len(symbols)} trading symbols")
                    return
            
            # Fallback to default symbols
            default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
            self.watchlist.set_available_symbols(default_symbols)
            self.strategy_panel.set_available_symbols(default_symbols)
            
            for symbol in default_symbols:
                self.watchlist.add_symbol(symbol)
                
        except Exception as e:
            logger.error(f"Error loading initial data: {str(e)}")
            # Add some default symbols anyway
            default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
            self.watchlist.set_available_symbols(default_symbols)
            self.strategy_panel.set_available_symbols(default_symbols)
            
            for symbol in default_symbols:
                self.watchlist.add_symbol(symbol)
    
    def _update_ui(self):
        """Centralized UI update method (like in the example)."""
        # Update watchlist prices
        try:
            self.watchlist.update_prices()
        except Exception as e:
            logger.error(f"Error updating watchlist: {str(e)}")
        
        # Schedule the next update
        self.after(1500, self._update_ui)