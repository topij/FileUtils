# src/FileUtils/core/enums.py

from enum import Enum, auto


class OutputFileType(Enum):
    """Supported output file types."""

    # Tabular data formats
    CSV = "csv"
    XLSX = "xlsx"
    PARQUET = "parquet"
    JSON = "json"
    YAML = "yaml"
    
    # Document formats
    DOCX = "docx"
    MARKDOWN = "md"
    PDF = "pdf"


class StorageType(Enum):
    """Supported storage backends."""

    LOCAL = "local"
    AZURE = "azure"
