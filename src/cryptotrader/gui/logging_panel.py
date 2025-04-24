# src/cryptotrader/gui/logging_panel.py
import tkinter as tk
from datetime import datetime
from .styling import *

class LoggingPanel(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.txt = tk.Text(self, height=10, width=60, state=tk.DISABLED,
                           bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
        self.txt.pack(side=tk.TOP)

    def add_log(self, msg: str):
        self.txt.configure(state=tk.NORMAL)
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        self.txt.insert("end", f"{timestamp} :: {msg}\n")
        self.txt.configure(state=tk.DISABLED)