"""
Configuration package for the CryptoTrader application.

This package contains all configuration-related modules:
- settings: Application settings and environment variables
- logging: Logging configuration
"""

from .settings import Config
from .logging import setup_logging, get_logger

__all__ = ['Config', 'setup_logging', 'get_logger']