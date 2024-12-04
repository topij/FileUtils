# src/FileUtils/config/__init__.py

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from jsonschema import validate

from .schema import CONFIG_SCHEMA
from .defaults import DEFAULT_CONFIG


def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration against schema.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If configuration is invalid
    """
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {str(e)}") from e


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    default_config_path = Path(__file__).parent / "default_config.yaml"

    with open(default_config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(
    config_file: Optional[Union[str, Path]] = None, validate_schema: bool = True
) -> Dict[str, Any]:
    """Load and validate configuration.

    Args:
        config_file: Path to configuration file
        validate_schema: Whether to validate against schema

    Returns:
        Configuration dictionary
    """
    # Start with default configuration
    config = get_default_config()

    # Load user configuration if provided
    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}

                # Validate user config if requested
                if validate_schema:
                    validate_config(user_config)

                config.update(user_config)
            except Exception as e:
                raise ValueError(f"Error loading configuration file: {e}") from e

    return config


__all__ = ["DEFAULT_CONFIG", "get_default_config", "validate_config", "load_config"]
