import os

class Config:
    # General application settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Binance API settings
    BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET')
    
    # Binance endpoints - Updated to Binance US
    BINANCE_BASE_URL = "https://api.binance.us"
    BINANCE_WSS_URL = "wss://stream.binance.us:9443/ws"