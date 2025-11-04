"""Common utility functions."""

import logging
import warnings
from pathlib import Path
from typing import Optional, Union

from .logging import setup_logger


def ensure_path(path: Union[str, Path]) -> Path:
    """Convert string to Path and ensure it exists."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Deprecated: use utils.logging.setup_logger.

    Kept for backward compatibility and emits a deprecation warning.
    """
    warnings.warn(
        "utils.common.get_logger is deprecated; use utils.logging.setup_logger",
        DeprecationWarning,
        stacklevel=2,
    )
    return setup_logger(name=name, level=level)


def format_file_path(
    base_path: Union[str, Path],
    file_name: str,
    extension: str,
    include_timestamp: bool = False,
) -> Path:
    """Create standardized file path with optional timestamp."""
    path = ensure_path(base_path)
    if not file_name.endswith(f".{extension}"):
        file_name = f"{file_name}.{extension}"
    if include_timestamp:
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{Path(file_name).stem}_{timestamp}{Path(file_name).suffix}"
    return path / file_name
