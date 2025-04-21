"""
Chart Widget Component

Displays interactive candlestick charts for cryptocurrency trading.
"""

import time
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel,
    QGroupBox, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot

# For matplotlib integration with Qt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle

from cryptotrader.config import get_logger
from cryptotrader.services.binance.models import Candle


logger = get_logger(__name__)


class CandlestickChart(FigureCanvas):
    """Matplotlib canvas for displaying candlestick charts."""
    
    def __init__(self, parent=None, width=10, height=8, dpi=100):
        """Initialize the chart canvas."""
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Initial setup
        self.axes.set_title("Loading data...")
        self.axes.set_ylabel("Price")
        self.axes.set_xlabel("Time")
        self.axes.grid(True, alpha=0.3)
        
        # Enable zooming and panning
        self.fig.tight_layout()
        
        # Data storage
        self.candles = []
        self.symbol = ""
        self.timeframe = ""
    
    def plot_candles(self, candles: List[Candle], symbol: str, timeframe: str):
        if not candles:
            return

        self.candles = candles
        self.symbol = symbol
        self.timeframe = timeframe

        self.axes.clear()
        dates = []

        for candle in candles:
            try:
                timestamp = candle.timestamp
                open_price = candle.open
                high_price = candle.high
                low_price = candle.low
                close_price = candle.close
            except AttributeError:
                # fallback for dict or list-based data
                timestamp = candle.timestamp
                open_price = candle.open_price
                high_price = candle.high_price
                low_price = candle.low_price
                close_price = candle.close_price


            date = datetime.fromtimestamp(timestamp / 1000)
            dates.append(date)

            color = 'green' if close_price >= open_price else 'red'
            self.axes.plot([date, date], [low_price, high_price], color='black', linewidth=1)

            if len(dates) > 1:
                width = (dates[-1] - dates[-2]) * 0.8
            else:
                width = 0.01  # fallback

            rect = Rectangle(
                (mdates.date2num(date) - width / 2, min(open_price, close_price)),
                width=width,
                height=abs(close_price - open_price),
                facecolor=color,
                edgecolor='black',
                linewidth=0.5
            )
            self.axes.add_patch(rect)

        self.axes.set_title(f"{symbol} {timeframe} Chart")
        self.axes.xaxis_date()
        self.fig.autofmt_xdate()
        self.axes.grid(True, alpha=0.3)

        # Apply better x-axis formatting
        if timeframe in ["1m", "5m", "15m"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        elif timeframe in ["30m", "1h", "4h"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%H:%M'))
        else:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        self.draw()



class ChartWidget(QWidget):
    """Widget for displaying and controlling trading charts."""
    
    def __init__(self, market_client):
        super().__init__()
        
        self.market_client = market_client
        self.current_symbol = "BTCUSDT"
        self.current_timeframe = "1h"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Control panel
        controls = QHBoxLayout()
        
        # Symbol selector
        symbol_group = QGroupBox("Symbol")
        symbol_layout = QVBoxLayout(symbol_group)
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems(["BTCUSDT", "ETHUSDT", "BNBUSDT"])
        self.symbol_combo.currentTextChanged.connect(self.symbol_changed)
        symbol_layout.addWidget(self.symbol_combo)
        
        # Timeframe selector
        timeframe_group = QGroupBox("Timeframe")
        timeframe_layout = QVBoxLayout(timeframe_group)
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "30m", "1h", "4h", "1d"])
        self.timeframe_combo.setCurrentText("1h")
        self.timeframe_combo.currentTextChanged.connect(self.timeframe_changed)
        timeframe_layout.addWidget(self.timeframe_combo)
        
        # Refresh button
        refresh_group = QGroupBox("Actions")
        refresh_layout = QVBoxLayout(refresh_group)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_chart)
        refresh_layout.addWidget(self.refresh_btn)
        
        # Add control widgets to layout
        controls.addWidget(symbol_group)
        controls.addWidget(timeframe_group)
        controls.addWidget(refresh_group)
        controls.addStretch()
        
        # Add controls to main layout
        layout.addLayout(controls)
        
        # Chart container
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.StyledPanel)
        chart_frame.setFrameShadow(QFrame.Sunken)
        chart_layout = QVBoxLayout(chart_frame)
        
        # Create chart
        self.chart = CandlestickChart(self)
        
        # Create toolbar
        self.toolbar = NavigationToolbar(self.chart, self)
        
        # Add chart and toolbar to layout
        chart_layout.addWidget(self.toolbar)
        chart_layout.addWidget(self.chart)
        
        # Add chart frame to main layout
        layout.addWidget(chart_frame, 1)  # Give it a stretch factor of 1
        
        # Load initial data
        self.refresh_chart()
    
    def symbol_changed(self, symbol):
        """Handle symbol change event."""
        self.current_symbol = symbol
        self.refresh_chart()
    
    def timeframe_changed(self, timeframe):
        """Handle timeframe change event."""
        self.current_timeframe = timeframe
        self.refresh_chart()
    
    def refresh_chart(self):
        """Refresh chart data."""
        try:
            # Convert timeframe to API format (e.g., 1h -> 1h)
            interval = self.current_timeframe
            
            # Fetch candle data
            candle_data = self.market_client.get_historical_candles(
                symbol=self.current_symbol,
                interval=interval,
                limit=100  # Last 100 candles
            )
            
            if candle_data:
                # Plot the data
                self.chart.plot_candles(candle_data, self.current_symbol, self.current_timeframe)
                logger.info(f"Updated chart for {self.current_symbol} ({self.current_timeframe})")
            else:
                logger.error(f"Failed to fetch candle data for {self.current_symbol}")
                
        except Exception as e:
            logger.error(f"Error refreshing chart: {str(e)}")
    
    def set_available_symbols(self, symbols):
        """Set the available symbols in the combobox."""
        current = self.symbol_combo.currentText()
        self.symbol_combo.clear()
        self.symbol_combo.addItems(symbols)
        
        # Try to restore previous selection
        index = self.symbol_combo.findText(current)
        if index >= 0:
            self.symbol_combo.setCurrentIndex(index)
        else:
            # Default to first item
            self.symbol_combo.setCurrentIndex(0)

        