#!/usr/bin/env python3
"""
Trades Component

Displays executed trades information in a styled, dark-themed table.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import typing

from cryptotrader.config import get_logger
from cryptotrader.gui.app_styles import (
    apply_theme,
    Colors,
    create_table,
    create_button,
    StyleNames,
)

logger = get_logger(__name__)


class TradesWatch(tk.Frame):
    """Widget for displaying trade information in a styled table with dark theme support."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent, bg=Colors.BACKGROUND)
        # Apply global theme and retrieve fonts
        fonts = apply_theme(self.winfo_toplevel())

        # Header: title and clear button
        header_frame = tk.Frame(self, bg=Colors.BACKGROUND, padx=8, pady=8)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="Trades",
            font=fonts['bold'],
            bg=Colors.BACKGROUND,
            fg=Colors.FOREGROUND,
        )
        title_lbl.pack(side=tk.LEFT)

        clear_btn = create_button(
            header_frame,
            text="Clear",
            command=self.clear_trades,
            style_name=StyleNames.DANGER_BUTTON,
        )
        clear_btn.pack(side=tk.RIGHT)

        # Styled table for trades
        columns = ["Time", "Symbol", "Strategy", "Side", "Price", "Quantity", "Status"]
        widths = [150, 100, 120, 80, 100, 100, 80]
        table_frame, self.trades_tree = create_table(
            self,
            columns=columns,
            height=15,
            column_widths=widths,
            padding=4,
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Row tag styling: colored text with subtle alternate background
        self.trades_tree.tag_configure(
            "BUY",
            foreground=Colors.BUY,
            background=Colors.BACKGROUND_LIGHT,
        )
        self.trades_tree.tag_configure(
            "SELL",
            foreground=Colors.SELL,
            background=Colors.BACKGROUND_LIGHT,
        )

    def clear_trades(self):
        """Remove all trades from the table."""
        for iid in self.trades_tree.get_children():
            self.trades_tree.delete(iid)
        logger.info("Cleared all trades")

    def add_trade(self, data: typing.Dict):
        """Add or update a trade in the table based on timestamp-symbol-side key."""
        # Format timestamp
        ts = data.get("time")
        if isinstance(ts, (int, float)):
            time_str = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = str(ts)

        symbol = data.get("symbol", "N/A")
        strategy = data.get("strategy", "Manual")
        side = data.get("side", "BUY").upper()

        price = data.get("price", 0)
        price_str = f"{price:.8f}" if isinstance(price, (int, float)) else str(price)

        qty = data.get("quantity", 0)
        qty_str = f"{qty:.8f}" if isinstance(qty, (int, float)) else str(qty)

        status = data.get("status", "")

        # Unique row ID
        item_id = f"{time_str}_{symbol}_{side}"
        values = (time_str, symbol, strategy, side, price_str, qty_str, status)

        if self.trades_tree.exists(item_id):
            self.trades_tree.item(item_id, values=values)
            logger.info(f"Updated trade {item_id}")
        else:
            self.trades_tree.insert(
                "",
                "end",
                iid=item_id,
                values=values,
                tags=(side,),
            )
            logger.info(f"Added trade {item_id}")
