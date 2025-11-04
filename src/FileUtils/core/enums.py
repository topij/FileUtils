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
    PPTX = "pptx"


class StorageType(Enum):
    """Supported storage backends."""

    LOCAL = "local"
    AZURE = "azure"


class InputType(Enum):
    """Typed input directory areas to avoid magic strings."""

    RAW = "raw"
    PROCESSED = "processed"
    TEMPLATES = "templates"
    CONFIG = "config"
    LOGS = "logs"


class OutputArea(Enum):
    """Typed output directory areas to avoid magic strings."""

    RAW = "raw"
    PROCESSED = "processed"
    TEMPLATES = "templates"
    CONFIG = "config"
    LOGS = "logs"
