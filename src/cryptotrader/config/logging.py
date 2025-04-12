"""
Centralized logging configuration for the CryptoTrader application.

This module provides a consistent logging setup across the application with colored
output and various configuration options that can be adjusted through environment
variables.
"""

import os
import sys
import logging
from logging import handlers
from typing import Dict, Optional, Union, List

# Define ANSI color codes for colored terminal output
COLORS = {
    'RESET': '\033[0m',
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
}

# Define color mapping for different log levels
LEVEL_COLORS = {
    logging.DEBUG: COLORS['BLUE'],
    logging.INFO: COLORS['GREEN'],
    logging.WARNING: COLORS['YELLOW'],
    logging.ERROR: COLORS['RED'],
    logging.CRITICAL: COLORS['BOLD'] + COLORS['RED'],
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log level names in terminal output."""
    
    def format(self, record):
        # Save original levelname
        orig_levelname = record.levelname
        # Add color to levelname based on log level
        if record.levelno in LEVEL_COLORS:
            record.levelname = f"{LEVEL_COLORS[record.levelno]}{record.levelname}{COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = orig_levelname
        return result

def get_log_level() -> int:
    """Get log level from environment variable or use INFO as default."""
    log_level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
    return getattr(logging, log_level_name, logging.INFO)

def setup_logging(
    app_name: str = "cryptotrader",
    log_to_console: bool = True,
    log_to_file: bool = False,
    log_file: Optional[str] = None,
    log_level: Optional[int] = None,
    enable_colors: Optional[bool] = None
) -> logging.Logger:
    """
    Set up application logging with consistent formatting.
    
    Args:
        app_name: The name of the application (used for logger and default log file)
        log_to_console: Whether to log to the console
        log_to_file: Whether to log to a file
        log_file: The path to the log file (if None, uses app_name.log)
        log_level: The log level to use (if None, uses environment variable or INFO)
        enable_colors: Whether to use colored output (if None, auto-detects terminal)
    
    Returns:
        A configured logger instance
    """
    # Determine the log level
    if log_level is None:
        log_level = get_log_level()
    
    # Auto-detect if colors should be enabled
    if enable_colors is None:
        # Enable colors if output is to a terminal
        enable_colors = sys.stdout.isatty()
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Remove existing handlers if any
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Define the log format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        
        if enable_colors:
            formatter = ColoredFormatter(log_format, datefmt=date_format)
        else:
            formatter = logging.Formatter(log_format, datefmt=date_format)
            
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_to_file:
        if log_file is None:
            log_file = f"{app_name}.log"
            
        # Use a rotating file handler to prevent logs from growing too large
        file_handler = handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger configured with the application's settings.
    
    Args:
        name: The name for the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)