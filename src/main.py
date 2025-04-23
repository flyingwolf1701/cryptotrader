"""
CryptoTrader Application Entry Point

This script initializes the application and starts the main UI.
Keeps the main file clean by delegating the UI logic to the MainWindow class.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent  # Navigate to the project root from src/cryptotrader/main.py
sys.path.insert(0, str(project_root))

# Now import from the local modules
from gui.main_window import MainWindow
from config import get_logger

# Configure logging
logger = get_logger(__name__)

def main() -> None:
    """Application entry point."""
    # Log application startup
    logger.info("Starting CryptoTrader Application")
    
    # Create and show the main window
    window = MainWindow()
    
    # Start the event loop
    window.mainloop()

if __name__ == "__main__":
    main()