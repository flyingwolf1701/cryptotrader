import tkinter as tk
from tkinter import ttk

from cryptotrader.config import get_logger
from cryptotrader.gui.components.ui import watchlist_widget

# Set up logger through centralized system
logger = get_logger(__name__)

class OverviewLayout(ttk.Frame):
    """A grid layout with four panels for the Overview tab."""

    def __init__(self, parent, fonts):
        super().__init__(parent)
        self.fonts = fonts
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        # Configure grid layout for the frame
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Create four panels
        self.watchlist_panel = self._create_watchlist_panel(0, 0, "Watchlist Panel")
        self.strategy_panel = self._create_panel(0, 1, "Strategy Panel")
        self.logging_panel = self._create_panel(1, 0, "Logging Panel")
        self.trading_panel = self._create_panel(1, 1, "Trading Panel")

        logger.info("Overview layout initialized with four panels")

    def _create_panel(self, row, column, title):
        """Create a panel with a title and placeholder content."""
        panel = ttk.LabelFrame(self, text=title, padding=10)
        panel.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        label = ttk.Label(panel, text=f"Content for {title}")
        label.pack(pady=40, padx=40)

        return panel

    def _create_watchlist_panel(self, row, column, title):
        """Create the watchlist panel with the WatchlistWidget."""
        panel = ttk.LabelFrame(self, text=title, padding=10)
        panel.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        # Add the watchlist widget (uses centralized WatchlistWidget)
        self.watchlist = watchlist_widget.WatchlistWidget(panel)
        self.watchlist.pack(fill=tk.BOTH, expand=True)

        # Set available symbols
        available_symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        self.watchlist.set_available_symbols(available_symbols)

        logger.info("Watchlist panel initialized")

# Optional standalone test harness
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Overview Layout Test")
    root.geometry("800x600")

    # Apply a simple dark theme
    root.configure(bg="#1e1e1e")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#1e1e1e")
    style.configure("TLabelframe", background="#1e1e1e", foreground="#d4d4d4")
    style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#d4d4d4")
    style.configure("TLabel", background="#1e1e1e", foreground="#d4d4d4")

    fonts = {}
    overview = OverviewLayout(root, fonts)
    overview.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()
