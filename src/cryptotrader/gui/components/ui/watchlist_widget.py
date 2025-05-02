# File: src/gui/components/ui/watchlist_widget.py
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

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
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

        self._init_ui()

    def _init_ui(self):
        # --- Symbol entry first ---
        self.symbol_var = tk.StringVar()
        symbol_entry = ttk.Entry(self, textvariable=self.symbol_var, width=15)
        symbol_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # --- Exchange dropdown next ---
        self.exchange_var = tk.StringVar(value="Binance")
        exch_combo = ttk.Combobox(
            self,
            textvariable=self.exchange_var,
            values=["Binance"],
            state="readonly",
            width=10,
        )
        exch_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # --- Add button last ---
        add_btn = ttk.Button(self, text="Add to watchlist", command=self._on_add)
        add_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # --- Table headers ---
        for col, header in enumerate(self._headers):
            lbl = ttk.Label(self, text=header, font=("TkDefaultFont", 10, "bold"))
            lbl.grid(row=1, column=col, padx=5, pady=5)

    def _on_add(self):
        symbol = self.symbol_var.get().strip().upper()
        exchange = self.exchange_var.get()
        # only Binance supported for now
        if exchange != "Binance":
            messagebox.showerror(
                "Unsupported Exchange", f"Exchange {exchange} not supported."
            )
            return

        # call unified client properly
        all_syms = self.unified_client.get_binance_symbols()
        if symbol not in all_syms:
            messagebox.showerror(
                "Symbol Not Found", f"Couldn’t find {symbol} on {exchange}."
            )
            return

        if symbol in self.watched_symbols:
            return  # already in list

        # add to our own list, build UI row, and start polling
        self.watched_symbols.append(symbol)
        self._add_row(symbol)
        self.symbol_var.set("")
        self._refresh_symbol(symbol)

    def _add_row(self, symbol: str):
        row = 2 + (len(self.watched_symbols) - 1)
        # Symbol label
        lbl_sym = ttk.Label(self, text=symbol)
        lbl_sym.grid(row=row, column=0, padx=5, pady=2)
        self.body_widgets.setdefault("Symbol", []).append(lbl_sym)

        # Bid value
        bid_var = tk.StringVar(value="N/A")
        lbl_bid = ttk.Label(self, textvariable=bid_var)
        lbl_bid.grid(row=row, column=1, padx=5, pady=2)
        self.body_widgets.setdefault("bid_var", []).append(bid_var)
        self.body_widgets.setdefault("Bid", []).append(lbl_bid)

        # Ask value
        ask_var = tk.StringVar(value="N/A")
        lbl_ask = ttk.Label(self, textvariable=ask_var)
        lbl_ask.grid(row=row, column=2, padx=5, pady=2)
        self.body_widgets.setdefault("ask_var", []).append(ask_var)
        self.body_widgets.setdefault("Ask", []).append(lbl_ask)

        # Remove button
        btn_rm = ttk.Button(
            self, text="Remove", command=lambda s=symbol: self._remove_symbol(s)
        )
        btn_rm.grid(row=row, column=3, padx=5, pady=2)
        self.body_widgets.setdefault("Remove", []).append(btn_rm)

    def _refresh_symbol(self, symbol: str):
        # fetch once, then schedule the next call
        def _cb(sym, data):
            self._update_symbol_data(sym, data)

        self.logic.fetch_symbol_data(symbol, _cb)
        job = self.after(5000, lambda: self._refresh_symbol(symbol))
        self._refresh_jobs[symbol] = job

    def _update_symbol_data(self, symbol: str, data: dict):
        try:
            idx = self.watched_symbols.index(symbol)
        except ValueError:
            return

        bid = data.get("bidPrice") or data.get("bid") or "N/A"
        ask = data.get("askPrice") or data.get("ask") or "N/A"
        self.body_widgets["bid_var"][idx].set(bid)
        self.body_widgets["ask_var"][idx].set(ask)

    def _remove_symbol(self, symbol: str):
        if symbol not in self.watched_symbols:
            return
        idx = self.watched_symbols.index(symbol)
        # cancel its scheduled refresh
        job = self._refresh_jobs.pop(symbol, None)
        if job:
            self.after_cancel(job)

        # remove from our list
        self.watched_symbols.pop(idx)

        # tear down widgets/vars in every column
        for key, lst in list(self.body_widgets.items()):
            item = lst.pop(idx)
            # grid_forget only for actual widgets
            if isinstance(item, (ttk.Label, ttk.Button)):
                item.grid_forget()

        logger.info(f"Removed {symbol} from watchlist")
