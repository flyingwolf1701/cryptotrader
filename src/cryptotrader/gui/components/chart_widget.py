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
    
    def plot_candles(self, candles: List, symbol: str, timeframe: str):
        """Plot candlestick data on the chart.
        
        Args:
            candles: List of Candle objects or dictionary data
            symbol: Trading symbol (e.g., "BTCUSDT")
            timeframe: Chart timeframe (e.g., "1h")
        """
        if not candles:
            return
        
        # Store data
        self.candles = candles
        self.symbol = symbol
        self.timeframe = timeframe
        
        # Clear previous plot
        self.axes.clear()
        
        # Format dates for x-axis
        dates = []
        for c in candles:
            # Handle both Candle objects and dictionary data
            timestamp = getattr(c, 'timestamp', c[0]) if hasattr(c, 'timestamp') else c[0]
            dates.append(datetime.fromtimestamp(timestamp / 1000))
        
        # Draw candles
        for i, candle in enumerate(candles):
            # Handle both Candle objects and dictionary data
            if hasattr(candle, 'open'):
                open_price = candle.open
                high_price = candle.high
                low_price = candle.low
                close_price = candle.close
            else:
                open_price = float(candle[1])
                high_price = float(candle[2])
                low_price = float(candle[3])
                close_price = float(candle[4])
            
            # Determine candle color
            color = 'green' if close_price >= open_price else 'red'
            
            # Plot the wick (high-low range)
            self.axes.plot(
                [dates[i], dates[i]], 
                [low_price, high_price], 
                color='black', 
                linewidth=1
            )
            
            # Plot the body (open-close range)
            body_bottom = min(open_price, close_price)
            body_height = abs(close_price - open_price)
            
            # Calculate width for the candle body (in date units)
            if i < len(candles) - 1:
                width = (dates[i+1] - dates[i]) * 0.8
            else:
                # For the last candle, use the same width as the previous one
                width = (dates[i] - dates[i-1]) * 0.8 if i > 0 else 0.8
            
            # Create and add the candle body rectangle
            rect = Rectangle(
                (mdates.date2num(dates[i]) - width/2, body_bottom),
                width=width,
                height=body_height,
                facecolor=color,
                edgecolor='black',
                linewidth=0.5
            )
            self.axes.add_patch(rect)
        
        # Configure axes
        self.axes.set_title(f"{symbol} {timeframe} Chart")
        self.axes.xaxis_date()
        
        # Format the date axis based on timeframe
        if timeframe in ["1m", "5m", "15m"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        elif timeframe in ["30m", "1h", "4h"]:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%d-%H:%M'))
        else:
            self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        self.fig.autofmt_xdate()
        self.axes.grid(True, alpha=0.3)
        
        # Draw everything
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

        