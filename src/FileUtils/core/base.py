# src/FileUtils/core/base.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd


class StorageError(Exception):
    """Base exception for storage-related errors."""

    pass


class StorageConnectionError(StorageError):
    """Raised when storage connection fails."""

    pass


class StorageOperationError(StorageError):
    """Raised when a storage operation fails."""

    pass


class BaseStorage(ABC):
    """Abstract base class defining storage interface."""

    @abstractmethod
    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> str:
        """Save a single DataFrame."""
        pass

    @abstractmethod
    def save_dataframes(
        self,
        dataframes: Dict[str, pd.DataFrame],
        file_path: Union[str, Path],
        file_format: str,
        **kwargs,
    ) -> Dict[str, str]:
        """Save multiple DataFrames."""
        pass

    @abstractmethod
    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load a single DataFrame."""
        pass

    @abstractmethod
    def save_with_metadata(
        self, data: Dict[str, pd.DataFrame], base_path: Path, file_format: str, **kwargs
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata."""
        pass

    @abstractmethod
    def load_from_metadata(
        self, metadata_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using metadata."""
        pass

    @abstractmethod
    def load_dataframes(
        self, file_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple DataFrames."""
        pass

    @abstractmethod
    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists in storage."""
        pass

    @abstractmethod
    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from storage."""
        pass
