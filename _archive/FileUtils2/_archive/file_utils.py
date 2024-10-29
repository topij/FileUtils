# file_utils.py
# version 0.2.0



import argparse
import csv
import json
import logging
import logging.config
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import yaml
from jsonschema import validate, ValidationError

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
    "required": ["csv_delimiter", "encoding", "quoting", "include_timestamp", "logging_level", "disable_logging"],
}


class OutputFileType(Enum):
    CSV = "csv"
    XLSX = "xlsx"


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

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
    ) -> None:
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )
        self.config = self._load_config(config_file)
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Project root: {self.project_root}")
        self._setup_directory_structure()

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

    def _load_config(self, config_file: Optional[Union[str, Path]]) -> Dict:
        """
        Load configuration from a YAML file and merge it with default configurations.

        Args:
            config_file (Optional[Union[str, Path]]): Path to the configuration file.

        Returns:
            Dict: Configuration settings.

        Raises:
            ValueError: If the configuration file is invalid.
        """
        config = DEFAULT_CONFIG.copy()
        if config_file is None:
            config_file = self.project_root / "config.yaml"
        else:
            config_file = Path(config_file)

        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                validate(instance=user_config, schema=CONFIG_SCHEMA)
                config.update(user_config)
                logging.debug(f"Loaded configuration from {config_file}")
            except (yaml.YAMLError, ValidationError) as e:
                logging.warning(
                    f"Error loading configuration file {config_file}: {e}. Using default values."
                )
        else:
            logging.info(f"Configuration file {config_file} not found. Using default values.")

        return config

    def _setup_logging(self) -> None:
        """Set up logging based on configuration settings."""
        if self.config.get("disable_logging", False):
            logging.disable(logging.CRITICAL)
            return

        logging_level = self.config.get("logging_level", "INFO").upper()
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {"format": log_format, "datefmt": date_format},
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": logging_level,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": logging_level,
            },
        }

        logging.config.dictConfig(logging_config)

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
    
    # Saving methods

    def save_data_to_disk(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List]], pd.DataFrame],
        output_filetype: OutputFileType = OutputFileType.CSV,
        output_type: str = "test",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """
        Save data to disk in various formats.

        Args:
            data: Data to save. Can be a dictionary of DataFrames/lists or a single DataFrame.
            output_filetype (OutputFileType): The output file type, either CSV or XLSX.
            output_type (str): The type of output directory (e.g., "test", "processed").
            file_name (Optional[str]): Optional name for the output file.
            include_timestamp (Optional[bool]): Whether to include a timestamp in the file name.

        Returns:
            Tuple[Dict[str, str], Optional[str]]: A tuple containing a dictionary of saved file paths and an optional metadata file path.

        Raises:
            ValueError: If the data format is unsupported.
            TypeError: If the input types are incorrect.

        Examples:
            >>> file_utils = FileUtils()
            >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            >>> file_utils.save_data_to_disk(df, output_filetype=OutputFileType.CSV)
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        if not isinstance(data, (pd.DataFrame, dict)):
            raise TypeError("Data must be a pandas DataFrame or a dictionary of DataFrames/lists.")

        output_dir = self.get_data_path(output_type)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""

        if isinstance(data, pd.DataFrame):
            data = {"data": data}

        if all(isinstance(v, list) for v in data.values()):
            return self._save_list_data(
                data, output_dir, file_name, timestamp, output_filetype
            )
        elif all(isinstance(v, pd.DataFrame) for v in data.values()):
            return self._save_dataframe_data(
                data, output_dir, file_name, timestamp, output_filetype
            )
        else:
            raise ValueError(
                "Unsupported data format. Must be a DataFrame or a dictionary of DataFrames/lists."
            )

    def _save_list_data(
        self,
        data: Dict[str, List],
        output_dir: Path,
        file_name: Optional[str],
        timestamp: str,
        output_filetype: OutputFileType,
    ) -> Tuple[Dict[str, str], None]:
        """Helper method to save list data."""
        df = pd.DataFrame(data)
        file_name = file_name or f"saved_data_{timestamp}"
        file_path = output_dir / f"{file_name}.{output_filetype.value}"

        if output_filetype == OutputFileType.CSV:
            df.to_csv(
                file_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
                quoting=self.config["quoting"],
            )
        elif output_filetype == OutputFileType.XLSX:
            df.to_excel(file_path, index=False, engine="openpyxl")
        else:
            raise ValueError(f"Unsupported file type: {output_filetype}")

        self.logger.info(f"Data saved to {file_path}")
        return {file_name: str(file_path)}, None

    def _save_dataframe_data(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path,
        file_name: Optional[str],
        timestamp: str,
        output_filetype: OutputFileType,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Helper method to save DataFrame data."""
        if len(data) == 1:
            key, df = next(iter(data.items()))
            file_name = file_name or key
            file_name = f"{file_name}_{timestamp}" if timestamp else file_name
            file_path = output_dir / f"{file_name}.{output_filetype.value}"

            if output_filetype == OutputFileType.CSV:
                df.to_csv(
                    file_path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                    quoting=self.config["quoting"],
                )
            elif output_filetype == OutputFileType.XLSX:
                df.to_excel(file_path, index=False, engine="openpyxl")
            else:
                raise ValueError(f"Unsupported file type: {output_filetype}")

            self.logger.info(f"Data saved to {file_path}")
            return {file_name: str(file_path)}, None
        else:
            if output_filetype == OutputFileType.XLSX:
                return self._save_multiple_dataframes_to_excel(
                    data, output_dir, file_name, timestamp
                )
            elif output_filetype == OutputFileType.CSV:
                return self._save_multiple_dataframes_to_csv(
                    data, output_dir, timestamp
                )
            else:
                raise ValueError(f"Unsupported file type: {output_filetype}")

    def _save_multiple_dataframes_to_excel(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path,
        file_name: Optional[str],
        timestamp: str,
    ) -> Tuple[Dict[str, str], None]:
        """Save multiple DataFrames to an Excel file with multiple sheets."""
        file_name = f"{file_name}_{timestamp}.xlsx" if timestamp else f"{file_name}.xlsx"
        file_path = output_dir / file_name

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        self.logger.info(f"Data saved to {file_path}")
        return {file_name: str(file_path)}, None

    def _save_multiple_dataframes_to_csv(
        self, data: Dict[str, pd.DataFrame], output_dir: Path, timestamp: str
    ) -> Tuple[Dict[str, str], str]:
        """Save multiple DataFrames to separate CSV files and create metadata."""
        saved_files = {}
        for key, df in data.items():
            csv_file_name = f"{key}_{timestamp}.csv" if timestamp else f"{key}.csv"
            file_path = output_dir / csv_file_name
            df.to_csv(
                file_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
                quoting=self.config["quoting"],
            )
            saved_files[key] = str(file_path)
            self.logger.info(f"Data saved to {file_path}")

        metadata = {
            "timestamp": timestamp,
            "files": {
                key: {"path": path, "format": "csv"}
                for key, path in saved_files.items()
            },
            "config": self.config,
            "version": "1.0.0",
        }
        metadata_file = output_dir / f"metadata_{timestamp}.json" if timestamp else output_dir / "metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Metadata saved to {metadata_file}")
        return saved_files, str(metadata_file)

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
                    self.logger.info(f"Successfully loaded CSV with delimiter: '{delimiter}'")
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
        if file_path.suffix.lower() not in [".xlsx", ".xls"]:
            raise ValueError(f"File is not an Excel file: {file_path}")

        try:
            excel_file = pd.ExcelFile(file_path)
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

    # Utility methods

    def save_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        file_name: str,
        output_type: str = "reports",
        sheet_name: str = "Sheet1",
        include_timestamp: Optional[bool] = None,
        keep_index: bool = False,
    ):
        """
        Saves a single DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_name (str): Filename to save under, without extension.
            output_type (str): The type of output ("figures", "models", or "reports").
            sheet_name (str): Sheet name to save the DataFrame in.
            include_timestamp (Optional[bool]): Whether to include a timestamp in the filename.
            keep_index (bool): Whether to include the index in the saved file.

        Raises:
            TypeError: If the input types are incorrect.

        Examples:
            >>> file_utils = FileUtils()
            >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            >>> file_utils.save_dataframe_to_excel(df, 'output', output_type='reports')
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", False)

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        if not isinstance(file_name, str):
            raise TypeError("The 'file_name' parameter must be a string")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        output_dir = self.get_data_path(output_type)
        file_path = (
            output_dir / f"{file_name}_{timestamp}.xlsx" if timestamp else output_dir / f"{file_name}.xlsx"
        )

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=keep_index)

        self.logger.info(f"DataFrame saved to {file_path}")

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
            >>> file_utils.save_dataframes_to_excel(dfs, 'output')
        """
        if include_timestamp is None:
            include_timestamp = self.config.get("include_timestamp", True)

        if not isinstance(dataframes_dict, dict):
            raise TypeError("dataframes_dict must be a dictionary")

        for sheet_name, df in dataframes_dict.items():
            if not isinstance(df, pd.DataFrame):
                raise TypeError(
                    f"Value for key '{sheet_name}' must be a pandas DataFrame"
                )

        if parameters_dict is not None and not isinstance(parameters_dict, dict):
            raise TypeError("parameters_dict must be a dictionary or None")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        output_dir = self.get_data_path(output_type)
        file_path = (
            output_dir / f"{file_name}_{timestamp}.xlsx" if timestamp else output_dir / f"{file_name}.xlsx"
        )

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, dataframe in dataframes_dict.items():
                dataframe.to_excel(writer, sheet_name=sheet_name, index=keep_index)

            if parameters_dict:
                params_df = pd.DataFrame.from_dict(parameters_dict, orient='index', columns=['Value'])
                params_df.reset_index(inplace=True)
                params_df.rename(columns={'index': 'Parameter Name'}, inplace=True)
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
