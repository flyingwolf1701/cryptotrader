"""
Watchlist Component

Displays current market prices for selected cryptocurrency pairs.
Allows adding and removing symbols from the watchlist.
"""

import tkinter as tk
from tkinter import ttk
from functools import partial
from typing import Dict, Set, List, Callable, Any, Optional, Union, cast

from src.cryptotrader.config import get_logger
from src.cryptotrader.gui.components.styles import Colors, create_table, create_button

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    """Widget for displaying cryptocurrency price information."""

    def __init__(self, parent: tk.Widget, market_client: Any):
        super().__init__(parent)

        self.market_client: Any = market_client
        self.available_symbols: List[str] = []
        self.watched_symbols: Set[str] = set()
        self.price_data: Dict[str, Any] = {}
        self.symbol_selected_callback: Optional[Callable[[str], None]] = None
        self.button_refs: Dict[str, ttk.Button] = {}

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Add symbol controls at the top
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Symbol selector
        ttk.Label(controls_frame, text="Symbol:").pack(side=tk.LEFT, padx=(0, 5))

        self.symbol_var = tk.StringVar()
        self.symbol_selector = ttk.Combobox(
            controls_frame, textvariable=self.symbol_var, width=15
        )
        self.symbol_selector.pack(side=tk.LEFT, padx=(0, 5))

        # Add button
        self.add_button = ttk.Button(
            controls_frame, text="Add Symbol", command=self.add_selected_symbol
        )
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))

        # Create table for price data (without Remove column)
        table_columns = ["Symbol", "Price", "24h Change", "Volume"]
        table_frame, self.table = create_table(
            self, table_columns, height=8, column_widths=[100, 100, 100, 100]
        )
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create a frame for remove buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.grid(row=1, column=1, sticky="ns", padx=(0, 5), pady=5)

        # Initialize button references dictionary
        self.button_refs = {}

        # Bind click event for symbol selection
        self.table.bind("<ButtonRelease-1>", self.on_table_click)

    def set_available_symbols(self, symbols):
        """Set the list of available trading symbols."""
        self.available_symbols = sorted(symbols)
        self.symbol_selector["values"] = self.available_symbols

    def add_selected_symbol(self):
        """Add the currently selected symbol to the watchlist."""
        symbol = self.symbol_var.get().strip().upper()
        self.add_symbol(symbol)

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

        # Add new row to table with empty data initially
        values = (symbol, "Loading...", "Loading...", "Loading...")
        item_id = self.table.insert("", "end", values=values, tags=(symbol,))

        # Create remove button
        remove_btn = ttk.Button(
            self.button_frame,
            text="Remove",
            command=lambda s=symbol: self.remove_symbol(s),
            width=8,
        )

        # Store the button reference
        if not hasattr(self, "button_refs"):
            self.button_refs = {}
        self.button_refs[symbol] = remove_btn

        # Need to update idletasks to ensure table has correct bbox
        self.update_idletasks()

        # Get row position (y-coordinate)
        try:
            bbox = self.table.bbox(item_id, "#0")
            if bbox:
                y_pos = bbox[1]
                # Place button at appropriate position
                remove_btn.place(x=0, y=y_pos, height=25)
            else:
                # Fallback if bbox not available
                rows = len(self.table.get_children())
                y_pos = (rows - 1) * 25  # Assuming each row is about 25px high
                remove_btn.place(x=0, y=y_pos, height=25)
        except:
            # Fallback position
            remove_btn.pack(pady=2)
            logger.warning(
                f"Could not position button for {symbol} properly, using pack instead"
            )

        # Fetch initial price data
        self.fetch_symbol_data(symbol)

        logger.info(f"Added {symbol} to watchlist")

    def remove_symbol(self, symbol):
        """Remove a symbol from the watchlist."""
        if symbol not in self.watched_symbols:
            return

        # Find and remove the row
        for item_id in self.table.get_children():
            if self.table.item(item_id)["values"][0] == symbol:
                self.table.delete(item_id)
                break

        # Remove from tracked symbols
        self.watched_symbols.remove(symbol)

        # Remove from price data
        if symbol in self.price_data:
            del self.price_data[symbol]

        # Remove button if it exists
        if hasattr(self, "button_refs") and symbol in self.button_refs:
            self.button_refs[symbol].destroy()
            del self.button_refs[symbol]

        logger.info(f"Removed {symbol} from watchlist")

    def fetch_symbol_data(self, symbol):
        """Fetch price data for a specific symbol."""
        try:
            # Get 24hr ticker data
            ticker = self.market_client.get_24h_stats(symbol)

            # Debug the returned object
            logger.info(f"Single ticker type for {symbol}: {type(ticker)}")
            logger.info(f"Single ticker dir: {dir(ticker)}")

            if ticker:
                try:
                    # Try to extract lastPrice as test
                    lastPrice = None
                    if hasattr(ticker, "lastPrice"):
                        lastPrice = ticker.lastPrice
                        logger.info(f"Found lastPrice as attribute: {lastPrice}")
                    elif hasattr(ticker, "get") and callable(ticker.get):
                        lastPrice = ticker.get("lastPrice")
                        logger.info(f"Found lastPrice via get method: {lastPrice}")
                    elif hasattr(ticker, "__getitem__"):
                        lastPrice = ticker["lastPrice"]
                        logger.info(f"Found lastPrice via __getitem__: {lastPrice}")
                    else:
                        logger.error(f"Could not find lastPrice in ticker: {ticker}")
                except Exception as inner_e:
                    logger.error(
                        f"Error extracting lastPrice from ticker: {str(inner_e)}"
                    )

                # Update UI with ticker data (our update_symbol_data should handle the format)
                self.update_symbol_data(symbol, ticker)
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            # Try to update with placeholder data to avoid empty cells
            for item_id in self.table.get_children():
                if self.table.item(item_id)["values"][0] == symbol:
                    self.table.item(item_id, values=(symbol, "N/A", "N/A", "N/A"))
                    break

    def update_symbol_data(self, symbol, ticker_data):
        """Update the UI with new ticker data."""
        # Store the data
        self.price_data[symbol] = ticker_data

        # Get values needed for the UI - with extensive error handling
        price = 0
        change_pct = 0
        volume = 0

        try:
            # Try multiple approaches to extract the data we need
            # Method 1: Object attributes
            if (
                hasattr(ticker_data, "lastPrice")
                and hasattr(ticker_data, "priceChangePercent")
                and hasattr(ticker_data, "volume")
            ):
                price = float(ticker_data.lastPrice)
                change_pct = float(ticker_data.priceChangePercent)
                volume = float(ticker_data.volume)
                logger.info(
                    f"Extracted data via attributes for {symbol}: {price}, {change_pct}, {volume}"
                )

            # Method 2: Dictionary access with get
            elif hasattr(ticker_data, "get") and callable(getattr(ticker_data, "get")):
                price = float(ticker_data.get("lastPrice", 0))
                change_pct = float(ticker_data.get("priceChangePercent", 0))
                volume = float(ticker_data.get("volume", 0))
                logger.info(
                    f"Extracted data via get() for {symbol}: {price}, {change_pct}, {volume}"
                )

            # Method 3: Dictionary-style access
            elif hasattr(ticker_data, "__getitem__"):
                price = float(ticker_data["lastPrice"])
                change_pct = float(ticker_data["priceChangePercent"])
                volume = float(ticker_data["volume"])
                logger.info(
                    f"Extracted data via __getitem__ for {symbol}: {price}, {change_pct}, {volume}"
                )

            # Method 4: Access via __dict__
            elif hasattr(ticker_data, "__dict__"):
                dict_data = ticker_data.__dict__
                price = float(dict_data.get("lastPrice", 0))
                change_pct = float(dict_data.get("priceChangePercent", 0))
                volume = float(dict_data.get("volume", 0))
                logger.info(
                    f"Extracted data via __dict__ for {symbol}: {price}, {change_pct}, {volume}"
                )

            else:
                # Last resort - try to parse the string representation
                ticker_str = str(ticker_data)
                logger.warning(
                    f"Could not access ticker data attributes for {symbol}, trying string parsing"
                )
                logger.warning(f"Ticker string: {ticker_str}")

                # Default values
                price = 0
                change_pct = 0
                volume = 0

        except Exception as e:
            logger.error(f"Error extracting ticker data for {symbol}: {str(e)}")
            # Use default values
            price = 0
            change_pct = 0
            volume = 0

        # Format the values for display
        price_str = f"{price:.8f}" if price > 0 else "N/A"
        change_str = f"{change_pct:.2f}%" if change_pct != 0 else "0.00%"
        volume_str = f"{volume:.2f}" if volume > 0 else "N/A"

        # Find the row in the table and update it
        for item_id in self.table.get_children():
            values = self.table.item(item_id)["values"]
            if values and values[0] == symbol:
                # Update values
                self.table.item(
                    item_id, values=(symbol, price_str, change_str, volume_str)
                )

                # Configure tag for price change color
                tag_name = f"{symbol}_change"
                if change_pct > 0:
                    self.table.tag_configure(tag_name, foreground=Colors.SUCCESS)
                elif change_pct < 0:
                    self.table.tag_configure(tag_name, foreground=Colors.ERROR)

                self.table.item(item_id, tags=(tag_name,))
                break

    def update_prices(self) -> bool:
        """Update price data for all watched symbols.

        Returns:
            bool: True if update succeeded, False if it failed
        """
        if not self.watched_symbols:
            return True

        try:
            # We can fetch all tickers in one call for efficiency
            tickers = self.market_client.get_24h_stats(
                symbol=None
            )  # None fetches all tickers

            if tickers:
                # Debug the returned object type
                first_ticker = tickers[0] if isinstance(tickers, list) else tickers
                logger.info(f"Ticker type: {type(first_ticker)}")
                logger.info(f"Ticker dir: {dir(first_ticker)}")

                # Check if it's a PriceStats object
                if str(type(first_ticker)).find("PriceStats") >= 0:
                    # Direct debug of a PriceStats object to see what's in it
                    logger.info(
                        f"PriceStats object found, attributes: {dir(first_ticker)}"
                    )
                    logger.info(f"PriceStats repr: {repr(first_ticker)}")

                    # Try getting values directly
                    # Try to read properties - check for any potential getters
                    for attr_name in dir(first_ticker):
                        if not attr_name.startswith("_"):  # Skip private attrs
                            try:
                                attr_value = getattr(first_ticker, attr_name)
                                if not callable(attr_value):  # Skip methods
                                    logger.info(f"Attribute {attr_name} = {attr_value}")
                            except Exception as attr_e:
                                logger.error(
                                    f"Error reading attribute {attr_name}: {str(attr_e)}"
                                )

                # Process each ticker in the response
                if isinstance(tickers, list):
                    updated_count = 0
                    for ticker in tickers:
                        # Try different ways to get the symbol
                        symbol = None
                        try:
                            if hasattr(ticker, "symbol"):
                                symbol = ticker.symbol
                            elif hasattr(ticker, "__getitem__"):
                                symbol = ticker["symbol"]
                            elif hasattr(ticker, "__dict__"):
                                symbol = ticker.__dict__.get("symbol")

                            # Only update if it's in our watchlist
                            if symbol and symbol in self.watched_symbols:
                                self.update_symbol_data(symbol, ticker)
                                updated_count += 1
                        except Exception as e:
                            logger.error(f"Error processing ticker: {str(e)}")

                    logger.info(f"Updated {updated_count} symbols in watchlist")
                    return updated_count > 0
                else:
                    logger.warning(f"Expected list of tickers, got: {type(tickers)}")
                    return False
            return False  # No tickers received
        except Exception as e:
            logger.error(f"Error updating prices: {str(e)}")
            return False

    def on_table_click(self, event):
        """Handle table item clicks.

        When a row is clicked, emit the symbol selected signal.
        """
        # Check if we have any items
        if not self.table.get_children():
            return

        region = self.table.identify("region", event.x, event.y)
        if region == "cell":
            item_id = self.table.identify_row(event.y)
            if not item_id:  # No item at this position
                return

            column = self.table.identify_column(event.x)

            # If not clicking the "Remove" column
            if column != "#5":
                values = self.table.item(item_id)["values"]
                if values and len(values) > 0:
                    symbol = values[0]
                    logger.info(f"Selected symbol: {symbol}")

                    # Call the callback with the selected symbol
                    if self.symbol_selected_callback:
                        self.symbol_selected_callback(symbol)

                    # Also update the symbol selector to match
                    if symbol in self.available_symbols:
                        self.symbol_selector.set(symbol)
