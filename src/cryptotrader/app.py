from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from services.binance_client import Client
from models.binance_models import PriceData, Candle, AccountBalance

# Create FastAPI app
app = FastAPI(
    title="Crypto Trader API",
    description="A FastAPI service for interacting with the Binance API",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Binance client
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Dependency to get Binance client
def get_binance_client():
    if not BINANCE_API_KEY or not BINANCE_API_SECRET:
        raise HTTPException(
            status_code=500, 
            detail="API credentials not configured. Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables."
        )
    return Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# Root endpoint
@app.get("/")
async def root():
    return {"status": "success", "message": "Binance API is running"}

# API endpoints
@app.get("/api/symbols")
async def get_symbols():
    symbols = Client.get_symbols_binance()
    return {"status": "success", "data": symbols}

@app.get("/api/price/{symbol}")
async def get_price(symbol: str, client: Client = Depends(get_binance_client)):
    price_data = client.get_bid_ask(symbol.upper())
    
    if price_data:
        return {
            "status": "success",
            "data": {
                "symbol": symbol.upper(),
                "bid": price_data.bid,
                "ask": price_data.ask
            }
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to retrieve price for {symbol}"
        )

@app.get("/api/candles/{symbol}/{interval}")
async def get_candles(
    symbol: str, 
    interval: str, 
    client: Client = Depends(get_binance_client)
):
    candles = client.get_historical_candles(symbol.upper(), interval)
    
    if candles:
        return {
            "status": "success",
            "data": [
                {
                    "timestamp": c.timestamp,
                    "open": c.open_price,
                    "high": c.high_price,
                    "low": c.low_price,
                    "close": c.close_price,
                    "volume": c.volume,
                    "quote_volume": c.quote_volume
                } for c in candles
            ]
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to retrieve candles for {symbol}"
        )

@app.get("/api/balance")
async def get_balance(client: Client = Depends(get_binance_client)):
    balance = client.get_balance()
    
    if balance and balance.assets:
        # Filter non-zero assets
        non_zero_assets = {
            asset: {
                "free": data.free,
                "locked": data.locked
            } 
            for asset, data in balance.assets.items() 
            if float(data.free) > 0 or float(data.locked) > 0
        }
        
        return {
            "status": "success",
            "data": non_zero_assets
        }
    else:
        raise HTTPException(
            status_code=400, 
            detail="Failed to retrieve account balance"
        )