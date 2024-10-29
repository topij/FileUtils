import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import csv
import logging
import yaml
from typing import Dict, List, Tuple, Union, Optional
import argparse


class FileUtils:
    """
    A utility class for handling file operations in data science projects.

    This class provides methods for loading, saving, and backing up data files,
    as well as managing directory structures for data science projects.

    Attributes:
        project_root (Path): The root directory of the project.
        config (dict): Configuration settings for file operations.
    """

    _instance = None

    # Constants
    CSV_DELIMITERS = [",", ";", "\t", "|"]
    DEFAULT_ENCODING = "utf-8"
    DEFAULT_CSV_DELIMITER = ";"
    DEFAULT_LOGGING_LEVEL = "INFO"

    def __new__(
        cls,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
    ) -> "FileUtils":
        if cls._instance is None:
            cls._instance = super(FileUtils, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
    ) -> None:
        if self._initialized:
            return
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )
        self.config = self._load_config(config_file)
        self._setup_logging()
        self._initialized = True
        self.logger.debug(f"Project root: {self.project_root}")
        self._setup_directory_structure()

    @staticmethod
    def _get_project_root() -> Path:
        """Attempt to automatically determine the project root."""
        current_dir = Path.cwd()
        root_indicators = ["config.yaml", "main.py", ".env", "pyproject.toml", ".git"]
        while current_dir != current_dir.parent:
            if any((current_dir / indicator).exists() for indicator in root_indicators):
                return current_dir
            current_dir = current_dir.parent
        return Path.cwd()

    def _load_config(self, config_file: Optional[Union[str, Path]]) -> Dict:
        """
        Load configuration from a YAML file.

        Args:
            config_file (Optional[Union[str, Path]]): Path to the configuration file.

        Returns:
            Dict: Configuration settings.
        """
        if config_file is None:
            config_file = self.project_root / "config.yaml"
        else:
            config_file = Path(config_file)

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            logging.debug(f"Loaded configuration from {config_file}")
        except (yaml.YAMLError, FileNotFoundError) as e:
            logging.warning(
                f"Error loading configuration file {config_file}: {e}. Using default values."
            )
            config = {}

        # Set default values
        config.setdefault("csv_delimiter", self.DEFAULT_CSV_DELIMITER)
        config.setdefault("encoding", self.DEFAULT_ENCODING)
        config.setdefault("quoting", csv.QUOTE_MINIMAL)
        config.setdefault("include_timestamp", True)
        config.setdefault("logging_level", self.DEFAULT_LOGGING_LEVEL)
        config.setdefault("disable_logging", False)

        return config

    def _setup_logging(self) -> None:
        """Set up logging based on configuration settings."""
        if self.config.get("disable_logging", False):
            logging.disable(logging.CRITICAL)
            self.logger = logging.getLogger(__name__)
            print("Logging is disabled.")
            return

        logging_level = self.config.get(
            "logging_level", self.DEFAULT_LOGGING_LEVEL
        ).upper()
        numeric_level = getattr(logging, logging_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {logging_level}")

        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Logging level set to {logging_level}")

    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger with the specified name, configured according to the FileUtils settings.

        Args:
            name (str): Name of the logger, typically __name__ of the calling module.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(name)
        level_map = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
        }
        log_level_name = self.config.get("logging_level", "INFO").upper()
        log_level = level_map.get(log_level_name, logging.INFO)
        logger.setLevel(log_level)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _setup_directory_structure(self) -> None:
        """Set up the project directory structure based on configuration."""
        directory_structure = self.config.get(
            "directory_structure",
            {
                "data": ["raw", "interim", "processed", "configurations"],
                "reports": ["figures", "outputs"],
                "models": [],
                "src": [],
            },
        )
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
        return self.project_root / "data" / data_type

    # Saving methods

    def save_data_to_disk(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List]], pd.DataFrame],
        output_filetype: str = "csv",
        output_type: str = "test",
        file_name: Optional[str] = None,
        include_timestamp: bool = True,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """
        Save data to disk in various formats.

        Args:
            data: Data to save. Can be a dictionary of DataFrames/lists or a single DataFrame.
            output_filetype: The output file type, either "csv" or "xlsx".
            output_type: The type of output directory (e.g., "test", "processed").
            file_name: Optional name for the output file.
            include_timestamp: Whether to include a timestamp in the file name.

        Returns:
            A tuple containing a dictionary of saved file paths and an optional metadata file path.
        """
        output_dir = self.get_data_path(output_type)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )

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
        output_filetype: str,
    ) -> Tuple[Dict[str, str], None]:
        """Helper method to save list data."""
        df = pd.DataFrame(data)
        file_name = file_name or f"saved_data_{timestamp}"
        file_path = output_dir / f"{file_name}.{output_filetype}"

        if output_filetype == "csv":
            df.to_csv(
                file_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
            )
        else:  # xlsx
            df.to_excel(file_path, index=False, engine="openpyxl")

        return {file_name: str(file_path)}, None

    def _save_dataframe_data(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path,
        file_name: Optional[str],
        timestamp: str,
        output_filetype: str,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Helper method to save DataFrame data."""
        if len(data) == 1:
            key, df = next(iter(data.items()))
            file_name = file_name or key
            file_path = output_dir / f"{file_name}_{timestamp}.{output_filetype}"

            if output_filetype == "csv":
                df.to_csv(
                    file_path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                )
            else:  # xlsx
                df.to_excel(file_path, index=False, engine="openpyxl")

            return {file_name: str(file_path)}, None
        else:
            if output_filetype == "xlsx":
                return self._save_multiple_dataframes_to_excel(
                    data, output_dir, file_name, timestamp
                )
            else:  # csv
                return self._save_multiple_dataframes_to_csv(
                    data, output_dir, timestamp
                )

    def _save_multiple_dataframes_to_excel(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path,
        file_name: Optional[str],
        timestamp: str,
    ) -> Tuple[Dict[str, str], None]:
        file_name = f"{file_name}_{timestamp}.xlsx" or f"saved_data_{timestamp}.xlsx"
        file_path = output_dir / file_name
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, df in data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return {file_name: str(file_path)}, None

    def _save_multiple_dataframes_to_csv(
        self, data: Dict[str, pd.DataFrame], output_dir: Path, timestamp: str
    ) -> Tuple[Dict[str, str], str]:
        saved_files = {}
        for key, df in data.items():
            csv_file_name = f"{key}_{timestamp}.csv"
            file_path = output_dir / csv_file_name
            df.to_csv(
                file_path,
                index=False,
                encoding=self.config["encoding"],
                sep=self.config["csv_delimiter"],
            )
            saved_files[key] = str(file_path)

        metadata = {
            "timestamp": timestamp,
            "files": {
                key: {"path": path, "format": "csv"}
                for key, path in saved_files.items()
            },
            "format": "csv",
        }
        metadata_file = output_dir / f"metadata_{timestamp}.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
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
            ValueError: If the file format is unsupported or the file doesn't exist.
        """
        file_path = self.get_data_path(input_type) / Path(file_path)
        self.logger.info(f"Attempting to load file: {file_path}")

        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")

        if file_path.suffix.lower() in [".csv", ".txt"]:
            return self._load_csv_with_inference(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            return self._load_excel(file_path)
        elif file_path.suffix.lower() == ".json":
            return self._load_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def load_excel_sheets(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load all sheets from an Excel file into a dictionary of dataframes.

        Args:
            file_path (Union[str, Path]): Path to the Excel file.
            input_type (str): The type of input directory (e.g., "raw", "processed").

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with sheet names as keys and loaded DataFrames as values.

        Raises:
            ValueError: If the file doesn't exist or is not an Excel file.
        """
        file_path = self.get_data_path(input_type) / Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")
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
            self.logger.error(f"Failed to load Excel file {file_path}: {str(e)}")
            raise

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
            ValueError: If the metadata file doesn't exist or is invalid.
        """
        metadata_file = self.get_data_path(input_type) / Path(metadata_file)
        if not metadata_file.exists():
            raise ValueError(f"Metadata file does not exist: {metadata_file}")

        try:
            with metadata_file.open("r") as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in metadata file: {metadata_file}")

        dataframes = {}
        for key, file_info in metadata["files"].items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            if not file_path.exists():
                self.logger.warning(f"File does not exist: {file_path}")
                continue
            try:
                df = pd.read_csv(file_path, encoding=self.config["encoding"])
                dataframes[key] = df
                self.logger.info(f"Successfully loaded CSV file: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to load CSV file {file_path}: {str(e)}")

        return dataframes

    def load_data_from_metadata(
        self, metadata_file: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files based on a metadata file.

        Args:
            metadata_file (Union[str, Path]): Path to the metadata file.
            input_type (str): The type of input directory (e.g., "raw", "processed").

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with data types as keys and loaded DataFrames as values.

        Raises:
            ValueError: If the metadata file doesn't exist or is invalid.
        """
        metadata_file = self.get_data_path(input_type) / Path(metadata_file)
        if not metadata_file.exists():
            raise ValueError(f"Metadata file does not exist: {metadata_file}")

        try:
            with metadata_file.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in metadata file: {metadata_file}")

        loaded_data = {}
        for data_type, file_info in metadata.get("files", {}).items():
            file_path = self.get_data_path(input_type) / Path(file_info["path"])
            try:
                loaded_data[data_type] = self.load_single_file(file_path)
            except Exception as e:
                self.logger.error(f"Failed to load file for {data_type}: {str(e)}")

        return loaded_data

    def load_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        input_type: str = "raw",
        file_type: Optional[str] = None,
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple files of the same type.

        Args:
            file_paths (List[Union[str, Path]]): List of paths to the files to be loaded.
            input_type (str): The type of input directory (e.g., "raw", "processed").
            file_type (Optional[str]): Type of files to load. If None, infer from file extensions.

        Returns:
            Dict[str, pd.DataFrame]: Dictionary with file names as keys and loaded DataFrames as values.

        Raises:
            ValueError: If any file fails to load or if file types are inconsistent.
        """
        loaded_data = {}
        for file_path in file_paths:
            path = self.get_data_path(input_type) / Path(file_path)
            if file_type and path.suffix.lower() != f".{file_type.lower()}":
                raise ValueError(
                    f"File {path} does not match specified type: {file_type}"
                )

            try:
                loaded_data[path.stem] = self.load_single_file(path)
            except Exception as e:
                self.logger.error(f"Failed to load file {path}: {str(e)}")
                raise

        return loaded_data

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
                    file_path, delimiter=delimiter, encoding=self.config["encoding"]
                )
                if len(df.columns) > 1:
                    self.logger.info(
                        f"Successfully loaded CSV with delimiter: '{delimiter}'"
                    )
                    return df
            except Exception as e:
                self.logger.debug(
                    f"Failed to load with delimiter '{delimiter}': {str(e)}"
                )

        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                dialect = csv.Sniffer().sniff(f.read(1024))
            df = pd.read_csv(
                file_path, dialect=dialect, encoding=self.config["encoding"]
            )
            self.logger.info("Successfully loaded CSV using csv.Sniffer")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load CSV file: {str(e)}")
            raise ValueError(
                f"Unable to determine the correct delimiter for {file_path}"
            )

    def _load_excel(self, file_path: Path) -> pd.DataFrame:
        """
        Load an Excel file.

        Args:
            file_path (Path): Path to the Excel file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            Exception: If there's an error loading the Excel file.
        """
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            self.logger.info(f"Successfully loaded Excel file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Excel file: {str(e)}")
            raise

    def _load_json(self, file_path: Path) -> pd.DataFrame:
        """
        Load a JSON file.

        Args:
            file_path (Path): Path to the JSON file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.

        Raises:
            Exception: If there's an error loading the JSON file.
        """
        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                data = json.load(f)
            df = pd.DataFrame(data)
            self.logger.info(f"Successfully loaded JSON file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load JSON file: {str(e)}")
            raise

    # Utility methods

    def save_dataframe_to_excel(
        self,
        df: pd.DataFrame,
        file_name: str,
        output_type: str = "reports",
        sheet_name: str = "Sheet1",
        include_timestamp: bool = False,
        keep_index: bool = False,
    ):
        """
        Saves a single DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_name (str): Filename to save under, without extension.
            output_type (str): The type of output ("figures", "models", or "reports").
            sheet_name (str): Sheet name to save the DataFrame in.
            include_timestamp (bool): Whether to include a timestamp in the filename.
            keep_index (bool): Whether to include the index in the saved file.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        output_dir = self.get_data_path(output_type)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = (
            output_dir / f"{file_name}{'_' + timestamp if timestamp else ''}.xlsx"
        )

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=keep_index)

        self.logger.info(f"DataFrame saved to {file_path}")

    def save_dataframes_to_excel(
        self,
        dataframes_dict: Dict[str, pd.DataFrame],
        file_name: str,
        output_type: str = "reports",
        parameters_dict: Optional[Dict] = None,
        include_timestamp: bool = True,
        keep_index: bool = False,
    ):
        """
        Saves given dataframes and optional parameters to individual sheets in an Excel file.

        Args:
            dataframes_dict (Dict[str, pd.DataFrame]): Dictionary where keys are sheet names and values are dataframes to save.
            file_name (str): The base name for the Excel file to save, without extension.
            output_type (str): The type of output ("figures", "models", or "reports").
            parameters_dict (Optional[Dict]): Dictionary containing parameters to be saved on a separate sheet.
            include_timestamp (bool): Whether to include a timestamp in the filename.
            keep_index (bool): Whether to include the index in the saved file.
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

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        output_dir = self.get_data_path(output_type)
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = (
            output_dir / f"{file_name}{'_' + timestamp if timestamp else ''}.xlsx"
        )

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            for sheet_name, dataframe in dataframes_dict.items():
                dataframe.to_excel(writer, sheet_name=sheet_name, index=keep_index)

            if parameters_dict:
                params_data = [(k, v[0], v[1]) for k, v in parameters_dict.items()]
                params_df = pd.DataFrame(
                    params_data, columns=["Parameter Name", "Value", "Comment"]
                )
                params_df.to_excel(writer, sheet_name="Parameters", index=False)

        self.logger.info(f"Data saved to {file_path}")


# Utility functions


def setup_directory_structure(project_root=None):
    file_utils = FileUtils(project_root)
    file_utils.logger.info(
        f"Setting up directory structure in: {file_utils.project_root}"
    )
    file_utils._setup_directory_structure()
    file_utils.logger.info("Directory structure created successfully.")


def main():
    parser = argparse.ArgumentParser(
        description="File utilities for content traffic analysis project."
    )
    parser.add_argument(
        "-directory_setup",
        action="store_true",
        help="Set up the project directory structure",
    )
    parser.add_argument(
        "-project_root", type=str, help="Specify the project root directory"
    )
    parser.add_argument(
        "-test_logging", action="store_true", help="Test logging functionality"
    )
    args = parser.parse_args()

    file_utils = FileUtils(args.project_root)
    logger = file_utils.logger

    if args.directory_setup:
        setup_directory_structure(args.project_root)
    elif args.test_logging:
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.critical("This is a critical message.")
        logger.info(
            "Logging test complete. Check the output to verify logging behavior."
        )
    else:
        logger.warning("No action specified. Use -h for help.")


if __name__ == "__main__":
    main()
