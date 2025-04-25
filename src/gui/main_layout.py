"""
Main Layout for CryptoTrader

This module provides the main application layout with a tabbed interface.
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import get_logger
from src.gui.components.styles import Colors, apply_theme
from src.gui.layouts.udemy_layout import UdemyLayout
from src.gui.layouts.charts_layout import ChartsLayout

logger = get_logger(__name__)

class MainLayout(tk.Tk):
    """Main application window with tabbed layout."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window
        self.title("CryptoTrader Dashboard")
        self.geometry("1280x800")
        
        # Apply custom theme
        self.fonts = apply_theme(self)
        
        # Create UI elements
        self.setup_ui()
        
        logger.info("Main layout initialized")
    
    def setup_ui(self):
        """Set up the user interface components."""
        # Configure root window
        self.configure(bg=Colors.BACKGROUND)
        
        # Create main container with notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs for different views
        self.udemy_tab = ttk.Frame(self.notebook)
        self.charts_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.udemy_tab, text="Udemy Short")
        self.notebook.add(self.charts_tab, text="Charts View")
        
        # Create layouts for each tab
        self.udemy_layout = UdemyLayout(self.udemy_tab)
        self.udemy_layout.pack(fill=tk.BOTH, expand=True)
        
        self.charts_layout = ChartsLayout(self.charts_tab)
        self.charts_layout.pack(fill=tk.BOTH, expand=True)
        
        # Setup update timer for live data
        self.after(1500, self._update_ui)
    
    def _update_ui(self):
        """Centralized UI update method."""
        # Update components
        try:
            self.udemy_layout.update_components()
            self.charts_layout.update_components()
        except Exception as e:
            logger.error(f"Error updating UI: {str(e)}")
        
        # Schedule the next update
        self.after(1500, self._update_ui)