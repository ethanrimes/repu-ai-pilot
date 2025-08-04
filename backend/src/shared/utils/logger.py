# backend/src/shared/utils/logger.py
# Path: backend/src/shared/utils/logger.py

import logging
import sys
from typing import Optional
from functools import lru_cache

# Color codes for terminal output
COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[35m', # Magenta
    'RESET': '\033[0m'      # Reset
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""
    
    def format(self, record):
        # Add color to the level name
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        
        # Format the message
        result = super().format(record)
        
        # Reset the level name for other handlers
        record.levelname = levelname
        
        return result

@lru_cache(maxsize=None)
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with the specified name"""
    
    logger = logging.getLogger(name)
    
    # Only configure if logger has no handlers
    if not logger.handlers:
        # Set level from environment or default
        log_level = level or logging.INFO
        if isinstance(log_level, str):
            log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        logger.setLevel(log_level)
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        
        # Format with colors for console
        console_format = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger

# Convenience functions
def log_debug(message: str, logger_name: str = __name__):
    """Log a debug message"""
    logger = get_logger(logger_name)
    logger.debug(message)

def log_info(message: str, logger_name: str = __name__):
    """Log an info message"""
    logger = get_logger(logger_name)
    logger.info(message)

def log_warning(message: str, logger_name: str = __name__):
    """Log a warning message"""
    logger = get_logger(logger_name)
    logger.warning(message)

def log_error(message: str, logger_name: str = __name__, exc_info: bool = False):
    """Log an error message"""
    logger = get_logger(logger_name)
    logger.error(message, exc_info=exc_info)

def log_critical(message: str, logger_name: str = __name__, exc_info: bool = False):
    """Log a critical message"""
    logger = get_logger(logger_name)
    logger.critical(message, exc_info=exc_info)