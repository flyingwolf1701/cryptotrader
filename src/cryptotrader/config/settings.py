"""
Configuration module for the CryptoTrader application.
"""

import os
from dotenv import load_dotenv

from .logging import get_logger

# Get a logger for this module
logger = get_logger(__name__)

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration settings for the CryptoTrader application."""
    
    # General application settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Binance API settings
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')
    
    # Binance endpoints - Updated to Binance US
    BINANCE_BASE_URL = "https://api.binance.us"
    BINANCE_WSS_URL = "wss://stream.binance.us:9443/ws"
    
    @classmethod
    def print_config(cls):
        """Print configuration values for debugging (with minimal output)"""
        api_key_status = "✓" if cls.BINANCE_API_KEY else "✗"
        api_secret_status = "✓" if cls.BINANCE_API_SECRET else "✗"
        
        logger.info("API_KEY=%s, API_SECRET=%s", 
                   api_key_status, 
                   api_secret_status)

# Just run the print_config when this file is executed directly
if __name__ == "__main__":
    Config.print_config()