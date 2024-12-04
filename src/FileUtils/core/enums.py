# src/FileUtils/core/enums.py

from enum import Enum, auto


class OutputFileType(Enum):
    """Supported output file types."""

    CSV = "csv"
    XLSX = "xlsx"
    PARQUET = "parquet"
    JSON = "json"
    YAML = "yaml"


class StorageType(Enum):
    """Supported storage backends."""

    LOCAL = "local"
    AZURE = "azure"
