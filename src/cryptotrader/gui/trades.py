# src/cryptotrader/gui/trades.py
import tkinter as tk
from .styling import *

class TradesPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.body = {}
        headers = ["time", "symbol", "side", "qty", "status", "pnl"]
        self.table = tk.Frame(self, bg=BG_COLOR)
        self.table.pack(side=tk.TOP)
        for i, h in enumerate(headers):
            tk.Label(self.table, text=h.capitalize(), bg=BG_COLOR,
                     fg=FG_COLOR, font=BOLD_FONT).grid(row=0, column=i)
        self._row = 1

    def add_trade(self, data: dict):
        # data keys: time, symbol, side, qty, status, pnl
        for i, key in enumerate(["time","symbol","side","qty","status","pnl"]):
            tk.Label(self.table, text=data[key], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
                .grid(row=self._row, column=i)
        self._row += 1
