# src/FileUtils/utils/logging.py

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logger(
    name: str,
    level: Optional[str] = None,
    log_file: Optional[Union[str, Path]] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Set up logging configuration.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional path to log file
        format_string: Optional format string for log messages

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level (default to INFO if not specified)
    if level is None:
        level = "INFO"
    logger.setLevel(getattr(logging, level.upper()))

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
