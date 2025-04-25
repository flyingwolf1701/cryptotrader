"""
Configuration package for the CryptoTrader application.

This package contains all configuration-related modules:
- settings: Application settings and environment variables
- logging: Logging configuration
"""

from .secrets import Secrets
from .log_config import get_logger

__all__ = ['Secrets', 'get_logger']