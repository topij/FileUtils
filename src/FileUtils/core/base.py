"""Base storage implementation and exceptions."""
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pandas as pd
import json

from ..utils.common import get_logger


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class StorageConnectionError(StorageError):
    """Storage connection failure."""
    pass


class StorageOperationError(StorageError):
    """Storage operation failure."""
    pass


class BaseStorage(ABC):
    """Abstract base class for storage implementations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize storage.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> str:
        """Save a single DataFrame.
        
        Args:
            df: DataFrame to save
            file_path: Output path
            file_format: File format (csv, parquet, etc.)
            **kwargs: Additional format-specific arguments
            
        Returns:
            str: Path where file was saved
        """
        pass

    @abstractmethod
    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load a single DataFrame.
        
        Args:
            file_path: Path to file
            **kwargs: Additional format-specific arguments
            
        Returns:
            pd.DataFrame: Loaded data
        """
        pass

    def save_dataframes(
        self,
        dataframes: Dict[str, pd.DataFrame],
        file_path: Union[str, Path],
        file_format: str,
        **kwargs,
    ) -> Dict[str, str]:
        """Save multiple DataFrames."""
        saved_files = {}
        base_path = Path(file_path)

        if file_format == "xlsx":
            # Special handling for Excel files with proper engine and sheet names
            engine = kwargs.get('engine', 'openpyxl') 
            try:
                with pd.ExcelWriter(base_path, engine=engine) as writer:
                    for sheet_name, df in dataframes.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                saved_files[base_path.stem] = str(base_path)
                self.logger.info(f"Saved Excel file with sheets: {list(dataframes.keys())}")
            except Exception as e:
                raise StorageError(f"Failed to save Excel file: {e}") from e
        else:
            # Save individual files
            for name, df in dataframes.items():
                file_path = base_path.parent / f"{base_path.stem}_{name}.{file_format}"
                saved_path = self.save_dataframe(df, file_path, file_format)
                saved_files[name] = saved_path

        return saved_files

    def load_dataframes(
        self, file_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple DataFrames.
        
        Default implementation for multiple files. Override for format-specific handling.
        """
        path = Path(file_path)
        if path.suffix.lower() in (".xlsx", ".xls"):
            return pd.read_excel(path, sheet_name=None, engine="openpyxl")

        # For other formats, assume multiple files with pattern
        pattern = f"{path.stem}_*.{path.suffix}"
        dataframes = {}
        for file in path.parent.glob(pattern):
            name = file.stem.replace(f"{path.stem}_", "")
            dataframes[name] = self.load_dataframe(file)
        return dataframes

    def save_with_metadata(
        self,
        data: Dict[str, pd.DataFrame],
        base_path: Path,
        file_format: str,
        **kwargs,
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata.
        
        Args:
            data: Dictionary of DataFrames
            base_path: Base path for saving
            file_format: File format to use
            **kwargs: Additional arguments
            
        Returns:
            Tuple of (saved files dict, metadata path)
        """
        saved_files = self.save_dataframes(data, base_path, file_format)
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "files": {k: {"path": v, "format": file_format} for k, v in saved_files.items()},
            "config": self.config
        }

        metadata_path = base_path.parent / f"{base_path.stem}_metadata.json"
        with open(metadata_path, "w", encoding=self.config["encoding"]) as f:
            json.dump(metadata, f, indent=2)

        return saved_files, str(metadata_path)

    def load_from_metadata(
        self, metadata_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using metadata file.
        
        Args:
            metadata_path: Path to metadata file
            **kwargs: Additional arguments
            
        Returns:
            Dict[str, pd.DataFrame]: Loaded data
        """
        with open(metadata_path, "r", encoding=self.config["encoding"]) as f:
            metadata = json.load(f)

        data = {}
        for key, file_info in metadata["files"].items():
            file_path = Path(file_info["path"])
            data[key] = self.load_dataframe(file_path)

        return data

    @abstractmethod
    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        pass

    @abstractmethod
    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from storage."""
        pass