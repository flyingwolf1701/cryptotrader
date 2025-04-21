"""
CryptoTrader Application Entry Point

This script initializes the application and starts the main UI.
Keeps the main file clean by delegating the UI logic to the MainWindow class.
"""

import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent  # Navigate to the project root from src/cryptotrader/main.py
sys.path.insert(0, str(project_root))

# Now import from the local modules
from src.cryptotrader.gui.main_window import MainWindow
from src.cryptotrader.gui.components.styles import apply_dark_theme
from src.cryptotrader.config import get_logger

# Configure logging
logger = get_logger(__name__)

def main():
    """Application entry point."""
    # Create the application
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme
    apply_dark_theme(app)
    
    # Log application startup
    logger.info("Starting CryptoTrader Application")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()