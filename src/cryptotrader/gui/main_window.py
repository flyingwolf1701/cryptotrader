"""
CryptoTrader Main Window

This module implements the main application window and coordinates
between different UI components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Union, cast

# Import with relative imports to work within the project structure
from src.cryptotrader.config import get_logger
from src.cryptotrader.services.binance.restAPI import MarketOperations, SystemOperations

# Import components
from src.cryptotrader.gui.components.watchlist import WatchlistWidget
from src.cryptotrader.gui.components.chart_widget import ChartWidget
from src.cryptotrader.gui.components.logging_panel import LoggingPanel
from src.cryptotrader.gui.components.strategy_panel import StrategyPanel
from src.cryptotrader.gui.components.trade_history import TradeHistoryWidget
from src.cryptotrader.gui.components.styles import apply_theme

logger = get_logger(__name__)

class MainWindow(tk.Tk):
    """Main application window for the CryptoTrader dashboard."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("CryptoTrader Dashboard")
        self.geometry("1280x800")
        
        # Apply custom theme
        apply_theme(self)
        
        # Initialize API clients
        self.market_client: MarketOperations = MarketOperations()
        self.system_client: SystemOperations = SystemOperations()
        
        # Create UI elements
        self.setup_ui()
        
        # Setup update timer for live data
        self.after(1500, self.update_data)  # Update every 1.5 seconds
        
        # Load initial data
        self.load_initial_data()
        
        logger.info("CryptoTrader Dashboard initialized")
    
    def setup_ui(self) -> None:
        """Set up the user interface components."""
        # Create main splitter (PanedWindow in Tkinter)
        self.main_splitter = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_splitter.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create left side widget (chart and watchlist)
        self.left_frame = ttk.Frame(self.main_splitter)
        
        # Create right side with tabs
        self.right_frame = ttk.Frame(self.main_splitter)
        
        # Add frames to the PanedWindow
        self.main_splitter.add(self.left_frame, weight=60)
        self.main_splitter.add(self.right_frame, weight=40)
        
        # Create tab widget for trading components
        self.tabs = ttk.Notebook(self.right_frame)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        
        # Create and add components
        self.init_components()
    
    def init_components(self) -> None:
        """Initialize dashboard components and add them to the layout."""
        # Create left side components
        self.chart_widget = ChartWidget(self.left_frame, self.market_client)
        self.chart_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the watchlist with fixed height
        watchlist_frame = ttk.Frame(self.left_frame, height=200)
        watchlist_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5, side=tk.BOTTOM)
        watchlist_frame.pack_propagate(False)  # Prevent the frame from shrinking
        
        self.watchlist = WatchlistWidget(watchlist_frame, self.market_client)
        self.watchlist.pack(fill=tk.BOTH, expand=True)
        
        # Create right side components (for tabs)
        self.strategy_panel = StrategyPanel(self.tabs, self.market_client)
        self.trade_history = TradeHistoryWidget(self.tabs)
        self.logging_panel = LoggingPanel(self.tabs)
        
        # Add tabs
        self.tabs.add(self.strategy_panel, text="Trading Strategies")
        self.tabs.add(self.trade_history, text="Trade History")
        self.tabs.add(self.logging_panel, text="Logs")
        
        # Connect signal handlers
        self.strategy_panel.log_callback = self.logging_panel.add_log
        self.watchlist.symbol_selected_callback = self.chart_widget.symbol_changed
        
        # Add mock trades for demo purposes
        self.trade_history.add_mock_trades()
    
    def load_initial_data(self):
        """Load initial data for the dashboard components."""
        try:
            # Load exchange info and available symbols
            exchange_info = self.system_client.get_exchange_info()
            if exchange_info:
                symbols = [symbol['symbol'] for symbol in exchange_info.get('symbols', [])
                          if symbol.get('status') == 'TRADING']
                
                if symbols:
                    # Set available symbols in components
                    self.watchlist.set_available_symbols(symbols)
                    self.strategy_panel.set_available_symbols(symbols)
                    self.chart_widget.set_available_symbols(symbols)
                    
                    # Add default symbols to watchlist
                    default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                    for symbol in default_symbols:
                        if symbol in symbols:
                            self.watchlist.add_symbol(symbol)
                    
                    logger.info(f"Loaded {len(symbols)} trading symbols")
                else:
                    logger.warning("No trading symbols found")
                    # Add some default symbols anyway
                    default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                    self.watchlist.set_available_symbols(default_symbols)
                    self.strategy_panel.set_available_symbols(default_symbols)
                    self.chart_widget.set_available_symbols(default_symbols)
                    
                    for symbol in default_symbols:
                        self.watchlist.add_symbol(symbol)
            else:
                logger.error("Failed to retrieve exchange information")
                # Add some default symbols anyway
                default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
                self.watchlist.set_available_symbols(default_symbols)
                self.strategy_panel.set_available_symbols(default_symbols)
                self.chart_widget.set_available_symbols(default_symbols)
                
                for symbol in default_symbols:
                    self.watchlist.add_symbol(symbol)
                
        except Exception as e:
            logger.error(f"Error loading initial data: {str(e)}")
            # Add some default symbols anyway
            default_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
            self.watchlist.set_available_symbols(default_symbols)
            self.strategy_panel.set_available_symbols(default_symbols)
            self.chart_widget.set_available_symbols(default_symbols)
            
            for symbol in default_symbols:
                self.watchlist.add_symbol(symbol)
    
    def update_data(self):
        """Update live data for all components."""
        try:
            # Update price data in watchlist
            result = self.watchlist.update_prices()
            if result is False:  # If update_prices indicates a problem
                logger.warning("Watchlist update failed, will retry in 5 seconds")
                self.after(5000, self.update_data)  # Retry in 5 seconds
                return
                
            # Schedule the next update
            self.after(1500, self.update_data)
            
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            # Even if there's an error, continue the update cycle after a short delay
            self.after(5000, self.update_data)  # Retry in 5 seconds