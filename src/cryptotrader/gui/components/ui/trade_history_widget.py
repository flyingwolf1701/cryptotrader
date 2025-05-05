# File: src/cryptotrader/gui/components/ui/trade_history_widget.py
#!/usr/bin/env python3
"""
TradeHistoryWidget

Displays executed trades in a grid layout with add, clear, and mock methods.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import typing
import time
import random

from cryptotrader.config import get_logger
from cryptotrader.gui.components.styles import Colors
from cryptotrader.gui.components.logic.trade_history_logic import TradeHistoryLogic

logger = get_logger(__name__)

class TradeHistoryWidget(ttk.Frame):
    """UI component for displaying historical trades and PNL."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.logic = TradeHistoryLogic()
        self.trades: typing.List[dict] = []

        self._init_ui()
        # Optionally populate with mock trades:
        # self.add_mock_trades()

    def _init_ui(self):
        """Initialize UI: header, table, scrollbar, and buttons."""
        # Header
        header = ttk.Frame(self)
        header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        ttk.Label(header, text="Trades", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        clear_btn = ttk.Button(header, text="Clear", command=self.clear_trades)
        clear_btn.pack(side=tk.RIGHT)

        # Treeview for trades
        columns = ("time", "symbol", "strategy", "side", "price", "quantity", "status")
        self.trades_tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.trades_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.trades_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trades_tree.configure(yscrollcommand=scrollbar.set)

        # Configure columns and headings
        widths = {
            "time": 150, "symbol": 100, "strategy": 100,
            "side": 80, "price": 120, "quantity": 100, "status": 100
        }
        for col in columns:
            self.trades_tree.heading(col, text=col.capitalize())
            self.trades_tree.column(col, width=widths[col], anchor=tk.CENTER)

        # Color tags
        self.trades_tree.tag_configure("buy", foreground=Colors.BUY)
        self.trades_tree.tag_configure("sell", foreground=Colors.SELL)

    def add_trade(self, data: typing.Dict):
        """
        Add a single trade record to the treeview.
        """
        # Format timestamp
        ts = data.get("time", "")
        if isinstance(ts, (int, float)):
            ts = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")

        # Format price & quantity
        price = data.get("price", 0)
        price_str = f"{float(price):.8f}" if isinstance(price, (int, float)) else str(price)
        qty = data.get("quantity", 0)
        qty_str = f"{float(qty):.8f}" if isinstance(qty, (int, float)) else str(qty)

        values = (
            ts,
            data.get("symbol", "N/A"),
            data.get("strategy", "Manual"),
            data.get("side", "BUY"),
            price_str,
            qty_str,
            data.get("status", "FILLED"),
        )
        tag = "buy" if data.get("side", "BUY") == "BUY" else "sell"
        self.trades_tree.insert("", "end", values=values, tags=(tag,))

        logger.info(f"Added trade: {data.get('symbol')} {data.get('side')}")

    def clear_trades(self):
        """Clear all entries from the treeview."""
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        logger.info("Cleared all trades")

    def add_mock_trades(self, count: int = 10):
        """
        Populate the treeview with mock trades for testing.
        """

        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
        strategies = ["Breakout", "MACD", "Manual", "Grid"]
        sides = ["BUY", "SELL"]
        statuses = ["FILLED", "PARTIALLY_FILLED", "CANCELED"]

        for _ in range(count):
            trade = {
                "time": int(time.time() * 1000) - random.randint(0, 1_000_000),
                "symbol": random.choice(symbols),
                "strategy": random.choice(strategies),
                "side": random.choice(sides),
                "price": random.uniform(100, 50_000),
                "quantity": random.uniform(0.01, 2),
                "status": random.choice(statuses),
            }
            self.add_trade(trade)
