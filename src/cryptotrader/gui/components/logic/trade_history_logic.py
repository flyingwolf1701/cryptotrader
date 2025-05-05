"""
File: src/cryptotrader/gui/components/logic/trade_history_logic.py

Trade History Logic

Handles fetching trade data and calculating PNL.
"""
from typing import List, Optional
from cryptotrader.config import get_logger
from cryptotrader.services.unified_clients.binanceRestUnifiedClient import BinanceRestUnifiedClient

logger = get_logger(__name__)

class TradeHistoryLogic:
    """Business logic for fetching trade history and calculating PNL."""

    def __init__(self, client: Optional[BinanceRestUnifiedClient] = None):
        # Use provided client or default to BinanceRestUnifiedClient
        self.client = client or BinanceRestUnifiedClient()

    def fetch_trades(self, symbol: str) -> List[dict]:
        """Fetch past trades for a symbol using Binance API."""
        try:
            trades = self.client.get_my_trades(symbol)
            logger.info(f"Fetched {len(trades)} trades for {symbol}")
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {e}")
            return []

    def calculate_pnl(self, trades: List[dict]) -> float:
        """Calculate realized PNL from a list of trades."""
        total_cost = 0.0
        total_revenue = 0.0
        for trade in trades:
            qty = float(trade.get("qty", 0))
            price = float(trade.get("price", 0))
            commission = float(trade.get("commission", 0))
            # isBuyer indicates a buy trade
            if trade.get("isBuyer", False):
                total_cost += (qty * price) + commission
            else:
                total_revenue += (qty * price) - commission
        pnl = total_revenue - total_cost
        logger.info(f"Calculated PNL: {pnl:.2f}")
        return pnl
