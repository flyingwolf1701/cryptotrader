"""
Application Styles

This module defines color schemes and styles for the CryptoTrader dashboard.
"""

from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# Color definitions
class Colors:
    # Main colors
    BACKGROUND = "#1e1e1e"
    BACKGROUND_LIGHT = "#2d2d30"
    FOREGROUND = "#d4d4d4"
    ACCENT = "#007acc"
    
    # Status colors
    SUCCESS = "#6A8759"  # Green
    WARNING = "#BBB529"  # Yellow
    ERROR = "#FF5555"    # Red
    
    # Trading colors
    BUY = "#6A8759"      # Green
    SELL = "#CF6A4C"     # Red
    NEUTRAL = "#A9B7C6"  # Gray

# Font definitions
class Fonts:
    NORMAL = QFont("Segoe UI", 10)
    BOLD = QFont("Segoe UI", 10, QFont.Bold)
    MONOSPACE = QFont("Consolas", 10)
    SMALL = QFont("Segoe UI", 8)
    LARGE = QFont("Segoe UI", 12)

def apply_dark_theme(app: QApplication):
    """Apply a dark theme to the entire application.
    
    Args:
        app: The QApplication instance
    """
    # Create dark palette
    palette = QPalette()
    
    # Set colors
    palette.setColor(QPalette.Window, QColor(Colors.BACKGROUND))
    palette.setColor(QPalette.WindowText, QColor(Colors.FOREGROUND))
    palette.setColor(QPalette.Base, QColor(Colors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.AlternateBase, QColor(Colors.BACKGROUND))
    palette.setColor(QPalette.ToolTipBase, QColor(Colors.BACKGROUND))
    palette.setColor(QPalette.ToolTipText, QColor(Colors.FOREGROUND))
    palette.setColor(QPalette.Text, QColor(Colors.FOREGROUND))
    palette.setColor(QPalette.Button, QColor(Colors.BACKGROUND_LIGHT))
    palette.setColor(QPalette.ButtonText, QColor(Colors.FOREGROUND))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(Colors.ACCENT))
    palette.setColor(QPalette.Highlight, QColor(Colors.ACCENT))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    
    # Apply the palette
    app.setPalette(palette)
    
    # Set the application style sheet for more detailed styling
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }
        
        QTabWidget::pane {
            border: 1px solid #3c3c3c;
            background-color: #1e1e1e;
        }
        
        QTabBar::tab {
            background-color: #2d2d30;
            color: #d4d4d4;
            padding: 8px 12px;
            border: 1px solid #3c3c3c;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: #1e1e1e;
            border-bottom: 1px solid #1e1e1e;
        }
        
        QTabBar::tab:!selected {
            margin-top: 2px;
        }
        
        QTableWidget {
            background-color: #1e1e1e;
            color: #d4d4d4;
            gridline-color: #3c3c3c;
            border: 1px solid #3c3c3c;
        }
        
        QTableWidget::item {
            padding: 4px;
        }
        
        QTableWidget::item:selected {
            background-color: #264f78;
        }
        
        QHeaderView::section {
            background-color: #2d2d30;
            color: #d4d4d4;
            padding: 4px;
            border: 1px solid #3c3c3c;
        }
        
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 4px;
        }
        
        QPushButton {
            background-color: #2d2d30;
            color: #d4d4d4;
            border: 1px solid #3c3c3c;
            padding: 6px 12px;
            border-radius: 2px;
        }
        
        QPushButton:hover {
            background-color: #3e3e42;
        }
        
        QPushButton:pressed {
            background-color: #007acc;
        }
        
        QGroupBox {
            border: 1px solid #3c3c3c;
            border-radius: 3px;
            margin-top: 1ex;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
        }
    """)