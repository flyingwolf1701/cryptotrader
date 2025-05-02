from typing import Dict, List, Optional

class StrategyLogic:
    """Business logic for managing trading strategies."""

    def __init__(self):
        self.available_symbols: List[str] = []
        self.active_strategies: Dict[int, Dict] = {}
        self.strategy_parameters: Dict[int, Dict] = {}

        self.strategy_types = ["Technical", "Breakout"]
        self.timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

    def set_available_symbols(self, symbols: List[str]):
        self.available_symbols = sorted(symbols)

    def add_strategy(self, row_id: int) -> Dict:
        default_symbol = self.available_symbols[0] if self.available_symbols else "BTCUSDT"
        self.active_strategies[row_id] = {
            "strategy_type": self.strategy_types[0],
            "symbol": default_symbol,
            "timeframe": "1h",
            "balance_pct": "10",
            "tp_pct": "2",
            "sl_pct": "1",
            "status": "INACTIVE",
            "is_active": False,
        }
        self.strategy_parameters[row_id] = {}
        return self.active_strategies[row_id]

    def delete_strategy(self, row_id: int):
        self.active_strategies.pop(row_id, None)
        self.strategy_parameters.pop(row_id, None)

    def update_strategy_field(self, row_id: int, field: str, value):
        if row_id in self.active_strategies:
            self.active_strategies[row_id][field] = value

    def save_parameters(self, row_id: int, params: Dict):
        self.strategy_parameters[row_id] = params

    def toggle_strategy(self, row_id: int) -> bool:
        if row_id not in self.active_strategies:
            return False

        strategy = self.active_strategies[row_id]
        strategy["is_active"] = not strategy["is_active"]
        strategy["status"] = "ACTIVE" if strategy["is_active"] else "INACTIVE"
        return strategy["is_active"]

    def validate_strategy(self, row_id: int) -> Optional[str]:
        strategy = self.active_strategies.get(row_id)
        params = self.strategy_parameters.get(row_id)

        if not strategy:
            return "Strategy not found."

        try:
            balance_pct = float(strategy["balance_pct"])
            if balance_pct <= 0 or balance_pct > 100:
                return "Balance percentage must be between 0 and 100."

            tp_pct = float(strategy["tp_pct"])
            if tp_pct <= 0:
                return "Take profit must be greater than 0."

            sl_pct = float(strategy["sl_pct"])
            if sl_pct <= 0:
                return "Stop loss must be greater than 0."
        except ValueError:
            return "Invalid numeric input."

        if not params:
            return "Strategy parameters not set."

        if strategy["strategy_type"] == "Technical":
            required = ["ema_fast", "ema_slow", "ema_signal"]
            if not all(r in params for r in required):
                return "Missing MACD parameters."

        if strategy["strategy_type"] == "Breakout":
            if "min_volume" not in params:
                return "Missing Breakout minimum volume parameter."

        return None

    def start_strategy(self, row_id: int) -> bool:
        """Placeholder: Start executing the trading strategy."""
        pass

    def stop_strategy(self, row_id: int) -> bool:
        """Placeholder: Stop executing the trading strategy."""
        pass
