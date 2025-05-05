#!/usr/bin/env python3
"""
CryptoTrader Application Entry Point

This script initializes the application and starts the main UI using
 the new layout system.
"""

from cryptotrader.config import get_logger
from cryptotrader.gui.main_layout import MainLayout

# Initialize logger for this module
logger = get_logger(__name__)

def main() -> None:
    """Application entry point."""
    logger.info("Starting CryptoTrader Application")

    # Create and display the main application window
    window = MainLayout()
    window.mainloop()


if __name__ == "__main__":
    main()
