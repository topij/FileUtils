# src/FileUtils/storage/__init__.py
"""Storage implementations for FileUtils."""
from .local import LocalStorage
from .azure import AzureStorage

__all__ = ["LocalStorage", "AzureStorage"]
