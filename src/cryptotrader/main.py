import tkinter as tk
from connectors.binance_futures import BinanceFuturesClient

import logging

logger = logging.getlogger()

if __name__ == 'main':
  binance = BinanceFuturesClient(True)

  root = tk.Tk()

  root.mainloop






