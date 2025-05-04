"""
This file contains a lot of files that are standalone components but are condensed here for AI
"""
#------------------------------------------------------------------------------------------------
#src\cryptotrader\gui\components\ui\logging_widget.py
#------------------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk
from cryptotrader.gui.components.logic.logging_logic import LoggingLogic
from cryptotrader.gui.components.styles import Colors

class LoggingWidget(ttk.Frame):
    """UI component for displaying application logs."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)

        self.logic = LoggingLogic()
        self._init_ui()

    def _init_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        log_frame = ttk.Frame(self)
        log_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.log_view = tk.Text(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            background=Colors.BACKGROUND,
            foreground=Colors.FOREGROUND,
            font=("Courier New", 10)
        )

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_view.yview)
        self.log_view.configure(yscrollcommand=scrollbar.set)

        self.log_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.clear_btn = ttk.Button(
            button_frame, text="Clear Logs", command=self.clear_logs
        )
        self.clear_btn.pack(side=tk.RIGHT)

        self._configure_tags()
        self.add_log("Logging system initialized.")

    def _configure_tags(self):
        self.log_view.tag_configure("INFO", foreground="white")
        self.log_view.tag_configure("ERROR", foreground=Colors.ERROR)
        self.log_view.tag_configure("WARNING", foreground=Colors.WARNING)
        self.log_view.tag_configure("SUCCESS", foreground=Colors.SUCCESS)

    def add_log(self, message: str, level: str = "INFO"):
        log_entry = self.logic.add_log(message, level)
        formatted = f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}\n"

        self.log_view.insert(tk.END, formatted, log_entry["level"])
        self.log_view.see(tk.END)

    def clear_logs(self):
        self.logic.clear_logs()
        self.log_view.delete(1.0, tk.END)
        self.add_log("Logs cleared.")


#------------------------------------------------------------------------------------------------
#src\cryptotrader\gui\components\ui\strategy_widget.py
#------------------------------------------------------------------------------------------------
# File: src/cryptotrader/gui/components/ui/strategy_widget.py
"""
Strategy Widget

UI component for managing and viewing trading strategies.
"""

import tkinter as tk
from tkinter import ttk
from cryptotrader.config import get_logger
from cryptotrader.gui.components.logic.strategy_logic import StrategyLogic

logger = get_logger(__name__)

class StrategyWidget(ttk.Frame):
    """UI component for managing and viewing trading strategies."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.logic = StrategyLogic()
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

        table_frame = ttk.Frame(self)
        table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        columns = (
            "strategy",
            "symbol",
            "timeframe",
            "balance_pct",
            "tp_pct",
            "sl_pct",
            "status",
        )
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col in columns:
            self.table.heading(col, text=col.capitalize())
            self.table.column(col, anchor="center")
        self.table.pack(fill=tk.BOTH, expand=True)

    def _add_strategy_row(self):
        row_id = len(self.logic.active_strategies)
        data = self.logic.add_strategy(row_id)
        self.table.insert(
            "",
            "end",
            iid=row_id,
            values=(
                data["strategy_type"],
                data["symbol"],
                data["timeframe"],
                data["balance_pct"],
                data["tp_pct"],
                data["sl_pct"],
                data["status"],
            ),
        )

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        for row_id, data in self.logic.active_strategies.items():
            self.table.insert(
                "",
                "end",
                iid=row_id,
                values=(
                    data["strategy_type"],
                    data["symbol"],
                    data["timeframe"],
                    data["balance_pct"],
                    data["tp_pct"],
                    data["sl_pct"],
                    data["status"],
                ),
            )

    def clear_strategies(self):
        self.logic.active_strategies.clear()
        self.logic.strategy_parameters.clear()
        self.refresh_table()


#------------------------------------------------------------------------------------------------
#src\cryptotrader\gui\components\ui\trade_history_widget.py
#------------------------------------------------------------------------------------------------
# File: src/cryptotrader/gui/components/ui/trade_history_widget.py
#!/usr/bin/env python3
"""
TradeHistoryWidget

Displays executed trades in a grid layout with add, clear, and mock methods.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import typing

from cryptotrader.config import get_logger
from cryptotrader.gui.components.styles import Colors
from cryptotrader.gui.components.logic.trade_history_logic import TradeHistoryLogic

logger = get_logger(__name__)

class TradeHistoryWidget(ttk.Frame):
    """UI component for displaying historical trades and PNL."""

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        self.logic = TradeHistoryLogic()
        self.trades: typing.List[dict] = []

        self._init_ui()
        # Optionally populate with mock trades:
        # self.add_mock_trades()

    def _init_ui(self):
        """Initialize UI: header, table, scrollbar, and buttons."""
        # Header
        header = ttk.Frame(self)
        header.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        ttk.Label(header, text="Trades", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        clear_btn = ttk.Button(header, text="Clear", command=self.clear_trades)
        clear_btn.pack(side=tk.RIGHT)

        # Treeview for trades
        columns = ("time", "symbol", "strategy", "side", "price", "quantity", "status")
        self.trades_tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        self.trades_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.trades_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.trades_tree.configure(yscrollcommand=scrollbar.set)

        # Configure columns and headings
        widths = {
            "time": 150, "symbol": 100, "strategy": 100,
            "side": 80, "price": 120, "quantity": 100, "status": 100
        }
        for col in columns:
            self.trades_tree.heading(col, text=col.capitalize())
            self.trades_tree.column(col, width=widths[col], anchor=tk.CENTER)

        # Color tags
        self.trades_tree.tag_configure("buy", foreground=Colors.BUY)
        self.trades_tree.tag_configure("sell", foreground=Colors.SELL)

    def add_trade(self, data: typing.Dict):
        """
        Add a single trade record to the treeview.
        """
        # Format timestamp
        ts = data.get("time", "")
        if isinstance(ts, (int, float)):
            ts = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")

        # Format price & quantity
        price = data.get("price", 0)
        price_str = f"{float(price):.8f}" if isinstance(price, (int, float)) else str(price)
        qty = data.get("quantity", 0)
        qty_str = f"{float(qty):.8f}" if isinstance(qty, (int, float)) else str(qty)

        values = (
            ts,
            data.get("symbol", "N/A"),
            data.get("strategy", "Manual"),
            data.get("side", "BUY"),
            price_str,
            qty_str,
            data.get("status", "FILLED"),
        )
        tag = "buy" if data.get("side", "BUY") == "BUY" else "sell"
        self.trades_tree.insert("", "end", values=values, tags=(tag,))

        logger.info(f"Added trade: {data.get('symbol')} {data.get('side')}")

    def clear_trades(self):
        """Clear all entries from the treeview."""
        for item in self.trades_tree.get_children():
            self.trades_tree.delete(item)
        logger.info("Cleared all trades")

    def add_mock_trades(self, count: int = 10):
        """
        Populate the treeview with mock trades for testing.
        """
        import time, random

        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT"]
        strategies = ["Breakout", "MACD", "Manual", "Grid"]
        sides = ["BUY", "SELL"]
        statuses = ["FILLED", "PARTIALLY_FILLED", "CANCELED"]

        for _ in range(count):
            trade = {
                "time": int(time.time() * 1000) - random.randint(0, 1_000_000),
                "symbol": random.choice(symbols),
                "strategy": random.choice(strategies),
                "side": random.choice(sides),
                "price": random.uniform(100, 50_000),
                "quantity": random.uniform(0.01, 2),
                "status": random.choice(statuses),
            }
            self.add_trade(trade)


#------------------------------------------------------------------------------------------------
#src\cryptotrader\gui\components\ui\watchlist_widget.py
#------------------------------------------------------------------------------------------------
# File: src/cryptotrader/gui/components/ui/watchlist_widget.py
"""
Watchlist Widget

Displays selected cryptocurrency pairs with live bid/ask updates.
Symbol entry, exchange selector, and Add button are all here.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

from cryptotrader.config import get_logger
from cryptotrader.gui.components.logic.watchlist_logic import WatchlistLogic
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient
from cryptotrader.gui.app_styles import Colors, StyleNames, create_button

logger = get_logger(__name__)


class WatchlistWidget(ttk.Frame):
    """
    Watchlist Widget

    Displays selected cryptocurrency pairs with live bid/ask updates.
    Symbol entry, exchange selector, and Add button are all here.
    """

    def __init__(self, parent: tk.Widget):
        super().__init__(parent)
        # Apply themed frame style and padding
        self.configure(style='TFrame', padding=(10, 10))

        self.logger = logger
        self.unified_client = BinanceRestUnifiedClient()
        self.logic = WatchlistLogic(self.unified_client)

        # track symbols in insertion order
        self.watched_symbols: List[str] = []
        # map column/header → list of widgets or StringVars (for “Bid” and “Ask”)
        self.body_widgets: Dict[str, List] = {}
        self._headers = ["Symbol", "Bid", "Ask", "Remove"]
        # store after-job IDs so we can cancel when a symbol is removed
        self._refresh_jobs: Dict[str, str] = {}

        # Initialize UI
        self._init_ui()

    def set_available_symbols(self, symbols: List[str]) -> None:
        """
        Initialize the watchlist with a list of symbols.
        Clears any existing entries and adds the provided symbols.
        """
        # Remove all existing
        for sym in list(self.watched_symbols):
            self._remove_symbol(sym)
        # Add new in order
        for sym in symbols:
            self.symbol_var.set(sym)
            self._on_add()

    def _init_ui(self) -> None:
        # Configure grid
        for i in range(4):
            self.columnconfigure(i, weight=1)

        # Symbol entry
        self.symbol_var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.symbol_var, width=15)
        entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Exchange dropdown
        self.exchange_var = tk.StringVar(value="Binance")
        exch_combo = ttk.Combobox(
            self,
            textvariable=self.exchange_var,
            values=["Binance", "Crypto.com"],
            state="readonly",
            width=12,
        )
        exch_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Add button
        add_btn = create_button(
            self,
            text="Add to watchlist",
            command=self._on_add,
            style_name=StyleNames.SUCCESS_BUTTON
        )
        add_btn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Table headers
        for col, header in enumerate(self._headers):
            lbl = ttk.Label(
                self,
                text=header,
                font=("Segoe UI", 10, "bold"),
                foreground=Colors.FOREGROUND
            )
            lbl.grid(row=1, column=col, padx=5, pady=5)

    def _on_add(self) -> None:
        symbol = self.symbol_var.get().strip().upper()
        exchange = self.exchange_var.get()
        # only Binance supported
        if exchange != "Binance":
            messagebox.showerror(
                "Unsupported Exchange",
                f"Exchange {exchange} not supported."
            )
            return

        # Validate symbol
        all_syms = self.unified_client.get_binance_symbols()
        if symbol not in all_syms:
            messagebox.showerror(
                "Symbol Not Found",
                f"Couldn’t find {symbol} on {exchange}."
            )
            return
        if symbol in self.watched_symbols:
            return

        # Add row and start updates
        self.watched_symbols.append(symbol)
        self._add_row(symbol)
        self.symbol_var.set("")
        self._refresh_symbol(symbol)

    def _add_row(self, symbol: str) -> None:
        row = 2 + (len(self.watched_symbols) - 1)
        # Symbol
        lbl_sym = ttk.Label(self, text=symbol, foreground=Colors.FOREGROUND)
        lbl_sym.grid(row=row, column=0, padx=5, pady=2)
        self.body_widgets.setdefault("Symbol", []).append(lbl_sym)

        # Bid
        bid_var = tk.StringVar(value="N/A")
        lbl_bid = ttk.Label(self, textvariable=bid_var, foreground=Colors.FOREGROUND)
        lbl_bid.grid(row=row, column=1, padx=5, pady=2)
        self.body_widgets.setdefault("bid_var", []).append(bid_var)
        self.body_widgets.setdefault("Bid", []).append(lbl_bid)

        # Ask
        ask_var = tk.StringVar(value="N/A")
        lbl_ask = ttk.Label(self, textvariable=ask_var, foreground=Colors.FOREGROUND)
        lbl_ask.grid(row=row, column=2, padx=5, pady=2)
        self.body_widgets.setdefault("ask_var", []).append(ask_var)
        self.body_widgets.setdefault("Ask", []).append(lbl_ask)

        # Remove button
        btn_rm = create_button(
            self,
            text="Remove",
            command=lambda s=symbol: self._remove_symbol(s),
            style_name=StyleNames.DANGER_BUTTON
        )
        btn_rm.grid(row=row, column=3, padx=5, pady=2)
        self.body_widgets.setdefault("Remove", []).append(btn_rm)

    def _refresh_symbol(self, symbol: str) -> None:
        def callback(sym: str, data: dict) -> None:
            self._update_symbol_data(sym, data)
        self.logic.fetch_symbol_data(symbol, callback)
        job = self.after(5000, lambda: self._refresh_symbol(symbol))
        self._refresh_jobs[symbol] = job

    def _update_symbol_data(self, symbol: str, data: dict) -> None:
        try:
            idx = self.watched_symbols.index(symbol)
        except ValueError:
            return
        bid = data.get("bidPrice") or data.get("bid") or "N/A"
        ask = data.get("askPrice") or data.get("ask") or "N/A"
        self.body_widgets["bid_var"][idx].set(bid)
        self.body_widgets["ask_var"][idx].set(ask)

    def _remove_symbol(self, symbol: str) -> None:
        if symbol not in self.watched_symbols:
            return
        idx = self.watched_symbols.index(symbol)
        job = self._refresh_jobs.pop(symbol, None)
        if job:
            self.after_cancel(job)
        self.watched_symbols.pop(idx)
        for key, lst in list(self.body_widgets.items()):
            item = lst.pop(idx)
            if isinstance(item, (ttk.Label, ttk.Button)):
                item.grid_forget()
        logger.info(f"Removed {symbol} from watchlist")


#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\components\logic\logging_logic.py
#------------------------------------------------------------------------------------------------
import time
from typing import List, Dict
from cryptotrader.config import get_logger

logger = get_logger(__name__)


class LoggingLogic:
    """Handles logging operations separate from the UI."""

    def __init__(self):
        self.logs: List[Dict] = []

    def add_log(self, message: str, level: str = "INFO") -> Dict:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"timestamp": timestamp, "level": level.upper(), "message": message}
        self.logs.append(log_entry)

        if level.upper() == "ERROR":
            logger.error(message)
        elif level.upper() == "WARNING":
            logger.warning(message)
        elif level.upper() == "SUCCESS":
            logger.info(f"[SUCCESS] {message}")
        else:
            logger.info(message)

        return log_entry

    def clear_logs(self):
        self.logs.clear()

    def get_all_logs(self) -> List[Dict]:
        return list(self.logs)


#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\components\logic\strategy_logic.py
#------------------------------------------------------------------------------------------------
from typing import Dict, List, Optional

class StrategyLogic:
    """Business logic for managing trading strategies."""

    def __init__(self):
        self.available_symbols: List[str] = []
        self.active_strategies: Dict[int, Dict] = {}
        self.strategy_parameters: Dict[int, Dict] = {}

        self.strategy_types = ["Technical", "Breakout"]
        self.timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

    def set_available_symbols(self, symbols: List[str]):
        self.available_symbols = sorted(symbols)

    def add_strategy(self, row_id: int) -> Dict:
        default_symbol = self.available_symbols[0] if self.available_symbols else "BTCUSDT"
        self.active_strategies[row_id] = {
            "strategy_type": self.strategy_types[0],
            "symbol": default_symbol,
            "timeframe": "1h",
            "balance_pct": "10",
            "tp_pct": "2",
            "sl_pct": "1",
            "status": "INACTIVE",
            "is_active": False,
        }
        self.strategy_parameters[row_id] = {}
        return self.active_strategies[row_id]

    def delete_strategy(self, row_id: int):
        self.active_strategies.pop(row_id, None)
        self.strategy_parameters.pop(row_id, None)

    def update_strategy_field(self, row_id: int, field: str, value):
        if row_id in self.active_strategies:
            self.active_strategies[row_id][field] = value

    def save_parameters(self, row_id: int, params: Dict):
        self.strategy_parameters[row_id] = params

    def toggle_strategy(self, row_id: int) -> bool:
        if row_id not in self.active_strategies:
            return False

        strategy = self.active_strategies[row_id]
        strategy["is_active"] = not strategy["is_active"]
        strategy["status"] = "ACTIVE" if strategy["is_active"] else "INACTIVE"
        return strategy["is_active"]

    def validate_strategy(self, row_id: int) -> Optional[str]:
        strategy = self.active_strategies.get(row_id)
        params = self.strategy_parameters.get(row_id)

        if not strategy:
            return "Strategy not found."

        try:
            balance_pct = float(strategy["balance_pct"])
            if balance_pct <= 0 or balance_pct > 100:
                return "Balance percentage must be between 0 and 100."

            tp_pct = float(strategy["tp_pct"])
            if tp_pct <= 0:
                return "Take profit must be greater than 0."

            sl_pct = float(strategy["sl_pct"])
            if sl_pct <= 0:
                return "Stop loss must be greater than 0."
        except ValueError:
            return "Invalid numeric input."

        if not params:
            return "Strategy parameters not set."

        if strategy["strategy_type"] == "Technical":
            required = ["ema_fast", "ema_slow", "ema_signal"]
            if not all(r in params for r in required):
                return "Missing MACD parameters."

        if strategy["strategy_type"] == "Breakout":
            if "min_volume" not in params:
                return "Missing Breakout minimum volume parameter."

        return None

    def start_strategy(self, row_id: int) -> bool:
        """Placeholder: Start executing the trading strategy."""
        pass

    def stop_strategy(self, row_id: int) -> bool:
        """Placeholder: Stop executing the trading strategy."""
        pass


#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\components\logic\trade_history_logic.py
#------------------------------------------------------------------------------------------------
"""
File: src/cryptotrader/gui/components/logic/trade_history_logic.py

Trade History Logic

Handles fetching trade data and calculating PNL.
"""
from typing import List, Optional
from cryptotrader.config import get_logger
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)

class TradeHistoryLogic:
    """Business logic for fetching trade history and calculating PNL."""

    def __init__(self, client: Optional[BinanceRestUnifiedClient] = None):
        # Use provided client or default to BinanceRestUnifiedClient
        self.client = client or BinanceRestUnifiedClient()

    def fetch_trades(self, symbol: str) -> List[dict]:
        """Fetch past trades for a symbol using Binance API."""
        try:
            trades = self.client.get_my_trades(symbol)
            logger.info(f"Fetched {len(trades)} trades for {symbol}")
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            return []

    def calculate_pnl(self, trades: List[dict]) -> float:
        """Calculate realized PNL from a list of trades."""
        total_cost = 0.0
        total_revenue = 0.0
        for trade in trades:
            qty = float(trade.get("qty", 0))
            price = float(trade.get("price", 0))
            commission = float(trade.get("commission", 0))
            # isBuyer indicates a buy trade
            if trade.get("isBuyer", False):
                total_cost += (qty * price) + commission
            else:
                total_revenue += (qty * price) - commission
        pnl = total_revenue - total_cost
        logger.info(f"Calculated PNL: {pnl:.2f}")
        return pnl


#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\components\logic\watchlist_logic.py
#------------------------------------------------------------------------------------------------
# File: src/gui/components/logic/watchlist_logic.py
"""
Watchlist Logic

Handles symbol validation, searching, and fetching price updates using the Unified Client.
"""

from typing import Callable, Optional, List
from cryptotrader.config import get_logger
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)


class WatchlistLogic:
    """Business logic for symbol validation, lookup, and price updates."""

    def __init__(self, client: Optional[BinanceRestUnifiedClient] = None):
        # Use provided client or default to BinanceRestUnifiedClient
        self.client = client or BinanceRestUnifiedClient()

    def fetch_symbol_data(self, symbol: str, callback: Callable[[str, dict], None]) -> None:
        """Fetch latest bid/ask prices for a symbol and invoke the callback."""
        try:
            ticker = self.client.get_24h_ticker_price(symbol)
            if ticker:
                callback(symbol, ticker)
            else:
                logger.warning(f"No ticker data returned for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching ticker data for {symbol}: {e}")

    def search_symbols(self, query: str) -> List[str]:
        """Return a sorted list of symbols containing the query substring (case-insensitive)."""
        try:
            # Retrieves a Set[str] of symbols from unified client
            all_syms = self.client.get_binance_symbols()
            q = query.strip().upper()
            # Filter symbols by substring match
            matches = [sym for sym in all_syms if q in sym]
            return sorted(matches)
        except Exception as e:
            logger.error(f"Error searching symbols for query '{query}': {e}")
            return []

    def validate_symbol(self, symbol: str) -> bool:
        """Check if the exact symbol exists on Binance."""
        try:
            # Exact membership check against Set[str]
            return symbol.strip().upper() in self.client.get_binance_symbols()
        except Exception as e:
            logger.error(f"Error validating symbol '{symbol}': {e}")
            return False


#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\main_layout.py
#------------------------------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Main layout for the CryptoTrader application with complete tab structure,
now streamlined: removed "Trading View", and added Strategy and Logging tabs.
"""

import tkinter as tk
from tkinter import ttk

from cryptotrader.config import get_logger
from cryptotrader.gui.app_styles import apply_theme
from cryptotrader.gui.layouts.overview_layout import OverviewLayout
from cryptotrader.gui.components.ui.watchlist_widget import WatchlistWidget
from cryptotrader.gui.components.trades_component import TradesWatch
from cryptotrader.gui.components.ui.strategy_widget import StrategyWidget
from cryptotrader.gui.components.ui.logging_widget import LoggingWidget

# Initialize logger for this module
logger = get_logger(__name__)

class MainLayout(tk.Tk):
    """Main window for the application with all required tabs."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("CryptoTrader Dashboard")
        self.geometry("1024x768")

        # Apply theme and get fonts
        self.fonts = apply_theme(self)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Define tabs (removed "Trading View")
        tabs = [
            ("Overview",   ttk.Frame(self.notebook)),
            ("Watchlist",  ttk.Frame(self.notebook)),
            ("Market View",ttk.Frame(self.notebook)),
            ("Trades",     ttk.Frame(self.notebook)),
            ("Logging",    ttk.Frame(self.notebook)),
            ("Strategy",   ttk.Frame(self.notebook)),
            ("Charts",     ttk.Frame(self.notebook)),
            ("Settings",   ttk.Frame(self.notebook)),
        ]
        for name, frame in tabs:
            setattr(self, f"{name.lower().replace(' ', '_')}_tab", frame)
            self.notebook.add(frame, text=name)

        # Populate tabs
        self._setup_overview_tab()
        self._setup_watchlist_tab()
        self._setup_trades_tab()
        self._setup_logging_tab()
        self._setup_strategy_tab()
        # Placeholder for remaining tabs
        for name in ["Market View", "Charts", "Settings"]:
            tab = getattr(self, f"{name.lower().replace(' ', '_')}_tab")
            self._setup_placeholder_tab(tab, name)

        logger.info("Main layout initialized with all tabs")

    def _setup_placeholder_tab(self, tab, title):
        """Add placeholder content for tabs not yet implemented."""
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        label = ttk.Label(
            frame,
            text=f"{title} Content Will Be Added Here",
            font=self.fonts.get("large")
        )
        label.pack(pady=50)
        ttk.Button(
            frame,
            text=f"{title} Action",
            command=lambda: logger.info(f"{title} button clicked")
        ).pack(pady=10)

    def _setup_overview_tab(self):
        """Initialize the Overview tab with the grid overview layout."""
        layout = OverviewLayout(self.overview_tab, self.fonts)
        layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Overview tab initialized with grid layout")

    def _setup_watchlist_tab(self):
        """Initialize the Watchlist tab with the watchlist widget."""
        widget = WatchlistWidget(self.watchlist_tab)
        widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Watchlist tab initialized")

    def _setup_trades_tab(self):
        """Initialize the Trades tab with the TradesWatch component."""
        widget = TradesWatch(self.trades_tab)
        widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Trades tab initialized with TradesWatch component")

    def _setup_logging_tab(self):
        """Initialize the Logging tab with the logging widget."""
        widget = LoggingWidget(self.logging_tab)
        widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Logging tab initialized with LoggingWidget")

    def _setup_strategy_tab(self):
        """Initialize the Strategy tab with the strategy widget."""
        widget = StrategyWidget(self.strategy_tab)
        widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        logger.info("Strategy tab initialized with StrategyWidget")


def main():
    """Application entry point."""
    logger.info("Starting CryptoTrader Dashboard")
    window = MainLayout()
    window.mainloop()

if __name__ == "__main__":
    main()

#------------------------------------------------------------------------------------------------
# src\cryptotrader\gui\layouts\overview_layout.py
#------------------------------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk

from cryptotrader.config import get_logger
from cryptotrader.gui.components.ui.watchlist_widget import WatchlistWidget
from cryptotrader.gui.components.ui.strategy_widget import StrategyWidget
from cryptotrader.gui.components.ui.logging_widget import LoggingWidget
from cryptotrader.gui.components.ui.trade_history_widget import TradeHistoryWidget

# Initialize logger
logger = get_logger(__name__)

class OverviewLayout(ttk.Frame):
    """Grid layout for Overview tab: 2x2 panels with 40/60 width split."""

    def __init__(self, parent, fonts: dict):
        super().__init__(parent)
        self.fonts = fonts
        self._init_grid()
        self._create_panels()

    def _init_grid(self):
        # Two columns: left 40%, right 60%
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        # Two equal-height rows
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def _create_panels(self):
        # Watchlist panel (top-left)
        self.watchlist_panel = ttk.LabelFrame(self, text="Watchlist", padding=10)
        self.watchlist_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        WatchlistWidget(self.watchlist_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Watchlist panel initialized")

        # Strategy panel (top-right)
        self.strategy_panel = ttk.LabelFrame(self, text="Strategy", padding=10)
        self.strategy_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        StrategyWidget(self.strategy_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Strategy panel initialized")

        # Logging panel (bottom-left)
        self.logging_panel = ttk.LabelFrame(self, text="Logging", padding=10)
        self.logging_panel.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        LoggingWidget(self.logging_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Logging panel initialized")

        # Trade History panel (bottom-right)
        self.trade_history_panel = ttk.LabelFrame(self, text="Trade History", padding=10)
        self.trade_history_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        TradeHistoryWidget(self.trade_history_panel).pack(fill=tk.BOTH, expand=True)
        logger.info("Trade History panel initialized")

#------------------------------------------------------------------------------------------------
#src\cryptotrader\services\unified_clients\cryptoRestUnifiedClient.py
#------------------------------------------------------------------------------------------------
"""High‑level unified client mirroring BinanceRestUnifiedClient surface."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from cryptotrader.config import get_logger
from .base_operations import CryptoBaseOperations

logger = get_logger(__name__)

class CryptoRestUnifiedClient(CryptoBaseOperations):
    """Subset of endpoints required by existing app logic."""

    # ------------------------------------------------------------------
    # Market data
    # ------------------------------------------------------------------
    def get_exchange_info(self) -> Dict[str, Any]:
        """Return symbol metadata (mirror Binance get_exchange_info)."""
        # Crypto.com: /public/get-instruments
        return self._request("GET", "/public/get-instruments")

    def get_ticker_24h(self, instrument_name: str) -> Dict[str, Any]:
        """24h stats; instrument_name like "BTC_USDT"."""
        return self._request("GET", "/public/get-ticker", instrument_name=instrument_name)

    # ------------------------------------------------------------------
    # Account / Orders (minimal for watchlist & PnL)
    # ------------------------------------------------------------------
    def get_account_summary(self) -> Dict[str, Any]:
        return self._request("POST", "/private/get-account-summary")

    def place_order(
        self,
        instrument_name: str,
        side: str,
        type_: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Simple order placement (LIMIT or MARKET)."""
        return self._request(
            "POST",
            "/private/create-order",
            instrument_name=instrument_name,
            side=side,
            type=type_,
            price=price,
            quantity=quantity,
        )

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return self._request("POST", "/private/cancel-order", order_id=order_id)

    def get_my_trades(self, instrument_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Mirror Binance `get_my_trades`."""
        res = self._request("POST", "/private/get-trades", instrument_name=instrument_name, **kwargs)
        return res.get("data", [])

#------------------------------------------------------------------------------------------------
#src\cryptotrader\services\unified_clients\binanceRestUnifiedClient.py
#------------------------------------------------------------------------------------------------
# File: src/gui/unified_clients/binanceRestUnifiedClient.py

from typing import Optional, List, Set, Union

from cryptotrader.config import get_logger
from cryptotrader.services.binance.restAPI.systemApi import SystemOperations
from cryptotrader.services.binance.restAPI.orderApi import OrderOperations

# Import only the real classes that actually exist:
from cryptotrader.services.binance.models.base_models import (
    OrderRequest,
    OrderStatus,
)  # :contentReference[oaicite:0]{index=0}&#8203;:contentReference[oaicite:1]{index=1}
from cryptotrader.services.binance.models.order_models import (
    OrderResponseFull,
    OrderResponseResult,
    OrderResponseAck,
    CancelReplaceResponse,
    OrderTrade,
)  # :contentReference[oaicite:2]{index=2}&#8203;:contentReference[oaicite:3]{index=3}


logger = get_logger(__name__)


class BinanceRestUnifiedClient:
    """
    Unified client for accessing major Binance REST functionalities.
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.system = SystemOperations()
        self.orders = OrderOperations()

    def get_binance_symbols(self, only_trading: bool = True) -> Set[str]:
        """
        Return the current set of Binance symbols (defaults to only those in TRADING status).
        """
        return self.system.get_binance_symbols(only_trading)

    def get_24h_ticker_price(
        self, symbol: Optional[str] = None
    ) -> Union[List[dict], dict]:
        """
        Fetch 24-hour ticker price change statistics for a symbol or all symbols.
        """
        req = self.system.request(
            method="GET",
            endpoint="/api/v3/ticker/24hr",
        ).requiresAuth(False)

        if symbol:
            req = req.withQueryParams(symbol=symbol)
        return req.execute()

    def place_order(self, request: OrderRequest) -> OrderResponseFull:
        """
        Place a new spot order.
        """
        return self.orders.place_order(request)

    def cancel_order(self, order_id: str, symbol: str) -> OrderResponseAck:
        """
        Cancel an existing spot order by order ID and symbol.
        """
        return self.orders.cancelOrderRest(order_id, symbol)

    def get_order_status(self, order_id: str, symbol: str) -> OrderStatus:
        """
        Retrieve the current status of a specific spot order.
        """
        return self.orders.get_order_status(order_id, symbol)

    def get_open_orders(
        self, symbol: Optional[str] = None
    ) -> List[OrderResponseResult]:
        """
        Retrieve all open spot orders, optionally filtered by symbol.
        """
        return self.orders.get_open_orders(symbol)

    def get_my_trades(self, symbol: str) -> List[OrderTrade]:
        """
        Retrieve past trades for a given symbol.
        """
        return self.orders.get_my_trades(symbol)

    def cancel_replace_order(self, params: dict) -> CancelReplaceResponse:
        """
        Cancel an existing order and place a new one atomically.
        `params` should include the fields required by your
        `OrderOperations.cancel_replace_order` implementation.
        """
        return self.orders.cancel_replace_order(params)
