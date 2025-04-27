"""Logging utilities"""

import logging
from typing import Optional

try:
    from termcolor import colored
except ImportError:
    def colored(text, color):
        """Fallback if termcolor is not available"""
        return text

def setup_logging() -> logging.Logger:
    """Configure application-wide logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    return get_logger("remote_control")

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(name or "remote_control")
