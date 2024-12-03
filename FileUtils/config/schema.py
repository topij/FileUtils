"""Configuration schema definition and validation for FileUtils."""

from typing import Dict, Any
from jsonschema import validate, ValidationError

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "csv_delimiter": {"type": "string"},
        "encoding": {"type": "string"},
        "quoting": {"type": "integer", "minimum": 0, "maximum": 3},
        "include_timestamp": {"type": "boolean"},
        "logging_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
        "disable_logging": {"type": "boolean"},
        "parquet_compression": {"type": "string", "enum": ["snappy", "gzip", "brotli", "lz4", "zstd"]},
        "excel_engine": {"type": "string", "enum": ["openpyxl", "xlsxwriter"]},
        "directory_structure": {
            "type": "object",
            "properties": {
                "data": {"type": "array", "items": {"type": "string"}},
                "reports": {"type": "array", "items": {"type": "string"}},
                "models": {"type": "array", "items": {"type": "string"}},
                "src": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["data", "reports", "models", "src"]
        },
        "logging": {
            "type": "object",
            "properties": {
                "format": {"type": "string"},
                "date_format": {"type": "string"},
                "file_logging": {"type": "boolean"},
                "log_directory": {"type": "string"}
            }
        },
        "azure": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
                "container_mapping": {
                    "type": "object",
                    "patternProperties": {
                        "^.*$": {"type": "string"}
                    }
                },
                "retry_settings": {
                    "type": "object",
                    "properties": {
                        "max_retries": {"type": "integer", "minimum": 0},
                        "retry_delay": {"type": "integer", "minimum": 0},
                        "max_delay": {"type": "integer", "minimum": 0}
                    }
                },
                "connection_string": {"type": "string"}
            }
        },
        "error_handling": {
            "type": "object",
            "properties": {
                "raise_on_missing_file": {"type": "boolean"},
                "strict_type_checking": {"type": "boolean"},
                "auto_create_directories": {"type": "boolean"}
            }
        }
    },
    "required": [
        "csv_delimiter",
        "encoding",
        "quoting",
        "include_timestamp",
        "logging_level",
        "disable_logging",
        "directory_structure"
    ]
}

def validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration dictionary against schema.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ValidationError: If configuration is invalid
    """
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
    except ValidationError as e:
        raise ValidationError(f"Configuration validation failed: {str(e)}") from e

def get_default_config() -> Dict[str, Any]:
    """Get default configuration values.
    
    Returns:
        Dict[str, Any]: Default configuration dictionary
    """
    return {
        "csv_delimiter": ";",
        "encoding": "utf-8",
        "quoting": 0,
        "include_timestamp": True,
        "logging_level": "INFO",
        "disable_logging": False,
        "parquet_compression": "snappy",
        "excel_engine": "openpyxl",
        "directory_structure": {
            "data": ["raw", "interim", "processed", "external", "configurations"],
            "reports": ["figures", "outputs", "tables"],
            "models": ["trained", "evaluations"],
            "src": ["scripts", "notebooks"]
        },
        "logging": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "file_logging": False,
            "log_directory": "logs"
        },
        "azure": {
            "enabled": False,
            "container_mapping": {
                "raw": "raw-data",
                "processed": "processed-data",
                "interim": "interim-data",
                "parameters": "parameters",
                "configurations": "configurations"
            },
            "retry_settings": {
                "max_retries": 3,
                "retry_delay": 1,
                "max_delay": 30
            },
            "connection_string": ""
        },
        "error_handling": {
            "raise_on_missing_file": True,
            "strict_type_checking": True,
            "auto_create_directories": True
        }
    }