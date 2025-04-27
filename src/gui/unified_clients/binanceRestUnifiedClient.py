"""
Binance REST API Unified Client

This module provides a unified client for interacting with the Binance REST API.
It combines the functionality from:
- Market data operations
- Order operations
- Wallet operations
- User account operations

The client automatically handles authentication and rate limiting through
the underlying implementation in base_operations.
"""

from typing import Dict, List, Optional, Any, Union

from config import get_logger