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
