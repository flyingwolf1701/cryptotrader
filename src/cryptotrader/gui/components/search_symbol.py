"""
Symbol Search Component

A reusable component for searching and selecting trading symbols.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Set, Callable, Optional
import re
import threading
import os
import sys
from pathlib import Path

from config import get_logger
from cryptotrader.gui.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient
from cryptotrader.gui.components.styles import Colors

project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = get_logger(__name__)


class SymbolSearchLogic:
    """Business logic for symbol searching and filtering."""

    def __init__(self):
        """Initialize the symbol search logic."""
        self.client = BinanceRestUnifiedClient()
        self.available_symbols: List[str] = []
        self.filtered_symbols: List[str] = []
        self.on_symbols_updated: Set[Callable[[List[str]], None]] = set()
        self.on_filtered_symbols_updated: Set[Callable[[List[str]], None]] = set()
        self.is_initialized: bool = False

        # Fetch symbols asynchronously
        self._initialize_async()

    def _initialize_async(self):
        """Initialize symbol data asynchronously."""
        thread = threading.Thread(target=self._fetch_symbols)
        thread.daemon = True
        thread.start()

    def _fetch_symbols(self):
        """Fetch available symbols from the exchange."""
        try:
            # Get exchange info from system operations
            system_client = (
                self.client.system if hasattr(self.client, "system") else None
            )
            if system_client:
                exchange_info = system_client.getExchangeInfo()
            else:
                # Fallback to market client for exchange info
                exchange_info = self.client.market.getExchangeInfo()

            if exchange_info and "symbols" in exchange_info:
                symbols = [
                    symbol["symbol"]
                    for symbol in exchange_info["symbols"]
                    if symbol.get("status") == "TRADING"
                ]

                if symbols:
                    self.available_symbols = sorted(symbols)
                    self.filtered_symbols = self.available_symbols
                    self._notify_symbols_updated()
                    self._notify_filtered_symbols_updated()
                    self.is_initialized = True
                    logger.info(f"Loaded {len(symbols)} trading symbols")
                    return

            logger.warning("Failed to fetch symbols from exchange")
        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")

        # If we get here, there was an error - use fallback
        self.available_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        self.filtered_symbols = self.available_symbols
        self._notify_symbols_updated()
        self._notify_filtered_symbols_updated()
        self.is_initialized = True

    def filter_symbols(self, search_text: str):
        """Filter symbols based on search text."""
        if not search_text:
            self.filtered_symbols = self.available_symbols
        else:
            # Convert to uppercase for case-insensitive search
            search_text = search_text.upper()

            # First try exact match
            exact_matches = [s for s in self.available_symbols if search_text == s]
            if exact_matches:
                self.filtered_symbols = exact_matches
            else:
                # Then try contains match
                self.filtered_symbols = [
                    s for s in self.available_symbols if search_text in s
                ]

                # If still no matches, try searching for base currencies and quote currencies
                if not self.filtered_symbols:
                    # Split trading pairs into base and quote currency
                    # For example, BTCUSDT -> BTC (base) and USDT (quote)
                    base_matches = []
                    quote_matches = []

                    # Common quote currencies to help split the pairs correctly
                    quote_currencies = [
                        "USDT",
                        "BTC",
                        "ETH",
                        "BNB",
                        "BUSD",
                        "USD",
                        "EUR",
                    ]

                    for symbol in self.available_symbols:
                        # Find quote currency
                        quote = None
                        for q in quote_currencies:
                            if symbol.endswith(q):
                                quote = q
                                base = symbol[: -len(q)]
                                break

                        # If no known quote currency, assume last 3-4 chars
                        if not quote:
                            if len(symbol) > 4:
                                quote = symbol[-4:]
                                base = symbol[:-4]
                            else:
                                base = symbol[:-3]
                                quote = symbol[-3:]

                        # Check if search matches base or quote
                        if search_text in base:
                            base_matches.append(symbol)
                        elif search_text in quote:
                            quote_matches.append(symbol)

                    # Combine results, prioritizing base matches
                    self.filtered_symbols = base_matches + quote_matches

        self._notify_filtered_symbols_updated()

    def register_symbols_listener(self, callback: Callable[[List[str]], None]):
        """Register a listener for all symbols updates."""
        self.on_symbols_updated.add(callback)
        if self.is_initialized:
            callback(self.available_symbols)

    def unregister_symbols_listener(self, callback: Callable[[List[str]], None]):
        """Unregister a symbols listener."""
        if callback in self.on_symbols_updated:
            self.on_symbols_updated.remove(callback)

    def _notify_symbols_updated(self):
        """Notify listeners about symbols update."""
        for callback in self.on_symbols_updated:
            try:
                callback(self.available_symbols)
            except Exception as e:
                logger.error(f"Error notifying symbol listener: {str(e)}")

    def register_filtered_symbols_listener(self, callback: Callable[[List[str]], None]):
        """Register a listener for filtered symbols updates."""
        self.on_filtered_symbols_updated.add(callback)
        if self.is_initialized:
            callback(self.filtered_symbols)

    def unregister_filtered_symbols_listener(
        self, callback: Callable[[List[str]], None]
    ):
        """Unregister a filtered symbols listener."""
        if callback in self.on_filtered_symbols_updated:
            self.on_filtered_symbols_updated.remove(callback)

    def _notify_filtered_symbols_updated(self):
        """Notify listeners about filtered symbols update."""
        for callback in self.on_filtered_symbols_updated:
            try:
                callback(self.filtered_symbols)
            except Exception as e:
                logger.error(f"Error notifying filtered symbol listener: {str(e)}")

    def get_all_symbols(self) -> List[str]:
        """Get all available symbols."""
        return self.available_symbols

    def get_filtered_symbols(self) -> List[str]:
        """Get the filtered symbols."""
        return self.filtered_symbols


class SymbolSearchWidget(ttk.Frame):
    """Widget for searching and selecting trading symbols."""

    def __init__(
        self,
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        on_add: Optional[Callable[[str], None]] = None,
        width: int = 25,
        show_add_button: bool = True,
        max_displayed: int = 10,
    ):
        """Initialize the symbol search widget.

        Args:
            parent: Parent widget
            on_select: Callback when a symbol is selected
            on_add: Callback when a symbol is added (via Add button)
            width: Width of the search entry widget
            show_add_button: Whether to show the Add button
            max_displayed: Maximum number of symbols to display in dropdown
        """
        super().__init__(parent)

        self.on_select = on_select
        self.on_add = on_add
        self.width = width
        self.show_add_button = show_add_button
        self.max_displayed = max_displayed

        # Create the logic component
        self.logic = SymbolSearchLogic()

        # Initialize UI
        self.init_ui()

        # Register for symbol updates
        self.logic.register_filtered_symbols_listener(self._update_dropdown)

    def init_ui(self):
        """Initialize the UI components."""
        # Configure as a horizontal frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create a frame to hold the search entry and dropdown
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Create search entry with auto-completion
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_changed)

        self.search_entry = ttk.Entry(
            search_frame, textvariable=self.search_var, width=self.width
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Add keyboard event handlers
        self.search_entry.bind("<KeyRelease>", self._handle_key_release)
        self.search_entry.bind("<Down>", self._handle_down_key)
        self.search_entry.bind("<Return>", self._handle_return_key)
        self.search_entry.bind("<Escape>", self._handle_escape_key)

        # Create Add button if requested
        if self.show_add_button:
            self.add_button = ttk.Button(
                search_frame, text="Add", command=self._on_add_clicked
            )
            self.add_button.pack(side=tk.LEFT, padx=2)

        # Listbox for dropdown (not yet visible)
        self.dropdown_frame = tk.Frame(self)

        self.dropdown = tk.Listbox(
            self.dropdown_frame,
            height=self.max_displayed,
            bg=Colors.BACKGROUND_LIGHT,
            fg=Colors.FOREGROUND,
            selectbackground=Colors.ACCENT,
            selectforeground="white",
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=Colors.ACCENT,
        )
        self.dropdown.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar for dropdown
        dropdown_scroll = ttk.Scrollbar(
            self.dropdown_frame, orient="vertical", command=self.dropdown.yview
        )
        dropdown_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.dropdown.config(yscrollcommand=dropdown_scroll.set)

        # Bind listbox selection event
        self.dropdown.bind("<<ListboxSelect>>", self._on_dropdown_select)
        self.dropdown.bind("<Escape>", self._handle_escape_key)

        # Custom popup handling
        self.search_entry.bind("<FocusIn>", self._show_dropdown)
        self.search_entry.bind("<FocusOut>", self._on_focus_out)
        self.dropdown.bind("<FocusOut>", self._on_focus_out)

    def _on_search_changed(self, *args):
        """Handle search text changes."""
        search_text = self.search_var.get()

        # Convert to uppercase for consistency
        if search_text and not search_text.isupper():
            # Only modify if the text is not already uppercase
            # to avoid an infinite loop from trace events
            self.search_var.set(search_text.upper())
            return

        # Filter symbols
        self.logic.filter_symbols(search_text)

        # Show dropdown if we have search results
        if self.logic.get_filtered_symbols():
            self._show_dropdown()
        else:
            self._hide_dropdown()

    def _update_dropdown(self, symbols: List[str]):
        """Update dropdown list with symbols."""
        # Clear current items
        self.dropdown.delete(0, tk.END)

        # Add filtered symbols, limiting to max_displayed
        display_symbols = symbols[: self.max_displayed]
        for symbol in display_symbols:
            self.dropdown.insert(tk.END, symbol)

        # Update dropdown size
        visible_count = min(len(display_symbols), self.max_displayed)
        if visible_count > 0:
            self.dropdown.config(height=visible_count)

    def _show_dropdown(self, event=None):
        """Show the dropdown list."""
        # Only show if we have items
        if self.dropdown.size() > 0:
            # Calculate position beneath the entry widget
            x = self.search_entry.winfo_rootx()
            y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height()

            # Set position and make visible
            self.dropdown_frame.place(
                x=0,
                y=self.search_entry.winfo_height(),
                width=self.search_entry.winfo_width(),
                relwidth=1,
            )

    def _hide_dropdown(self):
        """Hide the dropdown list."""
        self.dropdown_frame.place_forget()

    def _on_dropdown_select(self, event):
        """Handle selection from dropdown."""
        selection = self.dropdown.curselection()
        if selection:
            index = selection[0]
            symbol = self.dropdown.get(index)

            # Update search entry
            self.search_var.set(symbol)

            # Hide dropdown
            self._hide_dropdown()

            # Call select callback
            if self.on_select:
                self.on_select(symbol)

    def _on_add_clicked(self):
        """Handle add button click."""
        symbol = self.search_var.get()

        # Validate symbol
        if symbol and symbol in self.logic.get_all_symbols():
            # Call add callback
            if self.on_add:
                self.on_add(symbol)

            # Clear search field
            self.search_var.set("")

    def _handle_key_release(self, event):
        """Handle key release events for custom behavior."""
        # Show dropdown when typing (unless it's already visible)
        if not event.keysym in ("Down", "Return", "Escape"):
            self._show_dropdown()

    def _handle_down_key(self, event):
        """Handle down arrow key to navigate to dropdown."""
        # Show dropdown if not visible
        self._show_dropdown()

        # Focus on listbox and select first item
        if self.dropdown.size() > 0:
            self.dropdown.focus_set()
            self.dropdown.selection_set(0)
            self.dropdown.see(0)
            return "break"  # Prevent default behavior

    def _handle_return_key(self, event):
        """Handle Return key press to select or add current value."""
        symbol = self.search_var.get()

        # If dropdown is visible with items, select first
        if self.dropdown_frame.winfo_viewable() and self.dropdown.size() > 0:
            # If nothing is selected, select the first item
            if not self.dropdown.curselection() and self.dropdown.size() > 0:
                symbol = self.dropdown.get(0)
                self.search_var.set(symbol)

            # Hide dropdown
            self._hide_dropdown()

            # Call select callback
            if self.on_select:
                self.on_select(symbol)

        # If no dropdown or empty, try to add the symbol
        elif self.show_add_button and symbol and symbol in self.logic.get_all_symbols():
            if self.on_add:
                self.on_add(symbol)
                self.search_var.set("")  # Clear input after adding

        return "break"  # Prevent default behavior

    def _handle_escape_key(self, event):
        """Handle Escape key to dismiss dropdown."""
        self._hide_dropdown()
        self.search_entry.focus_set()
        return "break"  # Prevent default behavior

    def _on_focus_out(self, event):
        """Handle focus leaving the widget."""
        # Check if focus went to the dropdown or search entry to avoid hiding
        if (
            event.widget == self.search_entry and self.focus_get() == self.dropdown
        ) or (event.widget == self.dropdown and self.focus_get() == self.search_entry):
            return

        # Hide dropdown after a short delay
        # (allows click events to register first)
        self.after(100, self._check_focus_and_hide)

    def _check_focus_and_hide(self):
        """Check if focus is still outside the widget and hide dropdown if so."""
        if self.focus_get() != self.search_entry and self.focus_get() != self.dropdown:
            self._hide_dropdown()

    def get_selected_symbol(self) -> str:
        """Get the currently selected symbol."""
        return self.search_var.get()

    def set_selected_symbol(self, symbol: str):
        """Set the selected symbol."""
        self.search_var.set(symbol)

    def __del__(self):
        """Clean up resources."""
        # Unregister listeners when widget is destroyed
        if hasattr(self, "logic"):
            self.logic.unregister_filtered_symbols_listener(self._update_dropdown)
