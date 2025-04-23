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

import time
import random
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from config import get_logger
from src.cryptotrader.gui.components.styles import Colors, create_table

logger = get_logger(__name__)

class TradeHistoryWidget(ttk.Frame):
    """Widget for displaying trade history."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.trades = []  # Store trade data
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Create header with controls
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Label(header_frame, text="Trade History").pack(side=tk.LEFT)
        
        # Add a clear button
        self.clear_btn = ttk.Button(header_frame, text="Clear History", command=self.clear_history)
        self.clear_btn.pack(side=tk.RIGHT)
        
        # Create table for trade data
        columns = ["Time", "Symbol", "Strategy", "Side", "Price", "Quantity", "Status", "P&L"]
        table_frame, self.table = create_table(self, columns, height=15)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configure tag styles for the table
        self.table.tag_configure("buy", foreground=Colors.BUY)
        self.table.tag_configure("sell", foreground=Colors.SELL)
        self.table.tag_configure("profit", foreground=Colors.SUCCESS)
        self.table.tag_configure("loss", foreground=Colors.ERROR)
    
    def add_trade(self, trade_data):
        """Add a trade to the history.
        
        Args:
            trade_data: Dictionary containing trade details
        """
        # Store the trade
        self.trades.append(trade_data)
        
        # Format datetime
        dt = datetime.fromtimestamp(int(trade_data['time'] / 1000))
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Format values for display
        symbol = trade_data['symbol']
        strategy = trade_data.get('strategy', 'Manual')
        side = trade_data['side']
        price = f"{float(trade_data['price']):.8f}"
        quantity = f"{float(trade_data['quantity']):.8f}"
        status = trade_data.get('status', 'FILLED')
        
        # Format P&L if available
        pnl = trade_data.get('pnl')
        if pnl is not None:
            pnl_str = f"{float(pnl):.2f}"
            tag = "profit" if float(pnl) >= 0 else "loss"
        else:
            pnl_str = "--"
            tag = ""
        
        # Add to table with appropriate tags
        values = (time_str, symbol, strategy, side, price, quantity, status, pnl_str)
        
        # Determine the tag based on side (buy/sell)
        side_tag = "buy" if side == "BUY" else "sell"
        
        item_id = self.table.insert("", "end", values=values, tags=(side_tag, tag))
        
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
        for item_id in self.table.get_children():
            values = self.table.item(item_id)["values"]
            current_time = values[0]
            current_symbol = values[1]
            
            # Match the trade by time and symbol (simplistic approach)
            # In a real app, you'd use a unique trade ID
            if (trade_id == f"{current_time}_{current_symbol}"):
                # Get all values
                values = list(values)
                
                # Update status
                values[6] = status
                
                # Update P&L if provided
                if pnl is not None:
                    pnl_str = f"{float(pnl):.2f}"
                    values[7] = pnl_str
                    
                    # Update tag based on P&L
                    tag = "profit" if float(pnl) >= 0 else "loss"
                    current_tags = list(self.table.item(item_id, "tags"))
                    
                    # Remove existing profit/loss tags
                    if "profit" in current_tags:
                        current_tags.remove("profit")
                    if "loss" in current_tags:
                        current_tags.remove("loss")
                    
                    # Add new tag
                    current_tags.append(tag)
                    
                    # Update item
                    self.table.item(item_id, values=tuple(values), tags=tuple(current_tags))
                else:
                    # Just update values without changing tags
                    self.table.item(item_id, values=tuple(values))
                
                logger.info(f"Updated trade {trade_id} status to {status}")
                break
    
    def clear_history(self):
        """Clear all trades from the history."""
        self.trades = []
        for item_id in self.table.get_children():
            self.table.delete(item_id)
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