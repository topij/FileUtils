"""Configuration module for FileUtils."""

from pathlib import Path
from typing import Dict, Any, Optional, Union

import yaml

from .schema import validate_config, get_default_config


def load_config(config_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Load and validate configuration.

    Args:
        config_file: Optional path to configuration file

    Returns:
        Dict[str, Any]: Validated configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    # Start with default configuration
    config = get_default_config()

    # If config file provided, load and merge with defaults
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                config.update(user_config)
            except Exception as e:
                raise ValueError(f"Error loading configuration file: {str(e)}") from e

    # Validate merged configuration
    validate_config(config)

    return config


__all__ = ["load_config", "validate_config", "get_default_config"]
