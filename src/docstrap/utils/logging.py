"""
Logging configuration for ISMS Manager.

This module provides consistent logging configuration across the application.
"""

import logging
import sys
from typing import Optional


def configure_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    date_format: Optional[str] = None,
) -> None:
    """
    Configure logging with consistent formatting.

    Args:
        level: Logging level (default: INFO)
        format_string: Optional custom format string
        date_format: Optional custom date format
    """
    if format_string is None:
        if level == logging.DEBUG:
            format_string = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        else:
            format_string = "%(message)s"

    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=level, format=format_string, datefmt=date_format, stream=sys.stdout
    )

    # Ensure error messages go to stderr
    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.WARNING)
    if format_string:
        error_handler.setFormatter(logging.Formatter(format_string, date_format))

    # Add handler to root logger
    logging.getLogger().addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Name for the logger, typically __name__

    Returns:
        Logger: Configured logger instance
    """
    return logging.getLogger(name)
