# """Configuration schema definition and validation for FileUtils."""

# from typing import Dict, Any
# from jsonschema import validate, ValidationError

# src/FileUtils/config/schema.py

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "csv_delimiter": {"type": "string"},
        "encoding": {"type": "string"},
        "quoting": {"type": "integer", "minimum": 0, "maximum": 3},
        "include_timestamp": {"type": "boolean"},
        "logging_level": {"type": "string"},
        "directory_structure": {
            "type": "object",
            "additionalProperties": {"type": "array", "items": {"type": "string"}},
        },
        "logging": {
            "type": "object",
            "properties": {
                "format": {"type": "string"},
                "date_format": {"type": "string"},
                "file_logging": {"type": "boolean"},
                "log_directory": {"type": "string"},
            },
        },
        "storage": {
            "type": "object",
            "properties": {
                "default_type": {"type": "string", "enum": ["local", "azure"]},
                "azure": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "container_mapping": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                        "retry_settings": {
                            "type": "object",
                            "properties": {
                                "max_retries": {"type": "integer", "minimum": 0},
                                "retry_delay": {"type": "integer", "minimum": 0},
                                "max_delay": {"type": "integer", "minimum": 0},
                            },
                        },
                    },
                },
            },
        },
    },
}


# def validate_config(config: Dict[str, Any]) -> None:
#     """Validate configuration dictionary against schema.

#     Args:
#         config: Configuration dictionary to validate

#     Raises:
#         ValidationError: If configuration is invalid
#     """
#     try:
#         validate(instance=config, schema=CONFIG_SCHEMA)
#     except ValidationError as e:
#         raise ValidationError(f"Configuration validation failed: {str(e)}") from e


# def get_default_config() -> Dict[str, Any]:
#     """Get default configuration values.

#     Returns:
#         Dict[str, Any]: Default configuration dictionary
#     """
#     return {
#         "csv_delimiter": ";",
#         "encoding": "utf-8",
#         "quoting": 0,
#         "include_timestamp": True,
#         "logging_level": "INFO",
#         "disable_logging": False,
#         "parquet_compression": "snappy",
#         "excel_engine": "openpyxl",
#         "directory_structure": {
#             "data": ["raw", "interim", "processed", "external", "configurations"],
#             "reports": ["figures", "outputs", "tables"],
#             "models": ["trained", "evaluations"],
#             "src": ["scripts", "notebooks"],
#         },
#         "logging": {
#             "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#             "date_format": "%Y-%m-%d %H:%M:%S",
#             "file_logging": False,
#             "log_directory": "logs",
#         },
#         "azure": {
#             "enabled": False,
#             "container_mapping": {
#                 "raw": "raw-data",
#                 "processed": "processed-data",
#                 "interim": "interim-data",
#                 "parameters": "parameters",
#                 "configurations": "configurations",
#             },
#             "retry_settings": {"max_retries": 3, "retry_delay": 1, "max_delay": 30},
#             "connection_string": "",
#         },
#         "error_handling": {
#             "raise_on_missing_file": True,
#             "strict_type_checking": True,
#             "auto_create_directories": True,
#         },
#     }
