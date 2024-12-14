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
        directory_structure: Optional[Dict[str, Any]] = None,
        config_override: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize FileUtils with enhanced configuration support.

        Args:
            project_root: Root directory for project
            config_file: Path to configuration file
            storage_type: Type of storage backend
            log_level: Logging level
            directory_structure: Optional directory structure override
            config_override: Optional dictionary to override any config values
            **kwargs: Additional arguments for storage backend
        """
        # Set up logging
        self.logger = setup_logger(__name__, log_level)

        # Load base configuration
        self.config = self._load_configuration(
            config_file=config_file,
            directory_structure=directory_structure,
            config_override=config_override,
        )
        validate_config(self.config)

        # Set project root
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )
        self.logger.info(f"Project root: {self.project_root}")

        # Set up directory structure (only if explicitly requested)
        if kwargs.get("create_directories", False):
            self._setup_directory_structure()

        # Initialize storage backend
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())
        self.storage = self._create_storage(storage_type, **kwargs)
        self.logger.info(f"FileUtils initialized with {storage_type.value} storage")

    def _load_configuration(
        self,
        config_file: Optional[Union[str, Path]] = None,
        directory_structure: Optional[Dict[str, Any]] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Load configuration with override support.

        Args:
            config_file: Optional path to configuration file
            directory_structure: Optional directory structure override
            config_override: Optional dictionary to override any config values

        Returns:
            Dict containing merged configuration
        """
        # Start with empty config
        config = {}

        # Load from file if provided
        if config_file:
            config = load_config(config_file)
        else:
            # Load default config if no file provided
            config = self._get_default_config()

        # Override directory structure if provided
        if directory_structure:
            config["directory_structure"] = directory_structure

        # Apply any additional overrides
        if config_override:
            self._deep_merge(config, config_override)

        return config

    def _get_default_config(self) -> Dict[str, Any]:
        """Get minimal default configuration."""
        return {
            "directory_structure": {"data": ["raw", "processed"]},
            "csv_delimiter": ";",
            "encoding": "utf-8",
            "quoting": 0,
            "include_timestamp": True,
        }

    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
        """Recursively merge two dictionaries."""
        for key, value in dict2.items():
            if (
                key in dict1
                and isinstance(dict1[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(dict1[key], value)
            else:
                dict1[key] = value

    def get_directory_structure(self) -> Dict[str, Any]:
        """Get current directory structure configuration."""
        return self.config.get("directory_structure", {})

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()

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

    def create_directory(self, directory_name: str, parent_dir: str = "data") -> Path:
        """Create a new directory within the configured directory structure.

        Args:
            directory_name: Name of the new directory to create
            parent_dir: Parent directory under project root (e.g., "data", "reports", "models")

        Returns:
            Path: Path to the created directory

        Raises:
            ValueError: If parent_dir is not in configured directory structure
            StorageError: If directory creation fails
        """
        try:
            # Validate parent directory exists in config
            if parent_dir not in self.config["directory_structure"]:
                valid_parents = list(self.config["directory_structure"].keys())
                raise ValueError(
                    f"Invalid parent directory: {parent_dir}. "
                    f"Must be one of: {', '.join(valid_parents)}"
                )

            # Create new directory path
            new_dir = self.project_root / parent_dir / directory_name

            # Create directory
            new_dir.mkdir(parents=True, exist_ok=True)

            # Add to config structure if not exists
            if directory_name not in self.config["directory_structure"][parent_dir]:
                self.config["directory_structure"][parent_dir].append(directory_name)

            self.logger.info(f"Created directory: {new_dir}")
            return new_dir

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            self.logger.error(f"Failed to create directory {directory_name}: {e}")
            raise StorageError(f"Failed to create directory: {e}") from e

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
            sheet_name = kwargs.get("sheet_name", "Sheet1")
            data = {sheet_name: data}

        # For Excel files, ensure openpyxl engine
        if output_filetype == OutputFileType.XLSX and "engine" not in kwargs:
            kwargs["engine"] = "openpyxl"

        # Generate output path
        base_path = format_file_path(
            self.get_data_path(output_type),
            file_name or "data",
            output_filetype.value,
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
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
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
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

    def load_yaml(
        self, file_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> Any:
        """Load a YAML file as a Python object.

        Args:
            file_path: Name of the YAML file to load
            input_type: Type of input directory ("raw", "processed", etc.)
            **kwargs: Additional arguments passed to yaml.safe_load

        Returns:
            Any: Loaded YAML content as Python object

        Raises:
            StorageError: If loading fails
        """
        try:
            if not str(file_path).startswith("azure://"):
                file_path = self.project_root / "data" / input_type / file_path

            return self.storage.load_yaml(file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise StorageError(f"Failed to load YAML file {file_path}: {e}") from e

    def load_json(
        self, file_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> Any:
        """Load a JSON file as a Python object.

        Args:
            file_path: Name of the JSON file to load
            input_type: Type of input directory ("raw", "processed", etc.)
            **kwargs: Additional arguments passed to json.load

        Returns:
            Any: Loaded JSON content as Python object

        Raises:
            StorageError: If loading fails
        """
        try:
            if not str(file_path).startswith("azure://"):
                file_path = self.project_root / "data" / input_type / file_path

            return self.storage.load_json(file_path, **kwargs)
        except Exception as e:
            self.logger.error(f"Failed to load JSON file {file_path}: {e}")
            raise StorageError(f"Failed to load JSON file {file_path}: {e}") from e

    # def get_directory_structure(self) -> Dict[str, List[str]]:
    #     """Get the actual current directory structure by scanning the filesystem.

    #     Returns:
    #         Dict[str, List[str]]: Dictionary mapping parent directories to their existing subdirectories

    #     Example:
    #         >>> file_utils.get_directory_structure()
    #         {
    #             'data': ['raw', 'processed', 'interim', 'features'],
    #             'reports': ['figures', 'monthly'],
    #             'models': ['trained']
    #         }
    #     """
    #     structure = {}

    #     # Scan through base directories defined in config
    #     for parent_dir in self.config["directory_structure"].keys():
    #         parent_path = self.project_root / parent_dir

    #         # Skip if parent directory doesn't exist
    #         if not parent_path.exists():
    #             continue

    #         # Get all existing subdirectories
    #         subdirs = [
    #             path.name
    #             for path in parent_path.iterdir()
    #             if path.is_dir()
    #             and not path.name.startswith(".")  # Skip hidden directories
    #         ]

    #         structure[parent_dir] = sorted(subdirs)  # Sort for consistent order

    #     return structure

    def set_logging_level(self, level: str) -> None:
        """Set the logging level after initialization.

        Args:
            level: Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

        Raises:
            ValueError: If invalid logging level provided
        """
        try:
            # Validate logging level
            level = level.upper()
            if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                raise ValueError(
                    f"Invalid logging level: {level}. "
                    "Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
                )

            # Update logger level
            self.logger.setLevel(level)

            # Update config
            self.config["logging_level"] = level

            self.logger.info(f"Logging level set to: {level}")

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to set logging level: {e}")
