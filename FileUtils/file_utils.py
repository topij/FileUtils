"""
FileUtils module

Version: 0.4.5
Author: Your Name
Date: 2023-12-03

This module provides a utility class `FileUtils` for handling file operations in data science projects. 
It includes methods for loading, saving, and managing data files and directory structures.

Optional support for Azure Blob Storage

Classes:
    - OutputFileType: Enum for supported output file types.
    - FileUtils: Utility class for file operations.

Functions:
    - main: Command-line interface for setting up directory structures and testing logging.

Usage:
    >>> from file_utils import FileUtils, OutputFileType'''

"""

__version__ = "0.4.5"
__author__ = "Topi Järvinen"

import argparse
import csv
import json
import logging
import logging.config
from datetime import datetime
from enum import Enum
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import yaml
from jsonschema import ValidationError, validate
from yaml.parser import ParserError
from yaml.scanner import ScannerError

DEFAULT_CONFIG = {
    "csv_delimiter": ";",
    "encoding": "utf-8",
    "quoting": csv.QUOTE_MINIMAL,
    "include_timestamp": True,
    "logging_level": "INFO",
    "disable_logging": False,
    "directory_structure": {
        "data": ["raw", "interim", "processed", "configurations"],
        "reports": ["figures", "outputs"],
        "models": [],
        "src": [],
    },
}

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "csv_delimiter": {"type": "string"},
        "encoding": {"type": "string"},
        "quoting": {"type": "integer"},
        "include_timestamp": {"type": "boolean"},
        "logging_level": {"type": "string"},
        "disable_logging": {"type": "boolean"},
        "directory_structure": {"type": "object"},
    },
    "required": [
        "csv_delimiter",
        "encoding",
        "quoting",
        "include_timestamp",
        "logging_level",
        "disable_logging",
    ],
}


class OutputFileType(Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PARQUET = "parquet"
    JSON = "json"
    YAML = "yaml"


class FileUtils:
    """
    A utility class for handling file operations in data science projects.

    This class provides methods for loading, saving, and backing up data files,
    as well as managing directory structures for data science projects.

    Attributes:
        project_root (Path): The root directory of the project.
        config (dict): Configuration settings for file operations.
    """

    CSV_DELIMITERS = [",", ";", "\t", "|"]

    @staticmethod
    def _load_initial_config(config_file: Optional[Union[str, Path]] = None) -> Dict:
        """
        Load initial configuration without using class methods.
        This is used during initialization before the logger is set up.

        Args:
            config_file: Path to the configuration file

        Returns:
            Dict: Configuration dictionary
        """
        config = DEFAULT_CONFIG.copy()

        if config_file is None:
            return config

        config_path = Path(config_file)
        if not config_path.exists():
            return config

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}

            validate(instance=user_config, schema=CONFIG_SCHEMA)
            config.update(user_config)
        except Exception as e:
            print(
                f"Warning: Error loading configuration file {config_file}: {e}. Using default values."
            )

        return config

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
        log_level: Optional[str] = None,
    ) -> None:
        """Initialize FileUtils.

        Args:
            project_root: Optional project root directory
            config_file: Optional configuration file path
            log_level: Optional logging level (e.g., "DEBUG", "INFO")
                      If provided, overrides the level from config
        """
        """Initialize FileUtils."""
        # Set project root first
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )

        # Load initial configuration
        self.config = self._load_initial_config(config_file)

        # Get current root logger level if none specified
        if log_level is None:
            root_logger = logging.getLogger()
            current_level = logging.getLevelName(root_logger.getEffectiveLevel())
            log_level = current_level

        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            # Only set up handler if none exists
            handler = logging.StreamHandler()
            handler.setLevel(log_level)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s [%(filename)s:%(lineno)d] - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Set logger level but don't modify root logger
        self.logger.setLevel(log_level)

        # Create a temporary logger for initialization messages
        # self.logger = logging.getLogger(__name__)

        # Override config logging level if provided
        # if log_level:
        #     if "logging" not in self.config:
        #         self.config["logging"] = {}
        #     self.config["logging"]["level"] = log_level

        # # Set up logging
        # self._setup_logging()

        # self.logger = logging.getLogger(__name__)
        self.logger.debug(
            "Initialized FileUtils with log level: %s",
            self.config.get("logging", {}).get("level", "INFO"),
        )

        # Log initial information
        self.logger.debug(f"Project root: {self.project_root}")

        # Set up directory structure
        self._setup_directory_structure()

        # Now that everything is set up, we can load the full configuration
        if config_file:
            self.config = self._load_config(config_file)

    @staticmethod
    def _get_project_root() -> Path:
        """Attempt to automatically determine the project root."""
        current_dir = Path.cwd()
        root_indicators = [
            "config.yaml",
            "main.py",
            ".env",
            "pyproject.toml",
            ".git",
        ]
        while current_dir != current_dir.parent:
            if any((current_dir / indicator).exists() for indicator in root_indicators):
                return current_dir
            current_dir = current_dir.parent
        return Path.cwd()

    def _load_config(self, config_file: Union[str, Path]) -> Dict:
        """
        Load full configuration from a YAML file after logger is initialized.

        Args:
            config_file: Path to the configuration file

        Returns:
            Dict: Updated configuration dictionary
        """
        try:
            config_path = Path(config_file)
            with open(config_path, "r", encoding=self.config["encoding"]) as f:
                user_config = yaml.safe_load(f) or {}

            validate(instance=user_config, schema=CONFIG_SCHEMA)
            self.config.update(user_config)
            self.logger.debug(f"Loaded configuration from {config_file}")
        except Exception as e:
            self.logger.warning(
                f"Error loading configuration file {config_file}: {e}. "
                "Keeping existing configuration."
            )

        return self.config

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        # Get logging config
        log_config = self.config.get("logging", {})

        # Get level from config (with default fallback)
        level_str = log_config.get("level", "INFO")

        # Convert string level to numeric
        try:
            level = getattr(logging, level_str.upper())
        except (AttributeError, TypeError):
            self.logger.warning(f"Invalid logging level '{level_str}', using INFO")
            level = logging.INFO

        # Configure root logger if handlers don't exist
        root_logger = logging.getLogger()

        if not root_logger.handlers:
            # Set up handler
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                log_config.get(
                    "format",
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                ),
                datefmt=log_config.get("date_format", "%Y-%m-%d %H:%M:%S"),
            )
            handler.setFormatter(formatter)
            handler.setLevel(level)
            root_logger.addHandler(handler)

        # Always set the root logger level
        root_logger.setLevel(level)
        # Also set level for any existing handlers
        for handler in root_logger.handlers:
            handler.setLevel(level)

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name, configured according to the FileUtils settings.

        Args:
            name (str): Name of the logger, typically __name__ of the calling module.

        Returns:
            logging.Logger: Configured logger instance.
        """
        return logging.getLogger(name)

    def _setup_directory_structure(self) -> None:
        """Set up the project directory structure based on configuration."""
        directory_structure = self.config.get("directory_structure", {})
        for main_dir, sub_dirs in directory_structure.items():
            main_path = self.project_root / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            for sub_dir in sub_dirs:
                (main_path / sub_dir).mkdir(parents=True, exist_ok=True)

    def get_data_path(self, data_type: str = "raw") -> Path:
        """
        Get the path for a specific data type directory.

        Args:
            data_type (str): Type of data directory (e.g., "raw", "processed").

        Returns:
            Path: Path to the specified data directory.
        """
        path = self.project_root / "data" / data_type
        if not path.exists():
            self.logger.warning(f"Data path {path} does not exist. Creating it.")
            path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_output_path(
        self,
        file_path: Union[str, Path],
        output_type: str,
        extension: str,
        include_timestamp: Optional[bool] = None,
    ) -> Path:
        """
        Utility method to generate output file paths with consistent timestamp handling.

        Args:
            file_path: Base file path
            output_type: Type of output directory
            extension: File extension (without dot)
            include_timestamp: Whether to include timestamp

        Returns:
            Path: Complete output path
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        file_path = Path(file_path)

        # Ensure correct extension
        if not file_path.suffix or file_path.suffix.lower() != f".{extension}":
            file_path = file_path.with_suffix(f".{extension}")

        return self.get_data_path(output_type) / (
            f"{file_path.stem}_{timestamp}{file_path.suffix}"
            if timestamp
            else file_path
        )

    # Saving methods

    def load_yaml(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        safe_load: bool = True,
    ) -> Dict[str, Any]:
        """
        Load data from a YAML file.
        Modified to handle both regular files and configuration files.
        """
        # Special handling for configuration files
        if isinstance(file_path, Path) and file_path.is_absolute():
            yaml_path = file_path
        else:
            yaml_path = self.get_data_path(input_type) / Path(file_path)

        if not yaml_path.exists():
            raise FileNotFoundError(f"File does not exist: {yaml_path}")

        try:
            with open(yaml_path, "r", encoding=self.config["encoding"]) as f:
                data = (
                    yaml.safe_load(f)
                    if safe_load
                    else yaml.load(f, Loader=yaml.FullLoader)
                )
                if data is None:
                    return {}
                return data
        except (ParserError, ScannerError) as e:
            self.logger.error(f"Invalid YAML in file {yaml_path}: {str(e)}")
            raise ValueError(f"Invalid YAML in file {yaml_path}") from e
        except Exception as e:
            self.logger.error(f"Error loading YAML file {yaml_path}: {str(e)}")
            raise ValueError(f"Error loading YAML file {yaml_path}") from e

    def save_yaml(
        self,
        data: Dict[str, Any],
        file_path: Union[str, Path],
        output_type: str = "processed",
        include_timestamp: Optional[bool] = None,
        default_flow_style: bool = False,
        sort_keys: bool = False,
    ) -> Path:
        """
        Save data to a YAML file.

        Args:
            data (Dict[str, Any]): Data to save
            file_path (Union[str, Path]): Path to save the YAML file
            output_type (str): The type of output directory (e.g., "processed")
            include_timestamp (Optional[bool]): Whether to include timestamp in filename
            default_flow_style (bool): YAML flow style setting
            sort_keys (bool): Whether to sort dictionary keys

        Returns:
            Path: Path to the saved file

        Raises:
            ValueError: If the data cannot be serialized to YAML
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        file_path = Path(file_path)
        if not file_path.suffix or file_path.suffix.lower() != ".yaml":
            file_path = file_path.with_suffix(".yaml")

        output_path = self.get_data_path(output_type) / (
            f"{file_path.stem}_{timestamp}{file_path.suffix}"
            if timestamp
            else file_path
        )

        try:
            with open(output_path, "w", encoding=self.config["encoding"]) as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=default_flow_style,
                    sort_keys=sort_keys,
                    allow_unicode=True,
                    indent=2,
                )
            self.logger.info(f"Data saved to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving YAML to {output_path}: {str(e)}")
            raise ValueError(f"Error saving YAML to {output_path}") from e

    def load_json(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, Any]:
        """
        Load data from a JSON file.

        Args:
            file_path (Union[str, Path]): Path to the JSON file
            input_type (str): The type of input directory (e.g., "raw", "processed")

        Returns:
            Dict[str, Any]: Loaded JSON data

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON is invalid
        """
        file_path = self.get_data_path(input_type) / Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                data = json.load(f)
                return data
        except JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in file {file_path}: {str(e)}")
            raise ValueError(f"Invalid JSON in file {file_path}") from e
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {str(e)}")
            raise ValueError(f"Error loading JSON file {file_path}") from e

    def save_json(
        self,
        data: Union[Dict[str, Any], List[Any]],
        file_path: Union[str, Path],
        output_type: str = "processed",
        include_timestamp: Optional[bool] = None,
        indent: int = 2,
        ensure_ascii: bool = False,
    ) -> Path:
        """
        Save data to a JSON file.

        Args:
            data (Union[Dict[str, Any], List[Any]]): Data to save
            file_path (Union[str, Path]): Path to save the JSON file
            output_type (str): The type of output directory (e.g., "processed")
            include_timestamp (Optional[bool]): Whether to include timestamp in filename
            indent (int): Number of spaces for indentation
            ensure_ascii (bool): If False, write non-ASCII characters as-is

        Returns:
            Path: Path to the saved file

        Raises:
            ValueError: If the data cannot be serialized to JSON
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        file_path = Path(file_path)
        if not file_path.suffix or file_path.suffix.lower() != ".json":
            file_path = file_path.with_suffix(".json")

        output_path = self.get_data_path(output_type) / (
            f"{file_path.stem}_{timestamp}{file_path.suffix}"
            if timestamp
            else file_path
        )

        try:
            with open(output_path, "w", encoding=self.config["encoding"]) as f:
                json.dump(
                    data,
                    f,
                    indent=indent,
                    ensure_ascii=ensure_ascii,
                    default=str,  # Handles datetime objects
                )
            self.logger.info(f"Data saved to {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Error saving JSON to {output_path}: {str(e)}")
            raise ValueError(f"Error saving JSON to {output_path}") from e

    def save_data_to_disk(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List, Dict]], pd.DataFrame],
        output_filetype: Union[OutputFileType, str] = OutputFileType.CSV,
        output_type: str = "processed",  # Changed from output_dir
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """
        Save data to disk in various formats.

        Args:
            data: Data to save. Can be a dictionary of DataFrames/lists or a single DataFrame.
            output_filetype: The output file type (CSV, XLSX, PARQUET, JSON, or YAML).
            output_type: Type of output directory (e.g., "raw", "processed").
            file_name: Optional name for the output file.
            include_timestamp: Whether to include a timestamp in the file name.
            **kwargs: Additional arguments passed to the specific save method.

        Returns:
            Tuple[Dict[str, str], Optional[str]]: A tuple containing a dictionary of saved file
            paths and an optional metadata file path.
        """
        if isinstance(output_filetype, str):
            output_filetype = OutputFileType(output_filetype.lower())

        if output_filetype in [OutputFileType.YAML, OutputFileType.JSON]:
            if isinstance(data, pd.DataFrame):
                data = data.to_dict(orient="records")

            save_method = (
                self.save_yaml
                if output_filetype == OutputFileType.YAML
                else self.save_json
            )
            file_name = file_name or "data"
            saved_path = save_method(
                data=data,
                file_path=file_name,
                output_type=output_type,
                include_timestamp=include_timestamp,
                **kwargs,
            )
            return {file_name: str(saved_path)}, None

        # Convert data to dictionary format if it's a single DataFrame
        if isinstance(data, pd.DataFrame):
            data = {"data": data}

        # Ensure data is in the correct format
        if all(isinstance(v, list) for v in data.values()):
            return self._save_list_data(
                data, output_type, file_name, include_timestamp, output_filetype
            )
        elif all(isinstance(v, pd.DataFrame) for v in data.values()):
            return self._save_dataframe_data(
                data, output_type, file_name, include_timestamp, output_filetype
            )
        else:
            raise ValueError(
                "Unsupported data format. Must be a DataFrame or a dictionary of DataFrames/lists."
            )

    def _save_list_data(
        self,
        data: Dict[str, List],
        output_type: str,  # Changed from output_dir
        file_name: Optional[str],
        include_timestamp: Optional[bool],
        output_filetype: OutputFileType,
    ) -> Tuple[Dict[str, str], None]:
        """Helper method to save list data."""
        df = pd.DataFrame(data)
        output_path = self._get_output_path(
            file_path=file_name or "saved_data",
            output_type=output_type,
            extension=output_filetype.value,
            include_timestamp=include_timestamp,
        )

        if output_filetype == OutputFileType.CSV:
            df.to_csv(
                output_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
                quoting=self.config["quoting"],
            )
        elif output_filetype == OutputFileType.XLSX:
            df.to_excel(output_path, index=False, engine="openpyxl")
        elif output_filetype == OutputFileType.PARQUET:
            df.to_parquet(output_path, index=False)
        else:
            raise ValueError(f"Unsupported file type: {output_filetype}")

        self.logger.info(f"Data saved to {output_path}")
        return {output_path.stem: str(output_path)}, None

    def _save_dataframe_data(
        self,
        data: Dict[str, pd.DataFrame],
        output_type: str,
        file_name: Optional[str],
        include_timestamp: Optional[bool],
        output_filetype: OutputFileType,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Helper method to save DataFrame data."""
        if len(data) == 1:
            key, df = next(iter(data.items()))
            output_path = self._get_output_path(
                file_path=file_name or key,
                output_type=output_type,
                extension=output_filetype.value,
                include_timestamp=include_timestamp,
            )

            # Use ExcelWriter even for single DataFrame to preserve sheet name
            if output_filetype == OutputFileType.XLSX:
                with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                    for sheet_name, dataframe in data.items():
                        dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
            elif output_filetype == OutputFileType.CSV:
                df.to_csv(
                    output_path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                    quoting=self.config["quoting"],
                )
            elif output_filetype == OutputFileType.PARQUET:
                df.to_parquet(output_path, index=False)
            else:
                raise ValueError(f"Unsupported file type: {output_filetype}")

            self.logger.info(f"Data saved to {output_path}")
            return {output_path.stem: str(output_path)}, None
        else:
            if output_filetype == OutputFileType.XLSX:
                return self._save_multiple_dataframes_to_excel(
                    data, output_type, file_name, include_timestamp
                )
            elif output_filetype == OutputFileType.CSV:
                return self._save_multiple_dataframes_to_csv(
                    data, output_type, include_timestamp
                )
            elif output_filetype == OutputFileType.PARQUET:
                return self._save_multiple_dataframes_to_parquet(
                    data, output_type, file_name, include_timestamp
                )
            else:
                raise ValueError(f"Unsupported file type: {output_filetype}")

    def _save_multiple_dataframes_to_excel(
        self,
        data: Dict[str, pd.DataFrame],
        output_type: str,
        file_name: Optional[str],
        include_timestamp: Optional[bool],
    ) -> Tuple[Dict[str, str], None]:
        """Save multiple DataFrames to an Excel file with multiple sheets."""
        output_path = self._get_output_path(
            file_path=file_name or "multiple_sheets",
            output_type=output_type,
            extension="xlsx",
            include_timestamp=include_timestamp,
        )

        try:
            # Context manager handles closing automatically
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            self.logger.info(f"Data saved to {output_path}")
            return {output_path.stem: str(output_path)}, None
        except Exception as e:
            self.logger.error(f"Failed to save Excel file: {e}")
            # If the file exists but is corrupted, try to remove it
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception:
                    pass
            raise ValueError(f"Error saving Excel file: {output_path}") from e

    def _save_multiple_dataframes_to_csv(
        self,
        data: Dict[str, pd.DataFrame],
        output_type: str,  # Changed from output_dir
        include_timestamp: Optional[bool],
    ) -> Tuple[Dict[str, str], str]:
        """Save multiple DataFrames to separate CSV files and create metadata."""
        saved_files = {}
        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )

        for key, df in data.items():
            output_path = self._get_output_path(
                file_path=key,
                output_type=output_type,
                extension="csv",
                include_timestamp=include_timestamp,
            )
            df.to_csv(
                output_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
                quoting=self.config["quoting"],
            )
            saved_files[key] = str(output_path)
            self.logger.info(f"Data saved to {output_path}")

        metadata = {
            "timestamp": timestamp,
            "files": {
                key: {"path": path, "format": "csv"}
                for key, path in saved_files.items()
            },
            "config": self.config,
            "version": __version__,
        }

        metadata_path = self.save_json(
            data=metadata,
            file_path=f"metadata_{timestamp}" if timestamp else "metadata",
            output_type=output_type,
        )

        return saved_files, str(metadata_path)

    def _save_multiple_dataframes_to_parquet(
        self,
        data: Dict[str, pd.DataFrame],
        output_type: str,  # Changed from output_dir
        file_name: Optional[str],
        include_timestamp: Optional[bool],
    ) -> Tuple[Dict[str, str], None]:
        """Save multiple DataFrames to separate Parquet files."""
        saved_files = {}

        for key, df in data.items():
            output_path = self._get_output_path(
                file_path=key,
                output_type=output_type,
                extension="parquet",
                include_timestamp=include_timestamp,
            )
            df.to_parquet(output_path, index=False)
            saved_files[key] = str(output_path)
            self.logger.info(f"Data saved to {output_path}")

        return saved_files, None

    # Loading methods

    def load_single_file(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> pd.DataFrame:
        """
        Load a single file based on the file extension.

        Args:
            file_path (Union[str, Path]): Path to the file to be loaded.
            input_type (str): The type of input directory (e.g., "raw", "processed").

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is unsupported.

        Examples:
            >>> file_utils = FileUtils()
            >>> df = file_utils.load_single_file('data.csv', input_type='processed')
        """
        file_path = self.get_data_path(input_type) / Path(file_path)
        self.logger.info(f"Attempting to load file: {file_path}")

        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        extension = file_path.suffix.lower()
        if extension in [".csv", ".txt"]:
            return self._load_csv_with_inference(file_path)
        elif extension in [".xlsx", ".xls"]:
            return self._load_excel(file_path)
        elif extension == ".json":
            return self._load_json(file_path)
        elif extension == ".parquet":
            return self._load_parquet(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_csv_with_inference(self, file_path: Path) -> pd.DataFrame:
        """
        Load a CSV file with delimiter inference and flexible parsing.

        Args:
            file_path (Path): Path to the CSV file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            ValueError: If unable to determine the correct delimiter.
        """
        for delimiter in self.CSV_DELIMITERS:
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
                if len(df.columns) > 1:
                    self.logger.info(
                        f"Successfully loaded CSV with delimiter: '{delimiter}'"
                    )
                    return df
            except pd.errors.ParserError as e:
                self.logger.debug(f"Parser error with delimiter '{delimiter}': {e}")

        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                sample = f.read(1024)
                dialect = csv.Sniffer().sniff(sample)
            df = pd.read_csv(
                file_path,
                dialect=dialect,
                encoding=self.config["encoding"],
                quoting=self.config["quoting"],
            )
            self.logger.info("Successfully loaded CSV using csv.Sniffer")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load CSV file: {e}")
            raise ValueError(
                f"Unable to determine the correct delimiter for {file_path}"
            ) from e

    def load_csvs_from_metadata(
        self, metadata_file: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple CSV files based on a metadata JSON file.
        Now using the new JSON loading functionality.
        """
        try:
            metadata = self.load_json(metadata_file, input_type)
        except (FileNotFoundError, ValueError) as e:
            raise ValueError(f"Error loading metadata file: {metadata_file}") from e

        dataframes = {}
        for key, file_info in metadata.get("files", {}).items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                continue

            try:
                df = self.load_single_file(file_path)
                dataframes[key] = df
                self.logger.info(f"Successfully loaded CSV file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to load CSV file {file_path}: {e}")
                raise ValueError(f"Error loading CSV file: {file_path}") from e

        return dataframes

    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """
        Load an Excel file.

        Args:
            file_path (Path): Path to the Excel file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If there's an error loading the Excel file.
        """
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            self.logger.info(f"Successfully loaded Excel file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Excel file: {e}")
            raise ValueError(f"Error loading Excel file: {file_path}") from e

    def _load_json(self, file_path: Path) -> pd.DataFrame:
        """
        Load a JSON file.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            ValueError: If there's an error loading the JSON file.
        """
        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            self.logger.info(f"Successfully loaded JSON file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load JSON file: {e}")
            raise ValueError(f"Error loading JSON file: {file_path}") from e

    def _load_parquet(self, file_path: Path) -> pd.DataFrame:
        """
        Load a Parquet file.

        Args:
            file_path (Path): Path to the Parquet file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            ValueError: If there's an error loading the Parquet file.
        """
        try:
            df = pd.read_parquet(file_path)
            self.logger.info(f"Successfully loaded Parquet file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Parquet file: {e}")
            raise ValueError(f"Error loading Parquet file: {file_path}") from e

    def load_excel_sheets(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all sheets from an Excel file into a dictionary of DataFrames.

        Args:
            file_path (Union[str, Path]): Path to the Excel file.
            input_type (str): The type of input directory (e.g., "raw", "processed").

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with sheet names as keys and DataFrames as values.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not an Excel file.

        Examples:
            >>> file_utils = FileUtils()
            >>> sheets = file_utils.load_excel_sheets('data.xlsx', input_type='raw')
        """

        file_path = self.get_data_path(input_type) / Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        if not file_path.suffix.lower() in [".xlsx", ".xls"]:
            raise ValueError(f"File is not an Excel file: {file_path}")

        try:
            # ExcelFile context manager handles cleanup
            with pd.ExcelFile(file_path) as excel_file:
                dataframes = {
                    sheet_name: excel_file.parse(sheet_name)
                    for sheet_name in excel_file.sheet_names
                }

            self.logger.info(
                f"Successfully loaded {len(dataframes)} sheets from {file_path}"
            )
            return dataframes
        except Exception as e:
            self.logger.error(f"Failed to load Excel file {file_path}: {e}")
            raise ValueError(f"Error loading Excel file: {file_path}") from e

    def load_csvs_from_metadata(
        self, metadata_file: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple CSV files based on a metadata JSON file.

        Args:
            metadata_file (Union[str, Path]): Path to the metadata JSON file.
            input_type (str): The type of input directory (e.g., "raw", "processed").

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with keys as specified in the metadata and loaded DataFrames as values.

        Raises:
            FileNotFoundError: If the metadata file doesn't exist.
            ValueError: If the metadata file is invalid or any CSV file fails to load.

        Examples:
            >>> file_utils = FileUtils()
            >>> dataframes = file_utils.load_csvs_from_metadata('metadata.json', input_type='raw')
        """
        metadata_file = self.get_data_path(input_type) / Path(metadata_file)
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file does not exist: {metadata_file}")

        try:
            with metadata_file.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata file: {metadata_file}") from e

        dataframes = {}
        for key, file_info in metadata.get("files", {}).items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                continue
            try:
                df = pd.read_csv(
                    file_path,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                    quoting=self.config["quoting"],
                )
                dataframes[key] = df
                self.logger.info(f"Successfully loaded CSV file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to load CSV file {file_path}: {e}")
                raise ValueError(f"Error loading CSV file: {file_path}") from e

        return dataframes

    def load_data_from_metadata(
        self, metadata_file: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files based on a metadata file.
        Now using the new JSON loading functionality.
        """
        try:
            metadata = self.load_json(metadata_file, input_type)
        except (FileNotFoundError, ValueError) as e:
            raise ValueError(f"Error loading metadata file: {metadata_file}") from e

        loaded_data = {}
        for data_type, file_info in metadata.get("files", {}).items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            try:
                loaded_data[data_type] = self.load_single_file(file_path)
            except Exception as e:
                self.logger.error(f"Failed to load file for {data_type}: {e}")
                raise ValueError(
                    f"Error loading file for {data_type}: {file_path}"
                ) from e

        return loaded_data

    def load_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        input_type: str = "raw",
        file_type: Optional[OutputFileType] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files of the same type.

        Args:
            file_paths (List[Union[str, Path]]): List of paths to the files to be loaded.
            input_type (str): The type of input directory (e.g., "raw", "processed").
            file_type (Optional[OutputFileType]): Type of files to load. If None, infer from file extensions.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with file names as keys and loaded DataFrames as values.

        Raises:
            ValueError: If any file fails to load or if file types are inconsistent.

        Examples:
            >>> file_utils = FileUtils()
            >>> files = ['data1.csv', 'data2.csv']
            >>> dataframes = file_utils.load_multiple_files(files, input_type='processed')
        """
        loaded_data = {}
        for file_path in file_paths:
            path = self.get_data_path(input_type) / Path(file_path)
            if not path.exists():
                self.logger.error(f"File does not exist: {path}")
                raise FileNotFoundError(f"File does not exist: {path}")

            inferred_file_type = path.suffix.lower().lstrip(".")
            if file_type and inferred_file_type != file_type.value:
                raise ValueError(
                    f"File {path} does not match specified type: {file_type.value}"
                )

            try:
                df = self.load_single_file(path)
                loaded_data[path.stem] = df
                self.logger.info(f"Successfully loaded file: {path}")
            except Exception as e:
                self.logger.error(f"Failed to load file {path}: {e}")
                raise ValueError(f"Error loading file {path}") from e

        return loaded_data

    # Utility methods

    # def save_dataframes_to_excel(
    #     self,
    #     dataframes_dict: Dict[str, pd.DataFrame],
    #     file_name: str,
    #     output_type: str = "reports",
    #     parameters_dict: Optional[Dict] = None,
    #     include_timestamp: Optional[bool] = None,
    #     keep_index: bool = False,
    # ):
    def save_dataframes_to_excel(
        self,
        dataframes_dict: Dict[str, pd.DataFrame],
        file_name: str,
        output_type: str = "reports",
        parameters_dict: Optional[Dict] = None,
        include_timestamp: Optional[bool] = None,
        keep_index: bool = False,
    ):
        """
            Saves given dataframes and optional parameters to individual sheets in an Excel file.

            Args:
                dataframes_dict (Dict[str, pd.DataFrame]): Dictionary where keys are sheet names and values are dataframes to save.
                file_name (str): The base name for the Excel file to save, without extension.
                output_type (str): The type of output ("figures", "models", or "reports").
                parameters_dict (Optional[Dict]): Dictionary containing parameters to be saved on a separate sheet.
                include_timestamp (Optional[bool]): Whether to include a timestamp in the filename.
                keep_index (bool): Whether to include the index in the saved file.

            Raises:
                TypeError: If the input types are incorrect.

            Examples:
                >>> file_utils = FileUtils()
                >>> dfs = {'Sheet1': pd.DataFrame({'A': [1]}), 'Sheet2': pd.DataFrame({'B': [2]})}
                >>> parameters = {'param1': ('value1', 'comment1'), 'param2': ('value2', 'comment2')}
                >>> file_utils.save_dataframes_to_excel(dfs, 'output', parameters_dict=parameters)

        Saves given dataframes and optional parameters to individual sheets in an Excel file.
        Now using the new utility methods for path handling.
        """
        if not isinstance(dataframes_dict, dict):
            raise TypeError("dataframes_dict must be a dictionary")

        for sheet_name, df in dataframes_dict.items():
            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"Value for key '{sheet_name}' must be a pandas DataFrame"
                )

        if parameters_dict is not None and not isinstance(parameters_dict, dict):
            raise TypeError("parameters_dict must be a dictionary or None")

        file_path = self._get_output_path(
            file_path=file_name,
            output_type=output_type,
            extension="xlsx",
            include_timestamp=include_timestamp,
        )

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, dataframe in dataframes_dict.items():
                dataframe.to_excel(writer, sheet_name=sheet_name, index=keep_index)

            if parameters_dict:
                params_df = pd.DataFrame.from_dict(
                    parameters_dict,
                    orient="index",
                    columns=["Value", "Comment"],
                )
                params_df.reset_index(inplace=True)
                params_df.rename(columns={"index": "Parameter Name"}, inplace=True)
                params_df.to_excel(writer, sheet_name="Parameters", index=False)

        self.logger.info(f"Data saved to {file_path}")

    # Command-line interface methods

    @staticmethod
    def setup_directory_structure(project_root=None):
        """
        Set up the project directory structure.

        Args:
            project_root (Optional[Union[str, Path]]): The root directory of the project.

        Examples:
            >>> FileUtils.setup_directory_structure()
        """
        file_utils = FileUtils(project_root)
        file_utils.logger.info(
            f"Setting up directory structure in: {file_utils.project_root}"
        )
        file_utils._setup_directory_structure()
        file_utils.logger.info("Directory structure created successfully.")

    @classmethod
    def create_azure_utils(
        cls,
        connection_string: Optional[str] = None,
        project_root: Optional[Union[str, Path]] = None,
    ) -> "AzureFileUtils":
        """Factory method to create Azure-enabled FileUtils instance."""
        try:
            from .azure_file_utils import AzureFileUtils

            return AzureFileUtils(connection_string, project_root)
        except ImportError:
            logger.warning(
                "Azure dependencies not installed. Using standard FileUtils."
            )
            return cls(project_root)


def main():
    parser = argparse.ArgumentParser(
        description="File utilities for data science projects."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    setup_parser = subparsers.add_parser(
        "setup", help="Set up project directory structure"
    )
    setup_parser.add_argument(
        "-p", "--project-root", type=str, help="Project root directory"
    )

    # Test logging command
    test_logging_parser = subparsers.add_parser(
        "test-logging", help="Test logging functionality"
    )
    test_logging_parser.add_argument(
        "-p", "--project-root", type=str, help="Project root directory"
    )

    args = parser.parse_args()
    file_utils = FileUtils(args.project_root)
    logger = file_utils.get_logger(__name__)

    if args.command == "setup":
        FileUtils.setup_directory_structure(args.project_root)
    elif args.command == "test-logging":
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical("This is a critical message.")
        logger.info(
            "Logging test complete. Check the output to verify logging behavior."
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
