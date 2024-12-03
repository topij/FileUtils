"""Unit tests for FileUtils package."""

import gc
import json
import logging
import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from FileUtils import FileUtils, OutputFileType, __version__

logger = logging.getLogger(__name__)


class TestFileUtils(unittest.TestCase):
    """Test cases for FileUtils."""

    def setUp(self):
        """Set up test environment."""
        # Store original logging config
        self.original_log_level = logging.getLogger().level
        self.original_handlers = logging.getLogger().handlers.copy()

        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test config
        self.config_data = {
            "csv_delimiter": ",",
            "encoding": "utf-8",
            "quoting": 0,
            "include_timestamp": True,
            "logging_level": "INFO",
            "disable_logging": False,
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "directory_structure": {
                "data": ["raw", "interim", "processed"],
                "reports": ["figures", "outputs"],
                "models": [],
                "src": [],
            },
        }

        # Create config file
        self.config_path = self.temp_dir / "config.yaml"
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config_data, f)

        # Initialize FileUtils
        self.file_utils = FileUtils(
            project_root=self.temp_dir, config_file=self.config_path
        )

        # Sample test data
        self.sample_df = pd.DataFrame(
            {
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "city": ["New York", "London", "Paris"],
            }
        )

        self.sample_dict = {
            "config": {"parameter1": "value1", "parameter2": "value2"},
            "data": {"items": [1, 2, 3], "status": "active"},
        }

    def tearDown(self):
        """Clean up after tests."""
        # Restore original logging configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(self.original_log_level)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        for handler in self.original_handlers:
            root_logger.addHandler(handler)

        # Force cleanup
        gc.collect()

        # Remove temporary directory with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                shutil.rmtree(self.temp_dir)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Warning: Could not clean up {self.temp_dir}: {e}")
                else:
                    import time

                    time.sleep(0.1)

    # Package Tests
    def test_version(self):
        """Test version is accessible."""
        self.assertIsNotNone(__version__)
        self.assertTrue(isinstance(__version__, str))

    # Initialization Tests
    def test_initialization(self):
        """Test initialization with config."""
        self.assertTrue(self.config_path.exists())
        self.assertEqual(self.file_utils.config["csv_delimiter"], ",")
        self.assertEqual(self.file_utils.config["encoding"], "utf-8")
        self.assertTrue(self.file_utils.config["include_timestamp"])

    def test_directory_structure(self):
        """Test directory structure creation."""
        data_dir = self.temp_dir / "data"
        self.assertTrue(data_dir.exists())
        self.assertTrue((data_dir / "raw").exists())
        self.assertTrue((data_dir / "processed").exists())
        self.assertTrue((data_dir / "interim").exists())

    def test_custom_directory_structure(self):
        """Test custom directory structure."""
        custom_config = self.config_data.copy()
        custom_config["directory_structure"]["custom"] = ["dir1", "dir2"]

        config_path = self.temp_dir / "custom_config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(custom_config, f)

        utils = FileUtils(project_root=self.temp_dir, config_file=config_path)
        self.assertTrue((self.temp_dir / "custom" / "dir1").exists())
        self.assertTrue((self.temp_dir / "custom" / "dir2").exists())

    # Logging Tests
    def test_logging_levels(self):
        """Test different logging levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            utils = FileUtils(project_root=self.temp_dir, log_level=level)
            self.assertEqual(utils.logger.level, getattr(logging, level))

    def test_invalid_log_level(self):
        """Test invalid logging level handling."""
        with self.assertRaises(ValueError):
            FileUtils(project_root=self.temp_dir, log_level="INVALID")

    # File Operation Tests
    def test_csv_operations(self):
        """Test CSV save and load operations."""
        # Single DataFrame
        result, _ = self.file_utils.save_data_to_disk(
            data=self.sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_csv",
            include_timestamp=False,
        )

        saved_path = Path(next(iter(result.values())))
        loaded_df = self.file_utils.load_single_file(
            saved_path.name, input_type="processed"
        )
        pd.testing.assert_frame_equal(loaded_df, self.sample_df)

    def test_excel_operations(self):
        """Test Excel save and load operations."""
        # Multiple DataFrames
        df_dict = {"sheet1": self.sample_df.copy(), "sheet2": self.sample_df.copy()}

        try:
            result, _ = self.file_utils.save_data_to_disk(
                data=df_dict,
                output_filetype=OutputFileType.XLSX,
                output_type="processed",
                file_name="test_excel",
                include_timestamp=False,
            )

            saved_path = Path(next(iter(result.values())))
            loaded_sheets = self.file_utils.load_excel_sheets(
                saved_path.name, input_type="processed"
            )

            self.assertEqual(len(loaded_sheets), 2)
            for sheet_name, df in df_dict.items():
                pd.testing.assert_frame_equal(loaded_sheets[sheet_name], df)
        finally:
            df_dict.clear()
            if "loaded_sheets" in locals():
                loaded_sheets.clear()
            gc.collect()

    def test_yaml_operations(self):
        """Test YAML save and load operations."""
        saved_path = self.file_utils.save_yaml(
            data=self.sample_dict,
            file_path="test_yaml",
            output_type="processed",
            include_timestamp=False,
        )

        loaded_data = self.file_utils.load_yaml(saved_path.name, input_type="processed")
        self.assertEqual(loaded_data, self.sample_dict)

    def test_json_operations(self):
        """Test JSON save and load operations."""
        saved_path = self.file_utils.save_json(
            data=self.sample_dict,
            file_path="test_json",
            output_type="processed",
            include_timestamp=False,
        )

        loaded_data = self.file_utils.load_json(saved_path.name, input_type="processed")
        self.assertEqual(loaded_data, self.sample_dict)

    # Error Handling Tests
    def test_file_not_found(self):
        """Test file not found handling."""
        with self.assertRaises(FileNotFoundError):
            self.file_utils.load_single_file("nonexistent.csv")

    def test_invalid_file_type(self):
        """Test invalid file type handling."""
        with self.assertRaises(ValueError):
            self.file_utils.save_data_to_disk(
                data=self.sample_df, output_filetype="invalid"
            )

    def test_invalid_yaml(self):
        """Test invalid YAML handling."""
        invalid_path = self.temp_dir / "data" / "processed" / "invalid.yaml"
        invalid_path.parent.mkdir(parents=True, exist_ok=True)
        with open(invalid_path, "w") as f:
            f.write("invalid: yaml: content: {[")

        with self.assertRaises(ValueError):
            self.file_utils.load_yaml(invalid_path.name, "processed")

    # Feature Tests
    def test_timestamp_inclusion(self):
        """Test timestamp in filenames."""
        result, _ = self.file_utils.save_data_to_disk(
            data=self.sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="timestamp_test",
            include_timestamp=True,
        )

        saved_path = Path(next(iter(result.values())))
        timestamp_format = datetime.now().strftime("%Y%m%d")
        self.assertTrue(timestamp_format in str(saved_path))

    def test_no_timestamp(self):
        """Test saving without timestamp."""
        result, _ = self.file_utils.save_data_to_disk(
            data=self.sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="no_timestamp",
            include_timestamp=False,
        )

        saved_path = Path(next(iter(result.values())))
        self.assertEqual(saved_path.stem, "no_timestamp")


if __name__ == "__main__":
    unittest.main(verbosity=2)
