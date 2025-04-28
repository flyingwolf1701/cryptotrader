# File: src/gui/components/ui/watchlist_widget.py
"""
Watchlist Widget

Displays selected cryptocurrency pairs with live bid/ask updates.
Allows adding symbols using the SymbolSearchWidget.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

from config import get_logger
from src.gui.components.styles import Colors
from src.gui.components.ui.symbol_search_widget import SymbolSearchWidget
from src.gui.components.logic.watchlist_logic import WatchlistLogic
from src.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    """UI component for displaying a watchlist of cryptocurrency symbols."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        self.unified_client = BinanceRestUnifiedClient()
        self.logic = WatchlistLogic(self.unified_client)

        self.watched_symbols = set()
        self.body_widgets = {}
        self._body_index = 1

        self._init_ui()

    def _init_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._commands_frame = ttk.Frame(self)
        self._commands_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.symbol_search = SymbolSearchWidget(
            self._commands_frame,
            on_add=self.add_symbol,
            width=30,
            client=self.unified_client
        )
        self.symbol_search.pack(fill=tk.X, padx=5, pady=5)

        self._table_frame = ttk.Frame(self)
        self._table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        for i in range(5):  # 5 columns
            self._table_frame.columnconfigure(i, weight=1)

        self._headers = ["symbol", "exchange", "bid", "ask", "remove"]
        for idx, h in enumerate(self._headers):
            header = ttk.Label(
                self._table_frame,
                text=h.capitalize() if h != "remove" else "",
                font=("Segoe UI", 10, "bold"),
            )
            header.grid(row=0, column=idx, sticky="ew", padx=5, pady=5)

        for h in self._headers:
            self.body_widgets[h] = {}
            if h in ["bid", "ask"]:
                self.body_widgets[h + "_var"] = {}

    def add_symbol(self, symbol: str):
        if not symbol or symbol in self.watched_symbols:
            return

        self.watched_symbols.add(symbol)
        b_index = self._body_index

        self.body_widgets["symbol"][b_index] = ttk.Label(
            self._table_frame, text=symbol, font=("Segoe UI", 10)
        )
        self.body_widgets["symbol"][b_index].grid(row=b_index, column=0, padx=5, pady=2)

        self.body_widgets["exchange"][b_index] = ttk.Label(
            self._table_frame, text="Binance", font=("Segoe UI", 10)
        )
        self.body_widgets["exchange"][b_index].grid(row=b_index, column=1, padx=5, pady=2)

        self.body_widgets["bid_var"][b_index] = tk.StringVar(value="Loading...")
        self.body_widgets["bid"][b_index] = ttk.Label(
            self._table_frame,
            textvariable=self.body_widgets["bid_var"][b_index],
            font=("Segoe UI", 10),
        )
        self.body_widgets["bid"][b_index].grid(row=b_index, column=2, padx=5, pady=2)

        self.body_widgets["ask_var"][b_index] = tk.StringVar(value="Loading...")
        self.body_widgets["ask"][b_index] = ttk.Label(
            self._table_frame,
            textvariable=self.body_widgets["ask_var"][b_index],
            font=("Segoe UI", 10),
        )
        self.body_widgets["ask"][b_index].grid(row=b_index, column=3, padx=5, pady=2)

        self.body_widgets["remove"][b_index] = ttk.Button(
            self._table_frame,
            text="X",
            width=3,
            command=lambda idx=b_index: self._remove_symbol(idx),
        )
        self.body_widgets["remove"][b_index].grid(row=b_index, column=4, padx=5, pady=2)

        self._body_index += 1
        self.logic.fetch_symbol_data(symbol, self._update_symbol_data)

    def _update_symbol_data(self, symbol: str, ticker: dict):
        for b_index, widget in self.body_widgets["symbol"].items():
            if widget.cget("text") == symbol:
                bid_price = float(ticker.get("bidPrice", 0))
                ask_price = float(ticker.get("askPrice", 0))

                precision = (
                    8 if bid_price < 10 else (6 if bid_price < 100 else (4 if bid_price < 1000 else 2))
                )

                bid_str = f"{bid_price:.{precision}f}" if bid_price > 0 else "N/A"
                ask_str = f"{ask_price:.{precision}f}" if ask_price > 0 else "N/A"

                self.body_widgets["bid_var"][b_index].set(bid_str)
                self.body_widgets["ask_var"][b_index].set(ask_str)
                break

    def _remove_symbol(self, b_index: int):
        symbol = self.body_widgets["symbol"][b_index].cget("text")

        if symbol in self.watched_symbols:
            self.watched_symbols.remove(symbol)

        for h in self._headers:
            self.body_widgets[h][b_index].grid_forget()
            del self.body_widgets[h][b_index]

        if "bid_var" in self.body_widgets and b_index in self.body_widgets["bid_var"]:
            del self.body_widgets["bid_var"][b_index]

        if "ask_var" in self.body_widgets and b_index in self.body_widgets["ask_var"]:
            del self.body_widgets["ask_var"][b_index]

        logger.info(f"Removed {symbol} from watchlist")
