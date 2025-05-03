# File: src/cryptotrader/gui/components/ui/watchlist_widget.py
"""
Watchlist Widget

Displays selected cryptocurrency pairs with live bid/ask updates.
Symbol entry, exchange selector, and Add button are all here.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

from cryptotrader.config import get_logger
from cryptotrader.gui.components.logic.watchlist_logic import WatchlistLogic
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient
from cryptotrader.gui.app_styles import Colors, StyleNames, create_button

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    """
    Watchlist Widget

    Displays selected cryptocurrency pairs with live bid/ask updates.
    Symbol entry, exchange selector, and Add button are all here.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        # Apply themed frame style and padding
        self.configure(style='TFrame', padding=(10, 10))

        self.logger = logger
        self.unified_client = BinanceRestUnifiedClient()
        self.logic = WatchlistLogic(self.unified_client)

        # track symbols in insertion order
        self.watched_symbols: List[str] = []
        # map column/header → list of widgets or StringVars (for “Bid” and “Ask”)
        self.body_widgets: Dict[str, List] = {}
        self._headers = ["Symbol", "Bid", "Ask", "Remove"]
        # store after-job IDs so we can cancel when a symbol is removed
        self._refresh_jobs: Dict[str, str] = {}

        # Initialize UI
        self._init_ui()

    def set_available_symbols(self, symbols: List[str]) -> None:
        """
        Initialize the watchlist with a list of symbols.
        Clears any existing entries and adds the provided symbols.
        """
        # Remove all existing
        for sym in list(self.watched_symbols):
            self._remove_symbol(sym)
        # Add new in order
        for sym in symbols:
            self.symbol_var.set(sym)
            self._on_add()

    def _init_ui(self) -> None:
        # Configure grid
        for i in range(4):
            self.columnconfigure(i, weight=1)

        # Symbol entry
        self.symbol_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.symbol_var, width=15)
        entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Exchange dropdown
        self.exchange_var = tk.StringVar(value="Binance")
        exch_combo = ttk.Combobox(
            self,
            textvariable=self.exchange_var,
            values=["Binance"],
            state="readonly",
            width=12,
        )
        exch_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Add button
        add_btn = create_button(
            self,
            text="Add to watchlist",
            command=self._on_add,
            style_name=StyleNames.SUCCESS_BUTTON
        )
        add_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Table headers
        for col, header in enumerate(self._headers):
            lbl = ttk.Label(
                self,
                text=header,
                font=("Segoe UI", 10, "bold"),
                foreground=Colors.FOREGROUND
            )
            lbl.grid(row=1, column=col, padx=5, pady=5)

    def _on_add(self) -> None:
        symbol = self.symbol_var.get().strip().upper()
        exchange = self.exchange_var.get()
        # only Binance supported
        if exchange != "Binance":
            messagebox.showerror(
                "Unsupported Exchange",
                f"Exchange {exchange} not supported."
            )
            return

        # Validate symbol
        all_syms = self.unified_client.get_binance_symbols()
        if symbol not in all_syms:
            messagebox.showerror(
                "Symbol Not Found",
                f"Couldn’t find {symbol} on {exchange}."
            )
            return
        if symbol in self.watched_symbols:
            return

        # Add row and start updates
        self.watched_symbols.append(symbol)
        self._add_row(symbol)
        self.symbol_var.set("")
        self._refresh_symbol(symbol)

    def _add_row(self, symbol: str) -> None:
        row = 2 + (len(self.watched_symbols) - 1)
        # Symbol
        lbl_sym = ttk.Label(self, text=symbol, foreground=Colors.FOREGROUND)
        lbl_sym.grid(row=row, column=0, padx=5, pady=2)
        self.body_widgets.setdefault("Symbol", []).append(lbl_sym)

        # Bid
        bid_var = tk.StringVar(value="N/A")
        lbl_bid = ttk.Label(self, textvariable=bid_var, foreground=Colors.FOREGROUND)
        lbl_bid.grid(row=row, column=1, padx=5, pady=2)
        self.body_widgets.setdefault("bid_var", []).append(bid_var)
        self.body_widgets.setdefault("Bid", []).append(lbl_bid)

        # Ask
        ask_var = tk.StringVar(value="N/A")
        lbl_ask = ttk.Label(self, textvariable=ask_var, foreground=Colors.FOREGROUND)
        lbl_ask.grid(row=row, column=2, padx=5, pady=2)
        self.body_widgets.setdefault("ask_var", []).append(ask_var)
        self.body_widgets.setdefault("Ask", []).append(lbl_ask)

        # Remove button
        btn_rm = create_button(
            self,
            text="Remove",
            command=lambda s=symbol: self._remove_symbol(s),
            style_name=StyleNames.DANGER_BUTTON
        )
        btn_rm.grid(row=row, column=3, padx=5, pady=2)
        self.body_widgets.setdefault("Remove", []).append(btn_rm)

    def _refresh_symbol(self, symbol: str) -> None:
        def callback(sym: str, data: dict) -> None:
            self._update_symbol_data(sym, data)
        self.logic.fetch_symbol_data(symbol, callback)
        job = self.after(5000, lambda: self._refresh_symbol(symbol))
        self._refresh_jobs[symbol] = job

    def _update_symbol_data(self, symbol: str, data: dict) -> None:
        try:
            idx = self.watched_symbols.index(symbol)
        except ValueError:
            return
        bid = data.get("bidPrice") or data.get("bid") or "N/A"
        ask = data.get("askPrice") or data.get("ask") or "N/A"
        self.body_widgets["bid_var"][idx].set(bid)
        self.body_widgets["ask_var"][idx].set(ask)

    def _remove_symbol(self, symbol: str) -> None:
        if symbol not in self.watched_symbols:
            return
        idx = self.watched_symbols.index(symbol)
        job = self._refresh_jobs.pop(symbol, None)
        if job:
            self.after_cancel(job)
        self.watched_symbols.pop(idx)
        for key, lst in list(self.body_widgets.items()):
            item = lst.pop(idx)
            if isinstance(item, (ttk.Label, ttk.Button)):
                item.grid_forget()
        logger.info(f"Removed {symbol} from watchlist")
