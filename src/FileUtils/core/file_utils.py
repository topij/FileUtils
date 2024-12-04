# src/FileUtils/core/file_utils.py

import logging
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import yaml
import json

from .base import BaseStorage, StorageError
from .enums import OutputFileType, StorageType
from ..storage.local import LocalStorage
from ..storage.azure import AzureStorage
from ..utils.logging import setup_logger
from ..config.schema import CONFIG_SCHEMA
from ..config import DEFAULT_CONFIG


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
            storage_type: Type of storage backend to use
            log_level: Logging level
            **kwargs: Additional arguments passed to storage backend
        """
        # Set up logging first
        self.logger = setup_logger(__name__, log_level)

        # Load configuration
        self.config = self._load_initial_config(config_file)

        # Set project root
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )

        # Set up directory structure
        self._setup_directory_structure()

        # Initialize storage backend
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())

        self.storage = self._create_storage(storage_type, **kwargs)

        self.logger.info(f"FileUtils initialized with {storage_type.value} storage")

    def _load_initial_config(
        self, config_file: Optional[Union[str, Path]] = None
    ) -> Dict:
        """Load initial configuration."""
        try:
            from ..config import get_default_config, validate_config

            # Get default config
            config = get_default_config()

            # Load and validate user config if provided
            if config_file:
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        user_config = yaml.safe_load(f) or {}
                    validate_config(user_config)
                    config.update(user_config)
                except Exception as e:
                    self.logger.warning(
                        f"Error loading configuration file {config_file}: {e}. "
                        "Using default values."
                    )

            return config
        except ImportError as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return DEFAULT_CONFIG  # Fallback to embedded defaults

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
                return LocalStorage(self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize Azure storage: {e}")
                self.logger.warning("Falling back to local storage.")
                return LocalStorage(self.config)

        return LocalStorage(self.config)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name."""
        return logging.getLogger(name)

    def get_data_path(self, data_type: str = "raw") -> Path:
        """Get the path for a specific data type directory.

        Args:
            data_type: Type of data directory (e.g., "raw", "processed").

        Returns:
            Path: Full path to the specified data directory

        Examples:
            >>> file_utils = FileUtils()
            >>> raw_path = file_utils.get_data_path("raw")
            >>> processed_path = file_utils.get_data_path("processed")
        """
        path = self.project_root / "data" / data_type
        if not path.exists():
            self.logger.warning(f"Data path {path} does not exist. Creating it.")
            path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_output_path(
        self,
        file_name: str,
        output_type: str,
        extension: str,
        include_timestamp: Optional[bool] = None,
    ) -> Path:
        """Generate output file path."""
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )

        file_path = Path(file_name)
        if not file_path.suffix or file_path.suffix.lower() != f".{extension}":
            file_path = file_path.with_suffix(f".{extension}")

        # Use get_data_path for consistent path handling
        data_dir = self.get_data_path(output_type)

        # Construct final path
        if timestamp:
            return data_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        return data_dir / file_path

    def save_data_to_storage(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List, Dict]], pd.DataFrame],
        output_filetype: Union[OutputFileType, str] = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Save data using configured storage backend.

        Args:
            data: Data to save (DataFrame or dict of DataFrames)
            output_filetype: Type of output file
            output_type: Type of output (e.g., "processed", "raw")
            file_name: Base name for output file
            include_timestamp: Whether to include timestamp in filename
            **kwargs: Additional arguments passed to storage backend

        Returns:
            Tuple of (saved files dict, optional metadata path)
        """
        if isinstance(output_filetype, str):
            output_filetype = OutputFileType(output_filetype.lower())

        # Convert single DataFrame to dict format
        if isinstance(data, pd.DataFrame):
            data = {"data": data}

        # Generate output path
        base_path = self._get_output_path(
            file_name or "data", output_type, output_filetype.value, include_timestamp
        )

        try:
            # Save data using appropriate method
            if len(data) == 1:
                saved_path = self.storage.save_dataframe(
                    next(iter(data.values())),
                    base_path,
                    output_filetype.value,
                    **kwargs,
                )
                saved_files = {next(iter(data.keys())): saved_path}
            else:
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
        """Load a single file from storage.

        Args:
            file_path: Path to file
            input_type: Type of input (e.g., "raw", "processed")
            **kwargs: Additional arguments passed to storage backend

        Returns:
            Loaded DataFrame
        """
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
        """Load all sheets from an Excel file.

        Args:
            file_path: Path to Excel file
            input_type: Type of input
            **kwargs: Additional arguments passed to storage backend

        Returns:
            Dict of sheet names to DataFrames
        """
        try:
            if not str(file_path).startswith("azure://"):
                file_path = self.project_root / "data" / input_type / file_path

            return self.storage.load_dataframes(file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to load Excel sheets from {file_path}: {e}")
            raise StorageError(f"Failed to load Excel sheets: {e}") from e

    def load_data_from_metadata(
        self, metadata_file: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple files based on metadata."""
        metadata = self.load_json(metadata_file, input_type)
        loaded_data = {}

        for data_type, file_info in metadata.get("files", {}).items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            loaded_data[data_type] = self.load_single_file(file_path)

        return loaded_data

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

            if file_type:
                if path.suffix.lower().lstrip(".") != file_type.value:
                    raise ValueError(
                        f"File {path} does not match type: {file_type.value}"
                    )

            loaded_data[path.stem] = self.load_single_file(path)

        return loaded_data

    def _load_json(self, file_path: Path) -> pd.DataFrame:
        """Load JSON file."""
        with open(file_path, "r", encoding=self.config["encoding"]) as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """Load Excel file."""
        return pd.read_excel(file_path, engine="openpyxl")

    def _load_parquet(self, file_path: Path) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(file_path)

    def save_json(
        self,
        data: Union[Dict[str, Any], List[Any]],
        file_path: Union[str, Path],
        output_type: str = "processed",
        include_timestamp: Optional[bool] = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Path:
        """Save data to JSON."""
        output_path = self._get_output_path(
            file_path, output_type, "json", include_timestamp
        )

        with open(output_path, "w", encoding=self.config["encoding"]) as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)

        return output_path

    def save_yaml(
        self,
        data: Dict[str, Any],
        file_path: Union[str, Path],
        output_type: str = "processed",
        include_timestamp: Optional[bool] = None,
        default_flow_style: bool = False,
        sort_keys: bool = False,
    ) -> Path:
        """Save data to YAML."""
        output_path = self._get_output_path(
            file_path, output_type, "yaml", include_timestamp
        )

        with open(output_path, "w", encoding=self.config["encoding"]) as f:
            yaml.dump(
                data,
                f,
                default_flow_style=default_flow_style,
                sort_keys=sort_keys,
                allow_unicode=True,
            )

        return output_path

    def load_yaml(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        safe_load: bool = True,
    ) -> Dict[str, Any]:
        """Load YAML file."""
        yaml_path = (
            file_path
            if isinstance(file_path, Path) and file_path.is_absolute()
            else self.get_data_path(input_type) / Path(file_path)
        )

        with open(yaml_path, "r", encoding=self.config["encoding"]) as f:
            data = (
                yaml.safe_load(f) if safe_load else yaml.load(f, Loader=yaml.FullLoader)
            )
        return data or {}

    def save_dataframes_to_excel(
        self,
        dataframes_dict: Dict[str, pd.DataFrame],
        file_name: str,
        output_type: str = "reports",
        parameters_dict: Optional[Dict] = None,
        include_timestamp: Optional[bool] = None,
        keep_index: bool = False,
    ) -> Path:
        """Save multiple DataFrames to Excel with optional parameters."""
        file_path = self._get_output_path(
            file_name, output_type, "xlsx", include_timestamp
        )

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, df in dataframes_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=keep_index)

            if parameters_dict:
                params_df = pd.DataFrame.from_dict(
                    parameters_dict,
                    orient="index",
                    columns=["Value", "Comment"],
                )
                params_df.reset_index(inplace=True)
                params_df.rename(columns={"index": "Parameter Name"}, inplace=True)
                params_df.to_excel(writer, sheet_name="Parameters", index=False)

        return file_path

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
        base_path = self._get_output_path(
            file_name or "data", output_type, output_filetype.value, include_timestamp
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
