import time
from typing import List, Dict
from cryptotrader.config import get_logger

logger = get_logger(__name__)


class LoggingLogic:
    """Handles logging operations separate from the UI."""

    def __init__(self):
        self.logs: List[Dict] = []

    def add_log(self, message: str, level: str = "INFO") -> Dict:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {"timestamp": timestamp, "level": level.upper(), "message": message}
        self.logs.append(log_entry)

        if level.upper() == "ERROR":
            logger.error(message)
        elif level.upper() == "WARNING":
            logger.warning(message)
        elif level.upper() == "SUCCESS":
            logger.info(f"[SUCCESS] {message}")
        else:
            logger.info(message)

        return log_entry

    def clear_logs(self):
        self.logs.clear()

    def get_all_logs(self) -> List[Dict]:
        return list(self.logs)
