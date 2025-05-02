"""

# Fix import path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # Add project root to Python path

Trades Component

Displays executed trades information in a grid layout.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import typing

from cryptotrader.config import get_logger
from cryptotrader.gui.components.styles import Colors

logger = get_logger(__name__)


class TradesWatch(ttk.Frame):
    """Widget for displaying trade information."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Create header with controls
        header_frame = ttk.Frame(self)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))

        ttk.Label(header_frame, text="Trades", font=("Segoe UI", 10, "bold")).pack(
            side=tk.LEFT
        )

        # Add a clear button
        self.clear_btn = ttk.Button(
            header_frame, text="Clear", command=self.clear_trades
        )
        self.clear_btn.pack(side=tk.RIGHT)

        # Create treeview for trades
        columns = ("time", "symbol", "strategy", "side", "price", "quantity", "status")
        self.trades_tree = ttk.Treeview(
            self, columns=columns, show="headings", height=15
        )
        self.trades_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.trades_tree.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trades_tree.configure(yscrollcommand=scrollbar.set)

        # Configure columns
        self.trades_tree.column("time", width=150, anchor=tk.W)
        self.trades_tree.column("symbol", width=100, anchor=tk.CENTER)
        self.trades_tree.column("strategy", width=100, anchor=tk.CENTER)
        self.trades_tree.column("side", width=80, anchor=tk.CENTER)
        self.trades_tree.column("price", width=120, anchor=tk.CENTER)
        self.trades_tree.column("quantity", width=100, anchor=tk.CENTER)
        self.trades_tree.column("status", width=100, anchor=tk.CENTER)

        # Configure headings
        self.trades_tree.heading("time", text="Time")
        self.trades_tree.heading("symbol", text="Symbol")
        self.trades_tree.heading("strategy", text="Strategy")
        self.trades_tree.heading("side", text="Side")
        self.trades_tree.heading("price", text="Price")
        self.trades_tree.heading("quantity", text="Quantity")
        self.trades_tree.heading("status", text="Status")

        # Configure tags for different types of trades
        self.trades_tree.tag_configure("buy", foreground=Colors.BUY)
        self.trades_tree.tag_configure("sell", foreground=Colors.SELL)

    def add_trade(self, data: typing.Dict):
        """Add a trade to the display.

        Args:
            data: Dictionary containing trade details
        """
        # Format time if it's a timestamp
        time_str = data.get("time", "")
        if isinstance(time_str, int):
            dt = datetime.fromtimestamp(time_str / 1000)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Format price and quantity
        price = data.get("price", 0)
        if isinstance(price, (int, float)):
            price_str = f"{price:.8f}"
        else:
            price_str = str(price)

        quantity = data.get("quantity", 0)
        if isinstance(quantity, (int, float)):
            quantity_str = f"{quantity:.8f}"
        else:
            quantity_str = str(quantity)

        # Prepare values for treeview
        values = (
            time_str,
            data.get("symbol", "N/A"),
            data.get("strategy", "Manual"),
            data.get("side", "BUY"),
            price_str,
            quantity_str,
            data.get("status", "FILLED"),
        )

        # Insert with appropriate tag
        side = data.get("side", "BUY")
        tag = "buy" if side == "BUY" else "sell"

        self.trades_tree.insert("", "end", values=values, tags=(tag,))

        logger.info(f"Added trade: {data.get('symbol')} {data.get('side')}")

    def clear_trades(self):
        """Clear all trades from the display."""
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)

        logger.info("Cleared all trades")

    def add_mock_trades(self):
        """Add mock trades for testing purposes."""
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
                "time": int(time.time() * 1000) - random.randint(0, 1000000),
                "symbol": symbol,
                "strategy": random.choice(strategies),
                "side": side,
                "price": price,
                "quantity": quantity,
                "status": random.choice(statuses),
            }

            self.add_trade(trade)
