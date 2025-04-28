"""

# Fix import path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # Add project root to Python path

Chart Widget Component

Displays interactive candlestick charts for cryptocurrency trading.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple, Union, cast

# For matplotlib integration with Tkinter
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import matplotlib.axes
import numpy as np

from config import get_logger
from src.services.binance.models import Candle
from src.gui.components.styles import Colors

logger = get_logger(__name__)


class CandlestickChart:
    """Matplotlib canvas for displaying candlestick charts."""

    def __init__(
        self, parent: tk.Widget, width: int = 10, height: int = 6, dpi: int = 100
    ):
        """Initialize the chart canvas."""
        self.fig: Figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes: matplotlib.axes.Axes = self.fig.add_subplot(111)

        # Configure figure appearance for dark theme
        self.fig.patch.set_facecolor(Colors.BACKGROUND)
        self.axes.set_facecolor(Colors.BACKGROUND)
        self.axes.spines["bottom"].set_color(Colors.FOREGROUND)
        self.axes.spines["top"].set_color(Colors.FOREGROUND)
        self.axes.spines["left"].set_color(Colors.FOREGROUND)
        self.axes.spines["right"].set_color(Colors.FOREGROUND)
        self.axes.tick_params(colors=Colors.FOREGROUND)
        self.axes.xaxis.label.set_color(Colors.FOREGROUND)
        self.axes.yaxis.label.set_color(Colors.FOREGROUND)
        self.axes.title.set_color(Colors.FOREGROUND)

        # Create canvas widget
        self.canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_widget: tk.Widget = self.canvas.get_tk_widget()

        # Create toolbar
        self.toolbar: NavigationToolbar2Tk = NavigationToolbar2Tk(self.canvas, parent)
        self.toolbar.config(background=Colors.BACKGROUND)
        self.toolbar._message_label.config(
            background=Colors.BACKGROUND, foreground=Colors.FOREGROUND
        )
        for button in self.toolbar.winfo_children():
            if isinstance(button, tk.Button):
                button.config(
                    background=Colors.BACKGROUND_LIGHT, foreground=Colors.FOREGROUND
                )

        # Initial setup
        self.axes.set_title("Loading data...")
        self.axes.set_ylabel("Price")
        self.axes.set_xlabel("Time")
        self.axes.grid(True, alpha=0.3)

        # Enable zooming and panning
        self.fig.tight_layout()

        # Data storage
        self.candles: List[Any] = []
        self.symbol: str = ""
        self.timeframe: str = ""

    def get_widget(self) -> tk.Widget:
        """Get the canvas widget for packing."""
        return self.canvas_widget

    def get_toolbar(self) -> NavigationToolbar2Tk:
        """Get the toolbar widget for packing."""
        return self.toolbar

    def plot_candles(self, candles: List[Any], symbol: str, timeframe: str) -> None:
        """Plot candlestick data on the chart.

        Args:
            candles: List of candle data objects
            symbol: Trading symbol (e.g. 'BTCUSDT')
            timeframe: Timeframe string (e.g. '1h')
        """
        if not candles:
            return

        self.candles = candles
        self.symbol = symbol
        self.timeframe = timeframe

        self.axes.clear()
        dates: List[datetime] = []

        for candle in candles:
            try:
                timestamp = candle.timestamp
                openPrice = candle.open
                highPrice = candle.high
                lowPrice = candle.low
                closePrice = candle.close
            except AttributeError:
                # fallback for dict or list-based data
                timestamp = candle.timestamp
                openPrice = candle.openPrice
                highPrice = candle.highPrice
                lowPrice = candle.lowPrice
                closePrice = candle.closePrice

            date = datetime.fromtimestamp(timestamp / 1000)
            dates.append(date)

            color = "green" if closePrice >= openPrice else "red"
            self.axes.plot(
                [date, date], [lowPrice, highPrice], color="black", linewidth=1
            )

            if len(dates) > 1:
                # Convert dates to numbers for width calculation
                date_num_current = mdates.date2num(date)
                date_num_prev = mdates.date2num(dates[-2])
                width = (date_num_current - date_num_prev) * 0.8
            else:
                width = 0.01  # fallback

            rect = Rectangle(
                (mdates.date2num(date) - width / 2, min(openPrice, closePrice)),
                width=width,
                height=abs(closePrice - openPrice),
                facecolor=color,
                edgecolor="black",
                linewidth=0.5,
            )
            self.axes.add_patch(rect)

        self.axes.set_title(f"{symbol} {timeframe} Chart")
        self.axes.xaxis_date()
        self.fig.autofmt_xdate()
        self.axes.grid(True, alpha=0.3)

        # Apply better x-axis formatting
        if timeframe in ["1m", "5m", "15m"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif timeframe in ["30m", "1h", "4h"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%d-%H:%M"))
        else:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        # Configure axes colors for dark theme
        self.axes.spines["bottom"].set_color(Colors.FOREGROUND)
        self.axes.spines["top"].set_color(Colors.FOREGROUND)
        self.axes.spines["left"].set_color(Colors.FOREGROUND)
        self.axes.spines["right"].set_color(Colors.FOREGROUND)
        self.axes.tick_params(colors=Colors.FOREGROUND)
        self.axes.xaxis.label.set_color(Colors.FOREGROUND)
        self.axes.yaxis.label.set_color(Colors.FOREGROUND)
        self.axes.title.set_color(Colors.FOREGROUND)

        self.canvas.draw()


class ChartWidget(ttk.Frame):
    """Widget for displaying and controlling trading charts."""

    def __init__(self, parent: tk.Widget, market_client: Any):
        super().__init__(parent)

        self.market_client: Any = market_client
        self.current_symbol: str = "BTCUSDT"
        self.current_timeframe: str = "1h"

        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create control panel at the top
        controls_frame = ttk.Frame(self)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Symbol selector
        symbol_frame = ttk.LabelFrame(controls_frame, text="Symbol")
        symbol_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        self.symbol_var: tk.StringVar = tk.StringVar(value=self.current_symbol)
        self.symbol_combo: ttk.Combobox = ttk.Combobox(
            symbol_frame, textvariable=self.symbol_var, width=10
        )
        self.symbol_combo.pack(padx=5, pady=5)
        self.symbol_combo.bind(
            "<<ComboboxSelected>>", lambda e: self.symbol_changed(self.symbol_var.get())
        )

        # Timeframe selector
        timeframe_frame = ttk.LabelFrame(controls_frame, text="Timeframe")
        timeframe_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        self.timeframe_var: tk.StringVar = tk.StringVar(value=self.current_timeframe)
        self.timeframe_combo: ttk.Combobox = ttk.Combobox(
            timeframe_frame,
            textvariable=self.timeframe_var,
            width=5,
            values=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
        )
        self.timeframe_combo.pack(padx=5, pady=5)
        self.timeframe_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.timeframe_changed(self.timeframe_var.get()),
        )

        # Refresh button
        action_frame = ttk.LabelFrame(controls_frame, text="Actions")
        action_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

        self.refresh_btn: ttk.Button = ttk.Button(
            action_frame, text="Refresh", command=self.refresh_chart
        )
        self.refresh_btn.pack(padx=5, pady=5)

        # Create chart frame
        chart_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Create chart
        self.chart: CandlestickChart = CandlestickChart(chart_frame)

        # Pack toolbar and chart
        self.chart.get_toolbar().pack(side=tk.TOP, fill=tk.X)
        self.chart.get_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Load initial data
        self.refresh_chart()

    def symbol_changed(self, symbol: str) -> None:
        """Handle symbol change event."""
        self.current_symbol = symbol
        self.refresh_chart()

    def timeframe_changed(self, timeframe: str) -> None:
        """Handle timeframe change event."""
        self.current_timeframe = timeframe
        self.refresh_chart()

    def refresh_chart(self) -> None:
        """Refresh chart data."""
        try:
            # Convert timeframe to API format (e.g., 1h -> 1h)
            interval = self.current_timeframe

            # Fetch candle data
            candle_data = self.market_client.get_historical_candles(
                symbol=self.current_symbol,
                interval=interval,
                limit=100,  # Last 100 candles
            )

            if candle_data:
                # Plot the data
                self.chart.plot_candles(
                    candle_data, self.current_symbol, self.current_timeframe
                )
                logger.info(
                    f"Updated chart for {self.current_symbol} ({self.current_timeframe})"
                )
            else:
                logger.error(f"Failed to fetch candle data for {self.current_symbol}")

        except Exception as e:
            logger.error(f"Error refreshing chart: {str(e)}")

    def set_available_symbols(self, symbols: List[str]) -> None:
        """Set the available symbols in the combobox."""
        current = self.symbol_var.get()

        self.symbol_combo["values"] = symbols

        # Try to restore previous selection
        if current in symbols:
            self.symbol_var.set(current)
        else:
            # Default to first item
            if symbols:
                self.symbol_var.set(symbols[0])
