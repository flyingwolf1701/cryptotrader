# src/cryptotrader/gui/watchlist.py
import tkinter as tk
from src.cryptotrader.services.binance import get_exchange_info, get_bid_ask
from .styling import *

class Watchlist(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        # Initial load of symbols
        info = get_exchange_info()
        self.symbols = [s['symbol'] for s in info['symbols']]

        # UI setup
        self._cmd_frame = tk.Frame(self, bg=BG_COLOR)
        self._cmd_frame.pack(side=tk.TOP)
        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        tk.Label(self._cmd_frame, text="Symbol:", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT).grid(row=0, column=0)
        self._entry = tk.Entry(self._cmd_frame, fg=FG_COLOR, bg=BG_COLOR_2, justify=tk.CENTER)
        self._entry.grid(row=1, column=0)
        self._entry.bind("<Return>", self._add_symbol)

        # Table headers
        headers = ["symbol", "bid", "ask", "remove"]
        for idx, h in enumerate(headers):
            tk.Label(self._table_frame, text=h.capitalize(), bg=BG_COLOR,
                     fg=FG_COLOR, font=BOLD_FONT).grid(row=0, column=idx)

        self.rows = {}  # index -> widgets
        self._row_index = 1
        self.after(1500, self._update_prices)

    def _add_symbol(self, event):
        sym = event.widget.get().upper()
        if sym in self.symbols:
            idx = self._row_index
            lbl = tk.Label(self._table_frame, text=sym, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
            lbl.grid(row=idx, column=0)
            bid_var = tk.StringVar()
            ask_var = tk.StringVar()
            tk.Label(self._table_frame, textvariable=bid_var, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT).grid(row=idx, column=1)
            tk.Label(self._table_frame, textvariable=ask_var, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT).grid(row=idx, column=2)
            rm = tk.Button(self._table_frame, text="X", command=lambda i=idx: self._remove_row(i))
            rm.grid(row=idx, column=3)
            self.rows[idx] = {'symbol': sym, 'bid_var': bid_var, 'ask_var': ask_var}
            self._row_index += 1
            event.widget.delete(0, tk.END)

    def _remove_row(self, idx):
        for widget in self.table_frame.grid_slaves(row=idx):
            widget.destroy()
        del self.rows[idx]

    def _update_prices(self):
        for idx, data in self.rows.items():
            price = get_bid_ask(data['symbol'])
            data['bid_var'].set(f"{price['bid']}")
            data['ask_var'].set(f"{price['ask']}")
        self.after(1500, self._update_prices)
