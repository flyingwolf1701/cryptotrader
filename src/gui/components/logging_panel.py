"""
Logging Panel Component

Displays application logs and system messages in a scrollable text view.
"""

import time
import tkinter as tk
from tkinter import ttk

from src.config import get_logger
from src.gui.components.styles import Colors

logger = get_logger(__name__)


class LoggingPanel(ttk.Frame):
    """Widget for displaying application logs and messages."""

    def __init__(self, parent):
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Configure grid layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create text widget with scrollbar for logs
        log_frame = ttk.Frame(self)
        log_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Configure the text widget for logs
        self.log_view = tk.Text(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            background=Colors.BACKGROUND,
            foreground=Colors.FOREGROUND,
            font=("Courier New", 10),
        )

        # Create scrollbar
        scrollbar = ttk.Scrollbar(
            log_frame, orient="vertical", command=self.log_view.yview
        )
        self.log_view.configure(yscrollcommand=scrollbar.set)

        # Pack widgets
        self.log_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Button controls
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.clear_btn = ttk.Button(
            button_frame, text="Clear Logs", command=self.clear_logs
        )
        self.clear_btn.pack(side=tk.RIGHT)

        # Configure text tags for different log levels
        self.log_view.tag_configure("INFO", foreground="white")
        self.log_view.tag_configure("ERROR", foreground=Colors.ERROR)
        self.log_view.tag_configure("WARNING", foreground=Colors.WARNING)
        self.log_view.tag_configure("SUCCESS", foreground=Colors.SUCCESS)

        # Add a welcome message
        self.add_log("Logging system initialized")

    def add_log(self, message, level="INFO"):
        """Add a log message to the view.

        Args:
            message: The log message to display
            level: Log level (INFO, WARNING, ERROR, etc.)
        """
        # Generate timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Create formatted log message
        log_entry = f"[{timestamp}] {level}: {message}\n"

        # Add the entry with color
        self.log_view.insert(tk.END, log_entry, level)
        self.log_view.see(tk.END)  # Scroll to the end

        # Also log to system logger
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)

    def clear_logs(self):
        """Clear all log messages from the view."""
        self.log_view.delete(1.0, tk.END)
        self.add_log("Logs cleared")
