# src/FileUtils/utils/logging.py

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_file: Optional[Union[str, Path]] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Set up logging configuration.

    Args:
        name: Logger name
        level: Logging level (string like "INFO" or logging constant like logging.INFO)
        log_file: Optional path to log file
        format_string: Optional format string for log messages

    Returns:
        Configured logger instance

    Examples:
        >>> setup_logger("myapp", level="DEBUG")
        >>> setup_logger("myapp", level=logging.WARNING)
    """
    logger = logging.getLogger(name)

    # Determine effective log level
    if level is None:
        effective_level = logging.INFO
    elif isinstance(level, int):
        effective_level = level  # Use integer directly
    else:
        effective_level = getattr(logging, level.upper())  # Convert string to int

    logger.setLevel(effective_level)

    # Set format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_string)

    # Add console handler if none exists
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
