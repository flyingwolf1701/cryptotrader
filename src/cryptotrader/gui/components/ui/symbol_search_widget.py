# File: src/gui/components/ui/symbol_search_widget.py
"""
Tkinter widget for searching/selecting trading symbols, wired to SymbolSearchLogic.
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Callable

from cryptotrader.gui.components.logic.symbol_search_logic import SymbolSearchLogic
from cryptotrader.gui.components.styles import Colors


class SymbolSearchWidget(ttk.Frame):
    """UI component for symbol search with dropdown and Add button."""
    def __init__(
        self,
        parent: tk.Widget,
        on_select: Optional[Callable[[str], None]] = None,
        on_add: Optional[Callable[[str], None]] = None,
        width: int = 25,
        show_add_button: bool = True,
        max_displayed: int = 10,
        client=None
    ):
        super().__init__(parent)
        self.on_select = on_select
        self.on_add = on_add
        self.width = width
        self.show_add_button = show_add_button
        self.max_displayed = max_displayed

        # Logic
        self.logic = SymbolSearchLogic(client)
        self.logic.initialize()

        # Build UI
        self._build_ui()

                # Register filtered-symbols listener (marshal to main thread)
        self._filtered_cb = lambda syms: self.after(0, self._update_dropdown, syms)
        self.logic.register_filtered_symbols_listener(self._filtered_cb)
        # Also register full-symbols listener to initialize dropdown with all symbols
        self.logic.register_symbols_listener(lambda syms: self.after(0, self._update_dropdown, syms))

        # Perform an initial filter to populate dropdown (all symbols)
        self.logic.filter_symbols("")

        # Cleanup on destroy
        self.bind('<Destroy>', self._on_destroy)

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_search_changed)
        self.search_entry = ttk.Entry(frame, textvariable=self.search_var, width=self.width)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.search_entry.bind('<KeyRelease>', self._show_dropdown)
        self.search_entry.bind('<Down>', self._on_down)
        self.search_entry.bind('<Return>', self._on_return)
        self.search_entry.bind('<Escape>', self._on_escape)
        self.search_entry.bind('<FocusIn>', self._show_dropdown)
        self.search_entry.bind('<FocusOut>', self._on_focus_out)

        if self.show_add_button:
            self.add_button = ttk.Button(frame, text='Add', command=self._on_add)
            self.add_button.pack(side=tk.LEFT, padx=2)

        self.dropdown_frame = tk.Frame(self)
        self.dropdown = tk.Listbox(
            self.dropdown_frame,
            height=self.max_displayed,
            bg=Colors.BACKGROUND_LIGHT,
            fg=Colors.FOREGROUND,
            selectbackground=Colors.ACCENT,
            selectforeground='white',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=Colors.ACCENT
        )
        scrollbar = ttk.Scrollbar(self.dropdown_frame, orient='vertical', command=self.dropdown.yview)
        self.dropdown.config(yscrollcommand=scrollbar.set)
        self.dropdown.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dropdown.bind('<<ListboxSelect>>', self._on_dropdown_select)
        self.dropdown.bind('<Escape>', self._on_escape)

    def _on_search_changed(self, *_) -> None:
        text = self.search_var.get().upper()
        if self.search_var.get() != text:
            self.search_var.set(text)
            return
        self.logic.filter_symbols(text)
        if self.logic.filtered_symbols:
            self._show_dropdown()
        else:
            self._hide_dropdown()

    def _update_dropdown(self, symbols: List[str]) -> None:
        self.dropdown.delete(0, tk.END)
        for sym in symbols[:self.max_displayed]:
            self.dropdown.insert(tk.END, sym)
        self.dropdown.config(height=min(len(symbols), self.max_displayed))

    def _show_dropdown(self, event=None) -> None:
        """Show the dropdown list below the search entry."""
        if self.dropdown.size() == 0:
            return
        # Calculate position relative to the entry widget
        x = self.search_entry.winfo_x()
        y = self.search_entry.winfo_y() + self.search_entry.winfo_height()
        # Place dropdown_frame inside this widget
        self.dropdown_frame.place(x=x, y=y, width=self.search_entry.winfo_width())

    def _hide_dropdown(self) -> None:
        self.dropdown_frame.place_forget()

    def _on_dropdown_select(self, event) -> None:
        sel = self.dropdown.curselection()
        if not sel:
            return
        symbol = self.dropdown.get(sel[0])
        self.search_var.set(symbol)
        self._hide_dropdown()
        if self.on_select:
            self.on_select(symbol)

    def _on_add(self) -> None:
        symbol = self.search_var.get()
        if symbol in self.logic.available_symbols and self.on_add:
            self.on_add(symbol)
            self.search_var.set('')

    def _on_down(self, event) -> str:
        self._show_dropdown()
        if self.dropdown.size() > 0:
            self.dropdown.focus_set()
            self.dropdown.selection_set(0)
            self.dropdown.see(0)
        return 'break'

    def _on_return(self, event) -> str:
        if self.dropdown_frame.winfo_ismapped() and self.dropdown.size() > 0:
            if not self.dropdown.curselection():
                self.dropdown.selection_set(0)
            self._on_dropdown_select(event)
        elif self.show_add_button:
            self._on_add()
        return 'break'

    def _on_escape(self, event) -> str:
        self._hide_dropdown()
        self.search_entry.focus_set()
        return 'break'

    def _on_focus_out(self, event) -> None:
        self.after(100, self._hide_if_outside)

    def _hide_if_outside(self) -> None:
        if self.focus_get() not in (self.search_entry, self.dropdown):
            self._hide_dropdown()

    def _on_destroy(self, event) -> None:
        self.logic.unregister_filtered_symbols_listener(self._filtered_cb)
