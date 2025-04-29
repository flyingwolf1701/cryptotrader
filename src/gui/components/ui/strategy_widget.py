import tkinter as tk
from tkinter import ttk
from src.gui.components.logic.strategy_logic import StrategyLogic
from src.gui.components.ui.symbol_search_widget import SymbolSearchWidget

class StrategyWidget(ttk.Frame):
    """UI component for managing and viewing trading strategies."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        self.logic = StrategyLogic()
        self.symbol_search: SymbolSearchWidget = None

        self._init_ui()

    def _init_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.add_btn = ttk.Button(
            controls_frame, text="Add Strategy", command=self._add_strategy_row
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)

        self.symbol_search = SymbolSearchWidget(
            controls_frame,
            on_select=self._on_symbol_selected,
            width=20
        )
        self.symbol_search.pack(side=tk.LEFT, padx=5)

        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        columns = ("strategy", "symbol", "timeframe", "balance_pct", "tp_pct", "sl_pct", "status")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.table.heading(col, text=col.capitalize())
            self.table.column(col, anchor="center")

        self.table.pack(fill=tk.BOTH, expand=True)

    def _add_strategy_row(self):
        row_id = len(self.logic.active_strategies)
        data = self.logic.add_strategy(row_id)

        self.table.insert("", "end", iid=row_id, values=(
            data["strategy_type"],
            data["symbol"],
            data["timeframe"],
            data["balance_pct"],
            data["tp_pct"],
            data["sl_pct"],
            data["status"]
        ))

    def _on_symbol_selected(self, symbol: str):
        """Set selected symbol for new strategies."""
        self.logic.set_available_symbols([symbol])

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        for row_id, data in self.logic.active_strategies.items():
            self.table.insert("", "end", iid=row_id, values=(
                data["strategy_type"],
                data["symbol"],
                data["timeframe"],
                data["balance_pct"],
                data["tp_pct"],
                data["sl_pct"],
                data["status"]
            ))

    def clear_strategies(self):
        self.logic.active_strategies.clear()
        self.logic.strategy_parameters.clear()
        self.refresh_table()
