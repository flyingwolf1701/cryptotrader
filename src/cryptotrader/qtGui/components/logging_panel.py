"""
Logging Panel Component

Displays application logs and system messages in a scrollable text view.
"""

import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QTextCursor

from cryptotrader.config import get_logger

logger = get_logger(__name__)

class LoggingPanel(QWidget):
    """Widget for displaying application logs and messages."""
    
    def __init__(self):
        super().__init__()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        # Main layout
        layout = QVBoxLayout(self)
        
        # Log text view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setLineWrapMode(QTextEdit.WidgetWidth)
        self.log_view.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        
        # Button controls
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_btn)
        
        # Add widgets to layout
        layout.addWidget(self.log_view)
        layout.addLayout(button_layout)
        
        # Add a welcome message
        self.add_log("Logging system initialized")
    
    @Slot(str)
    @Slot(str, str)
    def add_log(self, message, level="INFO"):
        """Add a log message to the view.
        
        Args:
            message: The log message to display
            level: Log level (INFO, WARNING, ERROR, etc.)
        """
        # Generate timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine color based on log level
        color = QColor("#FFFFFF")  # Default white
        if level == "ERROR":
            color = QColor("#FF5555")  # Red for errors
        elif level == "WARNING":
            color = QColor("#FFAA55")  # Orange for warnings
        elif level == "SUCCESS":
            color = QColor("#55FF55")  # Green for success
        
        # Create formatted log message
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Add the entry with color
        self.log_view.moveCursor(QTextCursor.End)
        self.log_view.setTextColor(color)
        self.log_view.insertPlainText(log_entry + "\n")
        self.log_view.moveCursor(QTextCursor.End)
        
        # Also log to system logger
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def clear_logs(self):
        """Clear all log messages from the view."""
        self.log_view.clear()
        self.add_log("Logs cleared")