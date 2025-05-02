# File: src/cryptotrader/gui/components/demos/watchlist_demo.py
"""
Demo runner for WatchlistWidget.

Run it with:
    python -m cryptotrader.gui.components.demos.watchlist_demo
"""

import tkinter as tk
from cryptotrader.gui.components.ui.watchlist_widget import WatchlistWidget

def main():
    root = tk.Tk()
    root.title("Watchlist Demo")
    root.geometry("600x400")

    watchlist = WatchlistWidget(root)
    watchlist.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
