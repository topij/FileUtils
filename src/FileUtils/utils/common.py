"""Common utility functions."""
from pathlib import Path
from typing import Union, Optional
import logging

def ensure_path(path: Union[str, Path]) -> Path:
    """Convert string to Path and ensure it exists."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get or create a logger with consistent formatting."""
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def format_file_path(
    base_path: Union[str, Path],
    file_name: str,
    extension: str,
    include_timestamp: bool = False
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