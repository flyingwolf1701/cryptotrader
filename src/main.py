"""
CryptoTrader Application Entry Point

This script initializes the application and starts the main UI using
the new layout system.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent  # Navigate to the project root from src/main.py
sys.path.insert(0, str(project_root))

# Import from local modules
from src.config import get_logger
from gui.main_layout import MainLayout

# Configure logging
logger = get_logger(__name__)

def main() -> None:
    """Application entry point."""
    # Log application startup
    logger.info("Starting CryptoTrader Application")
    
    # Create and show the main window with new layout
    window = MainLayout()
    
    # Start the event loop
    window.mainloop()

if __name__ == "__main__":
    main()