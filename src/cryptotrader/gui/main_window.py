"""
CryptoTrader Main Window

This module implements the main application window and coordinates
between different UI components.
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSplitter, QTabWidget
from PySide6.QtCore import QTimer, Qt

# Import with relative imports to work within the project structure
from src.cryptotrader.config import get_logger
from src.cryptotrader.services.binance.restAPI import MarketOperations, SystemOperations

# Import components
from src.cryptotrader.gui.components import (
    WatchlistWidget, 
    TradeHistoryWidget, 
    StrategyPanel,
    LoggingPanel,
    ChartWidget
    )

logger = get_logger(__name__)

class MainWindow(QMainWindow):
    """Main application window for the CryptoTrader dashboard."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.setWindowTitle("CryptoTrader Dashboard")
        self.resize(1280, 800)
        
        # Initialize API clients
        self.market_client = MarketOperations()
        self.system_client = SystemOperations()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # Create UI elements
        self.setup_ui()
        
        # Setup update timer for live data
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1500)  # Update every 1.5 seconds
        
        # Load initial data
        self.load_initial_data()
        
        logger.info("CryptoTrader Dashboard initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Create main splitter (horizontal)
        self.main_splitter = QSplitter(Qt.Horizontal)
        
        # Create left side widget (chart and watchlist)
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create right side with tabs
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget for trading components
        self.tabs = QTabWidget()
        self.right_layout.addWidget(self.tabs)
        
        # Add widgets to splitter
        self.main_splitter.addWidget(self.left_widget)
        self.main_splitter.addWidget(self.right_widget)
        
        # Set initial splitter sizes (60% left, 40% right)
        self.main_splitter.setSizes([600, 400])
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.main_splitter)
        
        # Create and add components
        self.init_components()
    
    def init_components(self):
        """Initialize dashboard components and add them to the layout."""
        # Create components
        self.chart_widget = ChartWidget(self.market_client)
        self.watchlist = WatchlistWidget(self.market_client)
        self.trade_history = TradeHistoryWidget()
        self.strategy_panel = StrategyPanel(self.market_client)
        self.logging_panel = LoggingPanel()
        
        # Connect signal handlers
        self.strategy_panel.log_message.connect(self.logging_panel.add_log)
        self.watchlist.symbol_selected.connect(self.chart_widget.symbol_changed)
        
        # Add mock trades for demo purposes
        self.trade_history.add_mock_trades()
        
        # Left side: add chart and watchlist
        self.left_layout.addWidget(self.chart_widget, 3)  # Chart takes 3/4 of vertical space
        self.left_layout.addWidget(self.watchlist, 1)     # Watchlist takes 1/4 of vertical space
        
        # Right side: add tabs for trading components
        self.tabs.addTab(self.strategy_panel, "Trading Strategies")
        self.tabs.addTab(self.trade_history, "Trade History")
        self.tabs.addTab(self.logging_panel, "Logs")
    
    def load_initial_data(self):
        """Load initial data for the dashboard components."""
        try:
            # Load exchange info and available symbols
            exchange_info = self.system_client.get_exchange_info()
            if exchange_info:
                symbols = [symbol['symbol'] for symbol in exchange_info.get('symbols', [])
                          if symbol.get('status') == 'TRADING']
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
                logger.error("Failed to retrieve exchange information")
                
        except Exception as e:
            logger.error(f"Error loading initial data: {str(e)}")
    
    def update_data(self):
        """Update live data for all components."""
        try:
            # Update price data in watchlist
            self.watchlist.update_prices()
            
            # Update chart if needed
            # self.chart_widget.refresh_chart()
            
            # Update other components that need periodic updates
            # self.trade_history.update_trades()
            
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")