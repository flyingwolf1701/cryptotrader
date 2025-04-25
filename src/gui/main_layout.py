"""
CryptoTrader Application with Complete Tab Structure

This script initializes the application with all tabs requested,
applying the dark theme styling from the styles component.
"""

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import logging
from typing import Dict
from src.gui.layouts.overview_layout import OverviewLayout
from gui.components.watchlist_component import WatchlistWidget

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Color definitions from styles.py
class Colors:
    # Main colors
    BACKGROUND: str = "#1e1e1e"
    BACKGROUND_LIGHT: str = "#2d2d30"
    FOREGROUND: str = "#d4d4d4"
    ACCENT: str = "#007acc"
    
    # Status colors
    SUCCESS: str = "#6A8759"  # Green
    WARNING: str = "#BBB529"  # Yellow
    ERROR: str = "#FF5555"    # Red
    
    # Trading colors
    BUY: str = "#6A8759"      # Green
    SELL: str = "#CF6A4C"     # Red
    NEUTRAL: str = "#A9B7C6"  # Gray

# Font definitions from styles.py
class Fonts:
    @staticmethod
    def create_fonts(root: tk.Tk) -> Dict[str, tkfont.Font]:
        """Create font objects for the application."""
        fonts: Dict[str, tkfont.Font] = {}
        fonts['normal'] = tkfont.Font(family="Segoe UI", size=10)
        fonts['bold'] = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        fonts['monospace'] = tkfont.Font(family="Consolas", size=10)
        fonts['small'] = tkfont.Font(family="Segoe UI", size=8)
        fonts['large'] = tkfont.Font(family="Segoe UI", size=12)
        return fonts

def apply_theme(root: tk.Tk) -> Dict[str, tkfont.Font]:
    """Apply a dark theme to the entire application."""
    # Configure the ttk theme
    style = ttk.Style(root)
    
    # Use 'clam' as a base theme to get more control over styling
    style.theme_use('clam')
    
    # Configure main window background
    root.configure(background=Colors.BACKGROUND)
    
    # Configure ttk styles
    style.configure('TFrame', background=Colors.BACKGROUND)
    style.configure('TLabel', background=Colors.BACKGROUND, foreground=Colors.FOREGROUND)
    style.configure('TButton', 
                   background=Colors.BACKGROUND_LIGHT, 
                   foreground=Colors.FOREGROUND,
                   borderwidth=1)
    style.map('TButton',
             background=[('active', Colors.ACCENT), ('pressed', Colors.ACCENT)],
             foreground=[('active', 'white'), ('pressed', 'white')])
    
    style.configure('TNotebook', background=Colors.BACKGROUND)
    style.configure('TNotebook.Tab', 
                   background=Colors.BACKGROUND_LIGHT, 
                   foreground=Colors.FOREGROUND,
                   padding=[10, 2])
    style.map('TNotebook.Tab',
             background=[('selected', Colors.BACKGROUND), ('active', Colors.ACCENT)],
             foreground=[('selected', Colors.FOREGROUND), ('active', 'white')])
    
    style.configure('TCombobox', 
                   background=Colors.BACKGROUND_LIGHT,
                   fieldbackground=Colors.BACKGROUND_LIGHT,
                   foreground=Colors.FOREGROUND,
                   arrowcolor=Colors.FOREGROUND)
    
    style.configure('Vertical.TScrollbar', 
                   background=Colors.BACKGROUND_LIGHT,
                   arrowcolor=Colors.FOREGROUND,
                   troughcolor=Colors.BACKGROUND)
    
    style.configure('Horizontal.TScrollbar', 
                   background=Colors.BACKGROUND_LIGHT,
                   arrowcolor=Colors.FOREGROUND,
                   troughcolor=Colors.BACKGROUND)
    
    style.configure('TPanedwindow', 
                   background=Colors.BACKGROUND,
                   sashwidth=4,
                   sashrelief=tk.RAISED)
    
    # Apply fonts
    fonts = Fonts.create_fonts(root)
    style.configure('TLabel', font=fonts['normal'])
    style.configure('TButton', font=fonts['normal'])
    style.configure('TNotebook.Tab', font=fonts['normal'])
    
    # Return fonts for use in the application
    return fonts


class MainLayout(tk.Tk):
    """Main window for the application with all required tabs."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("CryptoTrader Dashboard")
        self.geometry("1024x768")
        
        # Apply custom theme
        self.fonts = apply_theme(self)
        
        # Create main container with notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs for different views in the specified order
        self.overview_tab = ttk.Frame(self.notebook)
        self.watchlist_tab = ttk.Frame(self.notebook)
        self.market_tab = ttk.Frame(self.notebook)
        self.trading_tab = ttk.Frame(self.notebook)
        self.logging_tab = ttk.Frame(self.notebook)
        self.strategy_tab = ttk.Frame(self.notebook)
        self.charts_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook in the specified order
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.watchlist_tab, text="Watchlist")
        self.notebook.add(self.market_tab, text="Market View")
        self.notebook.add(self.trading_tab, text="Trading View")
        self.notebook.add(self.logging_tab, text="Logging")
        self.notebook.add(self.strategy_tab, text="Strategy")
        self.notebook.add(self.charts_tab, text="Charts")
        self.notebook.add(self.settings_tab, text="Settings")
        
        # Add content to each tab
        self._setup_overview_tab()
        self._setup_watchlist_tab()
        self._setup_market_tab()
        self._setup_trading_tab()
        self._setup_logging_tab()
        self._setup_strategy_tab()
        self._setup_charts_tab()
        self._setup_settings_tab()
        
        logger.info("Main layout initialized with all tabs")
    
    def _setup_tab_content(self, tab, tab_name):
        """Helper method to set up basic content for a tab."""
        frame = ttk.Frame(tab, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = ttk.Label(
            frame, 
            text=f"Hello {tab_name}", 
            font=self.fonts['large']
        )
        label.pack(pady=50)
        
        button = ttk.Button(
            frame,
            text=f"{tab_name} Action",
            command=lambda: logger.info(f"{tab_name} button clicked")
        )
        button.pack(pady=10)
        
        logger.info(f"{tab_name} tab initialized")
    
    def _setup_overview_tab(self):
        """Set up the Overview tab with the OverviewLayout."""
        # Create the overview layout and pack it to fill the tab
        self.overview_layout = OverviewLayout(self.overview_tab, self.fonts)
        self.overview_layout.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    logger.info("Overview tab initialized with grid layout")
    
    def _setup_watchlist_tab(self):
        """Set up the Watchlist tab with the WatchlistWidget."""
        # Create and configure the watchlist widget
        self.watchlist_widget = WatchlistWidget(self.watchlist_tab)
        self.watchlist_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # The WatchlistWidget will handle fetching available symbols internally
        
        logger.info("Watchlist tab initialized")
    
    def _setup_market_tab(self):
        """Set up the Market View tab."""
        self._setup_tab_content(self.market_tab, "Market View")
    
    def _setup_trading_tab(self):
        """Set up the Trading View tab."""
        self._setup_tab_content(self.trading_tab, "Trading View")
    
    def _setup_logging_tab(self):
        """Set up the Logging tab."""
        self._setup_tab_content(self.logging_tab, "Logging")
    
    def _setup_strategy_tab(self):
        """Set up the Strategy tab."""
        self._setup_tab_content(self.strategy_tab, "Strategy")
    
    def _setup_charts_tab(self):
        """Set up the Charts tab."""
        self._setup_tab_content(self.charts_tab, "Charts")
    
    def _setup_settings_tab(self):
        """Set up the Settings tab."""
        self._setup_tab_content(self.settings_tab, "Settings")


def main():
    """Application entry point."""
    # Log application startup
    logger.info("Starting CryptoTrader Dashboard")
    
    # Create and show the main window
    window = MainLayout()
    
    # Start the event loop
    window.mainloop()


if __name__ == "__main__":
    main()