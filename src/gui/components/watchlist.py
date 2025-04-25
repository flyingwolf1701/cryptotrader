"""
Watchlist Component

Displays current market prices for selected cryptocurrency pairs.
Based on the simpler grid-based approach but updated to work with your architecture.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Any, Optional

from src.config import get_logger
from src.gui.components.styles import Colors

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    """Widget for displaying cryptocurrency price information."""

    def __init__(self, parent: tk.Widget, market_client: Any):
        super().__init__(parent)

        self.market_client = market_client
        self.available_symbols = []
        self.watched_symbols = set()
        self.price_data = {}
        self.symbol_selected_callback = None

        # Widget collections for dynamic management
        self.body_widgets = {}

        # Current index for body entries
        self._body_index = 1

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Configure self
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create command frame for inputs at top
        self._commands_frame = ttk.Frame(self)
        self._commands_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Create symbol label
        self._symbol_label = ttk.Label(
            self._commands_frame, text="Symbol", font=("Segoe UI", 10, "bold")
        )
        self._symbol_label.grid(row=0, column=0, padx=5, pady=2)

        # Create entry with dropdown
        self._symbol_var = tk.StringVar()
        self._symbol_entry = ttk.Combobox(
            self._commands_frame, textvariable=self._symbol_var
        )
        self._symbol_entry.grid(row=1, column=0, padx=5, pady=2)
        self._symbol_entry.bind("<Return>", self._add_symbol_from_entry)

        # Add button
        self._add_button = ttk.Button(
            self._commands_frame, text="Add", command=self._add_symbol_from_button
        )
        self._add_button.grid(row=1, column=1, padx=5, pady=2)

        # Create table frame
        self._table_frame = ttk.Frame(self)
        self._table_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure table grid
        for i in range(5):  # 5 columns
            self._table_frame.columnconfigure(i, weight=1)

        # Define headers
        self._headers = ["symbol", "exchange", "bid", "ask", "remove"]

        # Create header labels
        for idx, h in enumerate(self._headers):
            header = ttk.Label(
                self._table_frame,
                text=h.capitalize() if h != "remove" else "",
                font=("Segoe UI", 10, "bold"),
            )
            header.grid(row=0, column=idx, sticky="ew", padx=5, pady=5)

        # Initialize body widgets
        for h in self._headers:
            self.body_widgets[h] = {}
            if h in ["bid", "ask"]:
                self.body_widgets[h + "_var"] = {}

    def set_available_symbols(self, symbols):
        """Set the list of available trading symbols."""
        self.available_symbols = sorted(symbols)
        self._symbol_entry["values"] = self.available_symbols

    def _add_symbol_from_entry(self, event):
        """Add symbol from entry when Enter is pressed."""
        symbol = self._symbol_var.get().strip().upper()
        if (
            symbol
            and symbol in self.available_symbols
            and symbol not in self.watched_symbols
        ):
            self.add_symbol(symbol)
            self._symbol_var.set("")  # Clear entry

    def _add_symbol_from_button(self):
        """Add symbol when button is clicked."""
        symbol = self._symbol_var.get().strip().upper()
        if (
            symbol
            and symbol in self.available_symbols
            and symbol not in self.watched_symbols
        ):
            self.add_symbol(symbol)
            self._symbol_var.set("")  # Clear entry

    def add_symbol(self, symbol):
        """Add a symbol to the watchlist table."""
        if (
            not symbol
            or symbol in self.watched_symbols
            or symbol not in self.available_symbols
        ):
            return

        # Add to tracked symbols
        self.watched_symbols.add(symbol)

        # Get current body index
        b_index = self._body_index

        # Create symbol label
        self.body_widgets["symbol"][b_index] = ttk.Label(
            self._table_frame, text=symbol, font=("Segoe UI", 10)
        )
        self.body_widgets["symbol"][b_index].grid(row=b_index, column=0, padx=5, pady=2)

        # Create exchange label (always Binance in this case)
        self.body_widgets["exchange"][b_index] = ttk.Label(
            self._table_frame, text="Binance", font=("Segoe UI", 10)
        )
        self.body_widgets["exchange"][b_index].grid(
            row=b_index, column=1, padx=5, pady=2
        )

        # Create bid price label with variable
        self.body_widgets["bid_var"][b_index] = tk.StringVar(value="Loading...")
        self.body_widgets["bid"][b_index] = ttk.Label(
            self._table_frame,
            textvariable=self.body_widgets["bid_var"][b_index],
            font=("Segoe UI", 10),
        )
        self.body_widgets["bid"][b_index].grid(row=b_index, column=2, padx=5, pady=2)

        # Create ask price label with variable
        self.body_widgets["ask_var"][b_index] = tk.StringVar(value="Loading...")
        self.body_widgets["ask"][b_index] = ttk.Label(
            self._table_frame,
            textvariable=self.body_widgets["ask_var"][b_index],
            font=("Segoe UI", 10),
        )
        self.body_widgets["ask"][b_index].grid(row=b_index, column=3, padx=5, pady=2)

        # Create remove button
        self.body_widgets["remove"][b_index] = ttk.Button(
            self._table_frame,
            text="X",
            width=3,
            command=lambda idx=b_index: self._remove_symbol(idx),
        )
        self.body_widgets["remove"][b_index].grid(row=b_index, column=4, padx=5, pady=2)

        # Make rows clickable for symbol selection
        self.body_widgets["symbol"][b_index].bind(
            "<Button-1>", lambda e, s=symbol: self._on_symbol_click(s)
        )
        self.body_widgets["exchange"][b_index].bind(
            "<Button-1>", lambda e, s=symbol: self._on_symbol_click(s)
        )
        self.body_widgets["bid"][b_index].bind(
            "<Button-1>", lambda e, s=symbol: self._on_symbol_click(s)
        )
        self.body_widgets["ask"][b_index].bind(
            "<Button-1>", lambda e, s=symbol: self._on_symbol_click(s)
        )

        # Increment body index for next addition
        self._body_index += 1

        # Fetch initial price data
        self.fetch_symbol_data(symbol)

        logger.info(f"Added {symbol} to watchlist")

    def _remove_symbol(self, b_index):
        """Remove a symbol from the watchlist."""
        # Get symbol from the row
        symbol = self.body_widgets["symbol"][b_index].cget("text")

        # Remove from tracked symbols
        if symbol in self.watched_symbols:
            self.watched_symbols.remove(symbol)

        # Remove from price data
        if symbol in self.price_data:
            del self.price_data[symbol]

        # Remove all widgets in this row
        for h in self._headers:
            self.body_widgets[h][b_index].grid_forget()
            del self.body_widgets[h][b_index]

        # Also remove bid/ask variables
        if "bid_var" in self.body_widgets and b_index in self.body_widgets["bid_var"]:
            del self.body_widgets["bid_var"][b_index]

        if "ask_var" in self.body_widgets and b_index in self.body_widgets["ask_var"]:
            del self.body_widgets["ask_var"][b_index]

        logger.info(f"Removed {symbol} from watchlist")

    def _on_symbol_click(self, symbol):
        """Handle click on a symbol row."""
        if self.symbol_selected_callback:
            self.symbol_selected_callback(symbol)
            logger.info(f"Selected {symbol} from watchlist")

    def fetch_symbol_data(self, symbol):
        """Fetch price data for a specific symbol."""
        try:
            # Get ticker data
            ticker = self.market_client.get_24h_stats(symbol)

            if ticker:
                self.update_symbol_data(symbol, ticker)
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")

    def update_symbol_data(self, symbol, ticker_data):
        """Update the UI with new ticker data."""
        # Store the data
        self.price_data[symbol] = ticker_data

        # Extract bid and ask prices
        bid_price = 0
        ask_price = 0

        try:
            # Try to extract prices based on ticker data structure
            if (
                hasattr(ticker_data, "lastPrice")
                and hasattr(ticker_data, "askPrice")
                and hasattr(ticker_data, "bidPrice")
            ):
                bid_price = float(ticker_data.bidPrice)
                ask_price = float(ticker_data.askPrice)
            elif hasattr(ticker_data, "get") and callable(ticker_data.get):
                bid_price = float(ticker_data.get("bidPrice", 0))
                ask_price = float(ticker_data.get("askPrice", 0))
            elif hasattr(ticker_data, "__getitem__"):
                bid_price = float(ticker_data["bidPrice"])
                ask_price = float(ticker_data["askPrice"])
        except Exception as e:
            logger.error(f"Error extracting price data for {symbol}: {str(e)}")

        # Update UI - find the row for this symbol
        for b_index, symbol_widget in self.body_widgets["symbol"].items():
            if symbol_widget.cget("text") == symbol:
                # Determine precision based on price magnitude
                precision = (
                    8
                    if bid_price < 10
                    else (6 if bid_price < 100 else (4 if bid_price < 1000 else 2))
                )

                # Format and update prices
                bid_str = f"{bid_price:.{precision}f}" if bid_price > 0 else "N/A"
                ask_str = f"{ask_price:.{precision}f}" if ask_price > 0 else "N/A"

                self.body_widgets["bid_var"][b_index].set(bid_str)
                self.body_widgets["ask_var"][b_index].set(ask_str)
                break

    def update_prices(self) -> bool:
        """Update price data for all watched symbols.

        Returns:
            bool: True if update succeeded, False if it failed
        """
        if not self.watched_symbols:
            return True

        try:
            # Get all symbols data
            all_tickers = self.market_client.get_24h_stats(
                None
            )  # None fetches all tickers

            if all_tickers and isinstance(all_tickers, list):
                for ticker in all_tickers:
                    # Get symbol from ticker
                    symbol = None
                    try:
                        if hasattr(ticker, "symbol"):
                            symbol = ticker.symbol
                        elif hasattr(ticker, "__getitem__"):
                            symbol = ticker["symbol"]

                        # Update if it's a symbol we're watching
                        if symbol and symbol in self.watched_symbols:
                            self.update_symbol_data(symbol, ticker)
                    except Exception as e:
                        logger.error(f"Error processing ticker: {str(e)}")

                return True
            return False
        except Exception as e:
            logger.error(f"Error updating prices: {str(e)}")
            return False
