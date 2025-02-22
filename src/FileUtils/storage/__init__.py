# src/FileUtils/storage/__init__.py
"""Storage implementations for FileUtils."""
from .local import LocalStorage

__all__ = ["LocalStorage"]

try:
    from .azure import AzureStorage
    __all__.append("AzureStorage")
except ImportError:
    # Azure storage is optional
    pass
