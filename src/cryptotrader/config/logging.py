"""
Centralized logging configuration for the CryptoTrader application.

This module provides a consistent logging setup across the application with colored
output and configuration options that can be adjusted through environment variables.
"""

import os
import sys
import logging

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

# Configure root logger with colored formatting
log_level_name = os.environ.get('LOG_LEVEL', 'INFO').upper()
log_level = getattr(logging, log_level_name, logging.INFO)

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)

# Define the log format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Use colored formatting if output is to a terminal
if sys.stdout.isatty():
    formatter = ColoredFormatter(log_format, datefmt=date_format)
else:
    formatter = logging.Formatter(log_format, datefmt=date_format)

console_handler.setFormatter(formatter)

# Only add handler if it hasn't been added already
if not root_logger.handlers:
    root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the application's settings.
    
    Args:
        name: The name for the logger, typically __name__
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)