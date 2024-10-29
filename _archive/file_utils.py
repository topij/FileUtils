import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import csv
import logging
import yaml
import argparse
from typing import Dict, List, Tuple, Union, Optional
import json

# import openpyxl


## TODO:
## Differentiate between saving a dictionary of dataframes and a dictionary of, for example,
## dictionary of basic data types (int, float, str, etc.)
# one common interface? save_data_to_disk with different parameters?


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

    def __new__(cls, project_root=None, config_file=None):
        if cls._instance is None:
            cls._instance = super(FileUtils, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, project_root=None, config_file=None):
        if self._initialized:
            return
        if project_root is None:
            self.project_root = self._get_project_root()
        else:
            self.project_root = Path(project_root)

        # Load configuration
        self.config = self.load_config(config_file)

        # Set up logging (only once)
        self.setup_logging()

        self._initialized = True

        # use self.logger
        self.logger.debug(f"Project root: {self.project_root}")

        # Set up directory structure
        self.directory_structure = self.config.get(
            "directory_structure",
            {
                "data": ["raw", "interim", "processed", "configurations"],
                "reports": ["figures", "outputs"],
                "models": [],
                "src": [],
            },
        )

        # Load output format settings
        self.output_format = self.config.get("output_format", "csv").lower()
        self.csv_delimiter = self.config.get("csv_delimiter", ",")
        self.encoding = self.config.get("encoding", "utf-8")

        self.ensure_directories()

        # Initialize directory attributes
        self.data_dir = self.project_root / "data"
        self.reports_dir = self.project_root / "reports"
        self.models_dir = self.project_root / "models"
        self.src_dir = self.project_root / "src"

    def load_config(self, config_file):
        if config_file is None:
            config_file = self.project_root / "config.yaml"
        else:
            config_file = Path(config_file)

        if config_file.exists():
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
            logging.debug(f"Loaded configuration from {config_file}")
        else:
            logging.warning(
                f"Configuration file {config_file} not found. Using default values."
            )
            config = {}

        # Set default values
        config.setdefault("csv_delimiter", ",")
        config.setdefault("encoding", "utf-8")
        config.setdefault("quoting", csv.QUOTE_MINIMAL)
        config.setdefault("include_timestamp", True)
        config.setdefault("logging_level", "INFO")
        config.setdefault("disable_logging", False)

        return config

    def setup_logging(self):
        if self.config.get("disable_logging", False):
            # Disable all logging
            logging.disable(logging.CRITICAL)
            self.logger = logging.getLogger(__name__)
            print("Logging is disabled.")
            return

        logging_level = self.config.get("logging_level", "INFO").upper()
        numeric_level = getattr(logging, logging_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {logging_level}")

        # Configure the root logger
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create a logger for this class
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging level set to {logging_level}")
        logging_level = self.config.get("logging_level", "INFO").upper()
        numeric_level = getattr(logging, logging_level, None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {logging_level}")

        # Configure the root logger
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create a logger for this class
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Logging level set to {logging_level}")

    def get_logger(self, name):
        logger = logging.getLogger(name)

        # Define a mapping of level names to level values
        level_map = {
            "CRITICAL": logging.CRITICAL,
            "ERROR": logging.ERROR,
            "WARNING": logging.WARNING,
            "INFO": logging.INFO,
            "DEBUG": logging.DEBUG,
        }

        # Get the log level from config, defaulting to INFO if not found
        log_level_name = self.config.get("logging_level", "INFO").upper()

        # Set the log level, defaulting to INFO if an invalid level is specified
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

    # def get_logger(name):
    #     """Get a logger with the specified name."""
    #     return logging.getLogger(name)

    # import logging

    @staticmethod
    def _get_project_root():
        """Attempt to automatically determine the project root."""
        current_dir = Path.cwd()
        root_indicators = ["config.yaml", "main.py", ".env", "pyproject.toml", ".git"]
        while current_dir != current_dir.parent:
            if any((current_dir / indicator).exists() for indicator in root_indicators):
                return current_dir
            current_dir = current_dir.parent
        return Path.cwd()

    def ensure_directories(self):
        """Ensures that all necessary directories exist."""
        for main_dir, sub_dirs in self.directory_structure.items():
            main_path = self.project_root / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            for sub_dir in sub_dirs:
                (main_path / sub_dir).mkdir(parents=True, exist_ok=True)

    def get_data_path(self, data_type="raw"):
        """Get the path for a specific data type directory."""
        return self.data_dir / data_type

    def get_report_path(self, report_type="outputs"):
        """Get the path for a specific report type directory."""
        return self.reports_dir / report_type

    def save_data_to_disk(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List]], pd.DataFrame],
        output_filetype: str = "csv",
        output_type: str = "test",
        file_name: Optional[str] = None,
        subtype: Optional[str] = None,
        include_timestamp: bool = True,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """
        Save data to disk in various formats.

        Args:
            data: Data to save. Can be a dictionary of DataFrames/lists or a single DataFrame.
            output_filetype: The output file type, either "csv" or "xlsx".
            output_type: The type of output directory (e.g., "test", "processed").
            file_name: Optional name for the output file.
            subtype: Optional subtype for the output directory.
            include_timestamp: Whether to include a timestamp in the file name.

        Returns:
            A tuple containing a dictionary of saved file paths and an optional metadata file path.
        """
        output_dir = self.get_data_path(output_type)
        if subtype:
            output_dir = output_dir / subtype
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = (
            datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
        )
        saved_files = {}

        # Handle single DataFrame
        if isinstance(data, pd.DataFrame):
            data = {"data": data}

        # Handle dictionary of lists (basic datatypes)
        if all(isinstance(v, list) for v in data.values()):
            df = pd.DataFrame(data)
            file_name = file_name or f"saved_data_{timestamp}"
            if output_filetype == "csv":
                file_path = output_dir / f"{file_name}.csv"
                df.to_csv(
                    file_path,
                    index=False,
                    encoding=self.encoding,
                    sep=self.csv_delimiter,
                )
            else:  # xlsx
                file_path = output_dir / f"{file_name}.xlsx"
                df.to_excel(file_path, index=False, engine="openpyxl")
            saved_files[file_name] = str(file_path)
            return saved_files, None

        # Handle dictionary of DataFrames
        if all(isinstance(v, pd.DataFrame) for v in data.values()):
            if len(data) == 1:
                key, df = next(iter(data.items()))
                file_name = file_name or key
                if output_filetype == "csv":
                    file_path = (
                        output_dir
                        / f"{file_name}{'_' + timestamp if timestamp else ''}.csv"
                    )
                    df.to_csv(
                        file_path,
                        index=False,
                        encoding=self.encoding,
                        sep=self.csv_delimiter,
                    )
                else:  # xlsx
                    file_path = (
                        output_dir
                        / f"{file_name}{'_' + timestamp if timestamp else ''}.xlsx"
                    )
                    df.to_excel(file_path, index=False, engine="openpyxl")
                saved_files[file_name] = str(file_path)
                return saved_files, None
            else:
                if output_filetype == "xlsx":
                    file_name = file_name or f"saved_data_{timestamp}.xlsx"
                    file_path = output_dir / file_name
                    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                        for sheet_name, df in data.items():
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                    saved_files[file_name] = str(file_path)
                    return saved_files, None
                else:  # csv
                    for key, df in data.items():
                        csv_file_name = (
                            f"{key}{'_' + timestamp if timestamp else ''}.csv"
                        )
                        file_path = output_dir / csv_file_name
                        df.to_csv(
                            file_path,
                            index=False,
                            encoding=self.encoding,
                            sep=self.csv_delimiter,
                        )
                        saved_files[key] = str(file_path)

                    metadata = {
                        "timestamp": timestamp,
                        "files": saved_files,
                        "format": output_filetype,
                    }
                    metadata_file = (
                        output_dir
                        / f"metadata{'_' + timestamp if timestamp else ''}.json"
                    )
                    with metadata_file.open("w", encoding="utf-8") as f:
                        json.dump(metadata, f, ensure_ascii=False, indent=2)
                    return saved_files, str(metadata_file)

        raise ValueError(
            "Unsupported data format. Must be a DataFrame or a dictionary of DataFrames/lists."
        )

    # def save_data_to_disk(
    #     self,
    #     data_dict,
    #     output_type="raw",
    #     subtype=None,
    #     create_metadata=True,
    #     include_timestamp=False,
    #     output_format="csv",
    # ):
    #     output_dir = self.get_data_path(output_type)
    #     if subtype:
    #         output_dir = output_dir / subtype
    #     output_dir.mkdir(parents=True, exist_ok=True)

    #     timestamp = (
    #         datetime.now().strftime("%Y%m%d_%H%M%S") if include_timestamp else ""
    #     )
    #     saved_files = {}

    #     # Use the specified output_format if provided, otherwise use the default
    #     format_to_use = output_format.lower() if output_format else self.output_format

    #     for data_name, df in data_dict.items():
    #         if format_to_use == "csv":
    #             filename = f"{data_name}{'_' + timestamp if timestamp else ''}.csv"
    #             file_path = output_dir / filename
    #             df.to_csv(
    #                 file_path,
    #                 index=False,
    #                 encoding=self.encoding,
    #                 sep=self.csv_delimiter,
    #             )
    #         elif format_to_use == "xlsx":
    #             filename = f"{data_name}{'_' + timestamp if timestamp else ''}.xlsx"
    #             file_path = output_dir / filename
    #             df.to_excel(file_path, index=False, engine="openpyxl")
    #         else:
    #             raise ValueError(f"Unsupported output format: {format_to_use}")

    #         saved_files[data_name] = str(file_path)
    #         self.logger.info(f"Saved {data_name} data to {file_path}")

    #     if create_metadata:
    #         metadata = {
    #             "timestamp": timestamp if timestamp else "no_timestamp",
    #             "files": saved_files,
    #             "format": format_to_use,
    #         }
    #         metadata_file = (
    #             output_dir / f"metadata{'_' + timestamp if timestamp else ''}.json"
    #         )
    #         with metadata_file.open("w", encoding="utf-8") as f:
    #             json.dump(metadata, f, ensure_ascii=False, indent=2)
    #         self.logger.info(f"Metadata saved to {metadata_file}")
    #         return saved_files, str(metadata_file)
    #     else:
    #         return saved_files, None

    def load_single_file(self, file_path):
        """
        Load a single file based on the file extension, with enhanced error handling and flexibility.

        Args:
            file_path (str or Path): Path to the file to be loaded.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.
        """
        file_path = Path(file_path)
        self.logger.info(f"Attempting to load file: {file_path}")

        if file_path.suffix.lower() in [".csv", ".txt"]:
            return self._load_csv_with_inference(file_path)
        elif file_path.suffix.lower() in [".xlsx", ".xls"]:
            return self._load_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _load_csv_with_inference(self, file_path):
        """
        Load a CSV file with delimiter inference and flexible parsing.

        Args:
            file_path (Path): Path to the CSV file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.
        """
        # Try common delimiters
        for delimiter in [",", ";", "\t", "|"]:
            try:
                df = pd.read_csv(file_path, delimiter=delimiter, encoding=self.encoding)
                if len(df.columns) > 1:
                    self.logger.info(
                        f"Successfully loaded CSV with delimiter: '{delimiter}'"
                    )
                    return df
            except Exception as e:
                self.logger.debug(
                    f"Failed to load with delimiter '{delimiter}': {str(e)}"
                )

        # If no delimiter worked, try csv.Sniffer
        try:
            with open(file_path, "r", encoding=self.encoding) as f:
                dialect = csv.Sniffer().sniff(f.read(1024))
            df = pd.read_csv(file_path, dialect=dialect, encoding=self.encoding)
            self.logger.info("Successfully loaded CSV using csv.Sniffer")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load CSV file: {str(e)}")
            raise ValueError(
                f"Unable to determine the correct delimiter for {file_path}"
            )

    def _load_excel(self, file_path):
        """
        Load an Excel file.

        Args:
            file_path (Path): Path to the Excel file.

        Returns:
            pd.DataFrame: Loaded data as a pandas DataFrame.
        """
        try:
            df = pd.read_excel(file_path, engine="openpyxl")
            self.logger.info(f"Successfully loaded Excel file: {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to load Excel file: {str(e)}")
            raise

    def load_data_from_metadata(self, metadata_file):
        """
        Load multiple files based on a metadata file.

        Args:
            metadata_file (str or Path): Path to the metadata file.

        Returns:
            dict: Dictionary with data types as keys and loaded DataFrames as values.
        """
        metadata_file = Path(metadata_file)
        with metadata_file.open("r", encoding="utf-8") as f:
            metadata = json.load(f)

        loaded_data = {}
        for data_type, file_path in metadata["files"].items():
            loaded_data[data_type] = self.load_single_file(file_path)

        return loaded_data

    def save_dataframe_to_excel(
        self,
        df,
        file_name,
        output_type="reports",
        sheet_name="Sheet1",
        include_timestamp=False,
        keep_index=False,
    ):
        """
        Saves a single DataFrame to an Excel file.

        Args:
            df (pd.DataFrame): DataFrame to save.
            file_name (str): Filename to save under, without extension.
            output_type (str): The type of output ("figures", "models", or "reports").
            sheet_name (str, optional): Sheet name to save the DataFrame in. Defaults to "Sheet1".
            keep_index (bool, optional): Whether to include the index in the saved file. Defaults to False.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.get_data_path(output_type)

        # if subtype:
        #     output_dir = output_dir / subtype
        output_dir.mkdir(parents=True, exist_ok=True)

        # file_path = output_dir / f"{file_name}_{timestamp}.xlsx"
        file_path = (
            output_dir
            / f"{file_name}{'_' + timestamp if include_timestamp else ''}.xlsx"
        )

        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=keep_index)

        self.logger.info(f"DataFrame saved to {file_path}")

    def save_dataframes_to_excel(
        self,
        dataframes_dict,
        file_name,
        output_type="reports",
        parameters_dict=None,
        include_timestamp=True,
        keep_index=False,
    ):
        """
        Saves given dataframes and optional parameters to individual sheets in an Excel file.

        Args:
            dataframes_dict (dict): Dictionary where keys are sheet names and values are dataframes to save.
            file_name (str): The base name for the Excel file to save, without extension.
            output_type (str): The type of output ("figures", "models", or "reports").
            parameters_dict (dict, optional): Dictionary containing parameters to be saved on a separate sheet.
            keep_index (bool, optional): Whether to include the index in the saved file. Defaults to False.
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        output_dir = self.get_data_path(output_type)

        # if subtype:
        #     output_dir = output_dir / subtype
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = (
            output_dir
            / f"{file_name}{'_' + timestamp if include_timestamp else ''}.xlsx"
        )
        # filename = f"{data_name}{'_' + timestamp if timestamp else ''}.xlsx"
        # file_path = self.get_output_path(output_type) / f"{file_name}_{timestamp}.xlsx"

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


def setup_directory_structure(project_root=None):
    file_utils = FileUtils(project_root)
    file_utils.logger.info(
        f"Setting up directory structure in: {file_utils.project_root}"
    )
    file_utils.ensure_directories()
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
