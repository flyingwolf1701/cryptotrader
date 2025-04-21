"""
Watchlist Component

Displays current market prices for selected cryptocurrency pairs.
Allows adding and removing symbols from the watchlist.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QHeaderView, QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QBrush

from cryptotrader.config import get_logger

logger = get_logger(__name__)

class WatchlistWidget(QWidget):
    """Widget for displaying cryptocurrency price information."""
    
    # Signal emitted when a symbol is selected in the watchlist table
    symbol_selected = Signal(str)
    
    def __init__(self, market_client):
        super().__init__()
        
        self.market_client = market_client
        self.available_symbols = []
        self.watched_symbols = set()
        self.price_data = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Add symbol controls
        controls_layout = QHBoxLayout()
        
        # Symbol selector
        self.symbol_selector = QComboBox()
        self.symbol_selector.setEditable(True)
        self.symbol_selector.setInsertPolicy(QComboBox.NoInsert)
        self.symbol_selector.setMinimumWidth(150)
        
        # Add button
        self.add_button = QPushButton("Add Symbol")
        self.add_button.clicked.connect(self.add_selected_symbol)
        
        controls_layout.addWidget(QLabel("Symbol:"))
        controls_layout.addWidget(self.symbol_selector)
        controls_layout.addWidget(self.add_button)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Symbol", "Price", "24h Change", "Volume", "Remove"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 80)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemClicked.connect(self.on_table_item_clicked)
        
        layout.addWidget(self.table)
    
    def set_available_symbols(self, symbols):
        """Set the list of available trading symbols."""
        self.available_symbols = sorted(symbols)
        self.symbol_selector.clear()
        self.symbol_selector.addItems(self.available_symbols)
    
    def add_selected_symbol(self):
        """Add the currently selected symbol to the watchlist."""
        symbol = self.symbol_selector.currentText().strip().upper()
        self.add_symbol(symbol)
    
    def add_symbol(self, symbol):
        """Add a symbol to the watchlist table."""
        if not symbol or symbol in self.watched_symbols or symbol not in self.available_symbols:
            return
        
        # Add to tracked symbols
        self.watched_symbols.add(symbol)
        
        # Add new row to table
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Add symbol cell
        self.table.setItem(row, 0, QTableWidgetItem(symbol))
        
        # Add placeholder data cells
        for col in range(1, 4):
            self.table.setItem(row, col, QTableWidgetItem("Loading..."))
        
        # Add remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda: self.remove_symbol(symbol))
        self.table.setCellWidget(row, 4, remove_btn)
        
        # Fetch initial price data
        self.fetch_symbol_data(symbol)
        
        logger.info(f"Added {symbol} to watchlist")
    
    def remove_symbol(self, symbol):
        """Remove a symbol from the watchlist."""
        if symbol not in self.watched_symbols:
            return
        
        # Find and remove the row
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == symbol:
                self.table.removeRow(row)
                break
        
        # Remove from tracked symbols
        self.watched_symbols.remove(symbol)
        
        # Remove from price data
        if symbol in self.price_data:
            del self.price_data[symbol]
        
        logger.info(f"Removed {symbol} from watchlist")
    
    def fetch_symbol_data(self, symbol):
        """Fetch price data for a specific symbol."""
        try:
            # Get 24hr ticker data
            ticker = self.market_client.get_24h_stats(symbol)
            if ticker:
                self.update_symbol_data(symbol, ticker)
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
    
    def update_symbol_data(self, symbol, ticker_data):
        """Update the UI with new ticker data."""
        # Store the data
        self.price_data[symbol] = ticker_data
        
        # Find the row
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == symbol:
                # Update price
                price = float(ticker_data.get('lastPrice', 0))
                self.table.setItem(row, 1, QTableWidgetItem(f"{price:.8f}"))
                
                # Update 24h change
                change_pct = float(ticker_data.get('priceChangePercent', 0))
                change_item = QTableWidgetItem(f"{change_pct:.2f}%")
                
                # Set color based on change direction
                if change_pct > 0:
                    change_item.setForeground(QBrush(QColor('green')))
                elif change_pct < 0:
                    change_item.setForeground(QBrush(QColor('red')))
                
                self.table.setItem(row, 2, change_item)
                
                # Update volume
                volume = float(ticker_data.get('volume', 0))
                self.table.setItem(row, 3, QTableWidgetItem(f"{volume:.2f}"))
                
                break
    
    def update_prices(self):
        """Update price data for all watched symbols."""
        if not self.watched_symbols:
            return
        
        try:
            # We can fetch all tickers in one call for efficiency
            tickers = self.market_client.get_24h_stats(symbol=None)  # None fetches all tickers
            
            if tickers:
                # Process each ticker in the response
                for ticker in tickers:
                    symbol = ticker.get('symbol')
                    if symbol in self.watched_symbols:
                        self.update_symbol_data(symbol, ticker)
        except Exception as e:
            logger.error(f"Error updating prices: {str(e)}")
    
    def on_table_item_clicked(self, item):
        """Handle table item clicks.
        
        When a row is clicked, emit the symbol selected signal.
        """
        # Get the symbol from the first column of the clicked row
        symbol_item = self.table.item(item.row(), 0)
        if symbol_item:
            symbol = symbol_item.text()
            # Emit the signal with the selected symbol
            self.symbol_selected.emit(symbol)
            logger.info(f"Selected symbol: {symbol}")
            
            # Also update the symbol selector to match
            index = self.symbol_selector.findText(symbol)
            if index >= 0:
                self.symbol_selector.setCurrentIndex(index)