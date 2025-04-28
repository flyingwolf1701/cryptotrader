# File: src/gui/components/ui/trade_history_widget.py
"""
Trade History Widget

Displays user's past trades for a selected symbol, with PNL calculation.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List

from config import get_logger
from src.gui.components.ui.symbol_search_widget import SymbolSearchWidget
from src.gui.components.logic.trade_history_logic import TradeHistoryLogic
from src.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class TradeHistoryWidget(ttk.Frame):
    """UI component for displaying historical trades and PNL."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        self.unified_client = BinanceRestUnifiedClient()
        self.logic = TradeHistoryLogic(self.unified_client)

        self.selected_symbol: Optional[str] = None
        self.trades: List[dict] = []

        self._init_ui()

    def _init_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Top frame for symbol search
        top_frame = ttk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.symbol_search = SymbolSearchWidget(
            top_frame,
            on_select=self._on_symbol_selected,
            width=30,
            client=self.unified_client
        )
        self.symbol_search.pack(fill=tk.X, padx=5, pady=5)

        # Table
        self._table = ttk.Treeview(self, columns=("side", "qty", "price", "time"), show="headings")
        for col in ("side", "qty", "price", "time"):
            self._table.heading(col, text=col.capitalize())
            self._table.column(col, anchor="center")

        self._table.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # PNL label
        self.pnl_var = tk.StringVar(value="PNL: -")
        self.pnl_label = ttk.Label(self, textvariable=self.pnl_var, font=("Segoe UI", 10, "bold"))
        self.pnl_label.pack(side=tk.TOP, pady=5)

        # Refresh button
        self.refresh_button = ttk.Button(self, text="Refresh", command=self._refresh_trades)
        self.refresh_button.pack(side=tk.TOP, pady=5)

    def _on_symbol_selected(self, symbol: str):
        self.selected_symbol = symbol
        self._refresh_trades()

    def _refresh_trades(self):
        if not self.selected_symbol:
            return

        self.trades = self.logic.fetch_trades(self.selected_symbol)
        self._update_table()
        self._update_pnl()

    def _update_table(self):
        self._table.delete(*self._table.get_children())

        for trade in self.trades:
            self._table.insert(
                "", "end",
                values=(
                    trade["side"],
                    f'{float(trade["qty"]):.6f}',
                    f'{float(trade["price"]):.2f}',
                    trade["time"]
                )
            )

    def _update_pnl(self):
        pnl = self.logic.calculate_pnl(self.trades)
        self.pnl_var.set(f"PNL: {pnl:.2f}")
