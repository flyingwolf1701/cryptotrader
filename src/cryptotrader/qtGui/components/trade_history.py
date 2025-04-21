"""
Trade History Component

Displays a history of executed trades with details such as:
- Time/date
- Symbol
- Side (buy/sell)
- Price
- Quantity
- Status
- Profit/Loss
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QLabel, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor, QBrush

from cryptotrader.config import get_logger

logger = get_logger(__name__)

class TradeHistoryWidget(QWidget):
    """Widget for displaying trade history."""
    
    def __init__(self):
        super().__init__()
        
        self.trades = []  # Store trade data
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Trade History"))
        header_layout.addStretch()
        
        # Clear button
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Time", "Symbol", "Strategy", "Side", "Price", "Quantity", "Status", "P&L"
        ])
        
        # Set column widths
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for col in [0, 3, 5, 6, 7]:  # Time, Side, Quantity, Status, P&L
            self.table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.table)
    
    def add_trade(self, trade_data):
        """Add a trade to the history.
        
        Args:
            trade_data: Dictionary containing trade details
        """
        # Store the trade
        self.trades.append(trade_data)
        
        # Add to table
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Format datetime
        dt = QDateTime.fromSecsSinceEpoch(int(trade_data['time'] / 1000))
        time_str = dt.toString("yyyy-MM-dd hh:mm:ss")
        
        # Add cells
        self.table.setItem(row, 0, QTableWidgetItem(time_str))
        self.table.setItem(row, 1, QTableWidgetItem(trade_data['symbol']))
        self.table.setItem(row, 2, QTableWidgetItem(trade_data.get('strategy', 'Manual')))
        
        # Set side with color
        side_item = QTableWidgetItem(trade_data['side'])
        side_color = QColor('green') if trade_data['side'] == 'BUY' else QColor('red')
        side_item.setForeground(QBrush(side_color))
        self.table.setItem(row, 3, side_item)
        
        # Price and quantity
        self.table.setItem(row, 4, QTableWidgetItem(f"{float(trade_data['price']):.8f}"))
        self.table.setItem(row, 5, QTableWidgetItem(f"{float(trade_data['quantity']):.8f}"))
        
        # Status
        status_item = QTableWidgetItem(trade_data.get('status', 'FILLED'))
        self.table.setItem(row, 6, status_item)
        
        # P&L (if available)
        pnl = trade_data.get('pnl')
        if pnl is not None:
            pnl_item = QTableWidgetItem(f"{float(pnl):.2f}")
            pnl_color = QColor('green') if float(pnl) >= 0 else QColor('red')
            pnl_item.setForeground(QBrush(pnl_color))
            self.table.setItem(row, 7, pnl_item)
        else:
            self.table.setItem(row, 7, QTableWidgetItem("--"))
        
        # Scroll to the new row
        self.table.scrollToBottom()
        
        logger.info(f"Added trade: {trade_data['symbol']} {trade_data['side']} to history")
    
    def update_trade_status(self, trade_id, status, pnl=None):
        """Update the status and P&L of an existing trade.
        
        Args:
            trade_id: ID of the trade to update
            status: New status
            pnl: Profit/Loss (optional)
        """
        # Update in data storage
        for trade in self.trades:
            if trade.get('id') == trade_id:
                trade['status'] = status
                if pnl is not None:
                    trade['pnl'] = pnl
                break
        
        # Update in table
        for row in range(self.table.rowCount()):
            current_time = self.table.item(row, 0).text()
            current_symbol = self.table.item(row, 1).text()
            
            # Match the trade by time and symbol (simplistic approach)
            # In a real app, you'd use a unique trade ID
            if (trade_id == f"{current_time}_{current_symbol}"):
                # Update status
                self.table.item(row, 6).setText(status)
                
                # Update P&L if provided
                if pnl is not None:
                    pnl_item = QTableWidgetItem(f"{float(pnl):.2f}")
                    pnl_color = QColor('green') if float(pnl) >= 0 else QColor('red')
                    pnl_item.setForeground(QBrush(pnl_color))
                    self.table.setItem(row, 7, pnl_item)
                
                logger.info(f"Updated trade {trade_id} status to {status}")
                break
    
    def clear_history(self):
        """Clear all trades from the history."""
        self.trades = []
        self.table.setRowCount(0)
        logger.info("Trade history cleared")
    
    # Add mock trades for testing
    def add_mock_trades(self):
        """Add mock trades for UI testing."""
        import time
        import random
        
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
        strategies = ["Breakout", "MACD", "Manual", "Grid"]
        sides = ["BUY", "SELL"]
        statuses = ["FILLED", "PARTIALLY_FILLED", "CANCELED"]
        
        # Create some mock trades
        for i in range(10):
            symbol = random.choice(symbols)
            side = random.choice(sides)
            price = random.uniform(100, 50000)
            quantity = random.uniform(0.01, 2)
            
            trade = {
                'time': int(time.time() * 1000) - random.randint(0, 1000000),
                'symbol': symbol,
                'strategy': random.choice(strategies),
                'side': side,
                'price': price,
                'quantity': quantity,
                'status': random.choice(statuses),
                'pnl': random.uniform(-100, 100) if random.random() > 0.3 else None
            }
            
            self.add_trade(trade)