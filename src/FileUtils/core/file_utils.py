"""Main FileUtils implementation."""
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from .base import BaseStorage

import pandas as pd
import yaml

from ..config import load_config, validate_config
from ..core.base import StorageError
from ..core.enums import OutputFileType, StorageType
from ..storage.local import LocalStorage
from ..utils.common import get_logger, format_file_path
from ..utils.logging import setup_logger


class FileUtils:
    """Main FileUtils class with storage abstraction."""

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
        storage_type: Union[str, StorageType] = StorageType.LOCAL,
        log_level: Optional[str] = None,
        **kwargs,
    ):
        """Initialize FileUtils.

        Args:
            project_root: Root directory for project
            config_file: Path to configuration file
            storage_type: Type of storage backend
            log_level: Logging level
            **kwargs: Additional arguments for storage backend
        """
        # Set up logging
        self.logger = setup_logger(__name__, log_level)

        # Load and validate configuration
        self.config = load_config(config_file)
        validate_config(self.config)

        # Set project root
        self.project_root = Path(project_root) if project_root else self._get_project_root()
        self.logger.info(f"Project root: {self.project_root}")

        # Set up directory structure
        self._setup_directory_structure()

        # Initialize storage backend
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())
        self.storage = self._create_storage(storage_type, **kwargs)

        self.logger.info(f"FileUtils initialized with {storage_type.value} storage")

    def _get_project_root(self) -> Path:
        """Determine project root directory."""
        current_dir = Path.cwd()
        root_indicators = [".git", "pyproject.toml", "setup.py"]

        while current_dir != current_dir.parent:
            if any((current_dir / indicator).exists() for indicator in root_indicators):
                return current_dir
            current_dir = current_dir.parent

        return Path.cwd()

    def _setup_directory_structure(self) -> None:
        """Create project directory structure."""
        structure = self.config["directory_structure"]
        for main_dir, sub_dirs in structure.items():
            main_path = self.project_root / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            for sub_dir in sub_dirs:
                (main_path / sub_dir).mkdir(parents=True, exist_ok=True)

    def _create_storage(self, storage_type: StorageType, **kwargs) -> BaseStorage:
        """Create storage backend instance."""
        if storage_type == StorageType.AZURE:
            try:
                from ..storage.azure import AzureStorage

                connection_string = kwargs.get("connection_string")
                if not connection_string:
                    self.logger.warning(
                        "Azure connection string not provided. Falling back to local storage."
                    )
                    return LocalStorage(self.config)
                return AzureStorage(connection_string, self.config)
            except ImportError:
                self.logger.warning(
                    "Azure storage dependencies not installed. Falling back to local storage."
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize Azure storage: {e}")
                self.logger.warning("Falling back to local storage.")

        return LocalStorage(self.config)

    def get_data_path(self, data_type: str = "raw") -> Path:
        """Get the path for a specific data directory.

        Args:
            data_type: Type of data directory (e.g., "raw", "processed")

        Returns:
            Path to the specified data directory
        """
        path = self.project_root / "data" / data_type
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_data_to_storage(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        output_filetype: Union[OutputFileType, str] = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Save data using configured storage backend.

        Args:
            data: DataFrame or dict of DataFrames to save
            output_filetype: Type of output file
            output_type: Type of output (e.g., "processed", "raw")
            file_name: Base name for output file
            include_timestamp: Whether to include timestamp in filename
            **kwargs: Additional arguments for storage backend

        Returns:
            Tuple of (saved files dict, optional metadata path)
        """
  
        if isinstance(output_filetype, str):
            output_filetype = OutputFileType(output_filetype.lower())

        # Convert single DataFrame to dict format
        if isinstance(data, pd.DataFrame):
            # Preserve sheet name if provided in kwargs, otherwise use default
            sheet_name = kwargs.get('sheet_name', 'Sheet1')
            data = {sheet_name: data}

        # For Excel files, ensure openpyxl engine
        if output_filetype == OutputFileType.XLSX and 'engine' not in kwargs:
            kwargs['engine'] = 'openpyxl'

        # Generate output path
        base_path = format_file_path(
            self.get_data_path(output_type),
            file_name or "data",
            output_filetype.value,
            include_timestamp if include_timestamp is not None else self.config.get("include_timestamp", True)
        )

        try:
            if len(data) == 1 and output_filetype != OutputFileType.XLSX:
                # For non-Excel single DataFrame
                sheet_name = next(iter(data.keys()))
                saved_path = self.storage.save_dataframe(
                    next(iter(data.values())),
                    base_path,
                    output_filetype.value,
                    sheet_name=sheet_name,  # Pass sheet name through
                    **kwargs,
                )
                saved_files = {sheet_name: saved_path}
            else:
                # For Excel or multiple DataFrames
                saved_files = self.storage.save_dataframes(
                    data, base_path, output_filetype.value, **kwargs
                )

            self.logger.info(f"Data saved successfully: {saved_files}")
            return saved_files, None

        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise StorageError(f"Failed to save data: {e}") from e

    def save_data_to_disk(self, *args, **kwargs):
        """Deprecated: Use save_data_to_storage instead."""
        warnings.warn(
            "save_data_to_disk is deprecated, use save_data_to_storage instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.save_data_to_storage(*args, **kwargs)

    def load_single_file(
        self, file_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> pd.DataFrame:
        """Load a single file from storage."""
        try:
            if not str(file_path).startswith("azure://"):
                file_path = self.project_root / "data" / input_type / file_path

            return self.storage.load_dataframe(file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {e}")
            raise StorageError(f"Failed to load file {file_path}: {e}") from e

    def load_excel_sheets(
        self, file_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load all sheets from an Excel file."""
        try:
            if not str(file_path).startswith("azure://"):
                file_path = self.project_root / "data" / input_type / file_path

            return self.storage.load_dataframes(file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to load Excel sheets from {file_path}: {e}")
            raise StorageError(f"Failed to load Excel sheets: {e}") from e

    def load_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        input_type: str = "raw",
        file_type: Optional[OutputFileType] = None,
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple files of the same type."""
        loaded_data = {}
        for file_path in file_paths:
            path = self.get_data_path(input_type) / Path(file_path)

            if file_type and path.suffix.lstrip(".") != file_type.value:
                raise ValueError(f"File {path} does not match type: {file_type.value}")

            loaded_data[path.stem] = self.load_single_file(path)

        return loaded_data

    def save_with_metadata(
        self,
        data: Dict[str, pd.DataFrame],
        output_filetype: OutputFileType = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata using configured storage."""
        base_path = format_file_path(
            self.get_data_path(output_type),
            file_name or "data",
            output_filetype.value,
            include_timestamp if include_timestamp is not None else self.config.get("include_timestamp", True)
        )

        return self.storage.save_with_metadata(
            data, base_path, output_filetype.value, **kwargs
        )

    def load_from_metadata(
        self, metadata_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using metadata file."""
        if not str(metadata_path).startswith("azure://"):
            metadata_path = self.get_data_path(input_type) / metadata_path

        return self.storage.load_from_metadata(metadata_path, **kwargs)