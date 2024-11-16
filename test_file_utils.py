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
from file_utils import FileUtils, OutputFileType

logger = logging.getLogger(__name__)


# Now let's fix the test class
class TestFileUtils(unittest.TestCase):
    def setUp(self):
        """Set up a temporary directory structure for testing."""
        # Store original logging config
        self.original_log_level = logging.getLogger().level
        self.original_handlers = logging.getLogger().handlers.copy()

        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test config file with updated structure
        config_data = {
            "csv_delimiter": ",",  # Match expected value
            "encoding": "utf-8",
            "quoting": 0,
            "include_timestamp": True,
            "logging_level": "INFO",  # Keep for backwards compatibility
            "disable_logging": False,
            "logging": {  # Add new logging section
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
            yaml.dump(config_data, f)

        # Initialize FileUtils with the config
        self.file_utils = FileUtils(
            project_root=self.temp_dir, config_file=self.config_path
        )

        # Sample data for tests
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

        # Store original logging config to restore after tests
        self.original_log_level = logging.getLogger().level
        self.original_handlers = logging.getLogger().handlers.copy()

    def test_initialization(self):
        """Test that FileUtils initializes correctly with config."""
        self.assertTrue(self.config_path.exists())
        self.assertEqual(self.file_utils.config["csv_delimiter"], ",")
        self.assertEqual(self.file_utils.config["encoding"], "utf-8")
        self.assertTrue(self.file_utils.config["include_timestamp"])

        # Test directory structure
        data_dir = self.temp_dir / "data"
        self.assertTrue(data_dir.exists())
        self.assertTrue((data_dir / "raw").exists())
        self.assertTrue((data_dir / "processed").exists())

    def test_logging_initialization_default(self):
        """Test default logging initialization."""
        import logging

        # Create new FileUtils instance with default logging
        file_utils = FileUtils(project_root=self.temp_dir)

        # Check default logging level (INFO)
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)

        # Check handler level
        self.assertTrue(root_logger.handlers)
        self.assertEqual(root_logger.handlers[0].level, logging.INFO)

    def test_logging_initialization_with_level(self):
        """Test logging initialization with specific level."""
        # Reset logging configuration
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create new FileUtils instance with DEBUG level
        file_utils = FileUtils(project_root=self.temp_dir, log_level="DEBUG")

        # Check if level was set correctly
        self.assertEqual(logging.getLevelName(root_logger.level), "DEBUG")

    def test_invalid_log_level(self):
        """Test handling of invalid log level."""
        # Reset logging configuration
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Create FileUtils with invalid level
        file_utils = FileUtils(
            project_root=self.temp_dir,
            config_file=None,  # Skip config to test just log level
            log_level="INVALID_LEVEL",
        )

        # Should fall back to INFO
        self.assertEqual(logging.getLevelName(root_logger.level), "INFO")

    def test_logging_config_override(self):
        """Test that log_level parameter overrides config file."""
        # Create config with INFO level
        config_data = {
            "csv_delimiter": ",",
            "encoding": "utf-8",
            "quoting": 0,
            "include_timestamp": True,
            "logging_level": "INFO",
            "disable_logging": False,
            "logging": {"level": "INFO"},
        }

        config_path = self.temp_dir / "config_override.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Create FileUtils with DEBUG override
        file_utils = FileUtils(
            project_root=self.temp_dir, config_file=config_path, log_level="DEBUG"
        )

        # Check if DEBUG level was applied
        self.assertEqual(logging.getLevelName(logging.getLogger().level), "DEBUG")

    def tearDown(self):
        """Clean up temporary directory and restore logging after tests."""
        # Restore original logging configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(self.original_log_level)

        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        for handler in self.original_handlers:
            root_logger.addHandler(handler)

        # Force garbage collection to help release file handles
        import gc

        gc.collect()

        # Add a small delay to ensure files are released
        import time

        time.sleep(0.1)

        # Try to remove the directory with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                shutil.rmtree(self.temp_dir)
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(
                        f"Warning: Could not clean up temporary directory {self.temp_dir}: {e}"
                    )
                else:
                    time.sleep(0.1)

    def test_save_and_load_yaml(self):
        """Test YAML file saving and loading."""
        # Save YAML file
        saved_path = self.file_utils.save_yaml(
            data=self.sample_dict,
            file_path="test_config",
            output_type="processed",
            include_timestamp=False,
        )

        # Load and verify YAML file
        loaded_data = self.file_utils.load_yaml(
            file_path=saved_path.name, input_type="processed"
        )

        self.assertEqual(loaded_data, self.sample_dict)
        self.assertTrue(saved_path.exists())

    def test_save_and_load_json(self):
        """Test JSON file saving and loading."""
        # Save JSON file
        saved_path = self.file_utils.save_json(
            data=self.sample_dict,
            file_path="test_data",
            output_type="processed",
            include_timestamp=False,
        )

        # Load and verify JSON file
        loaded_data = self.file_utils.load_json(
            file_path=saved_path.name, input_type="processed"
        )

        self.assertEqual(loaded_data, self.sample_dict)
        self.assertTrue(saved_path.exists())

    def test_save_and_load_csv(self):
        """Test CSV file saving and loading with standardized output_type."""
        # Test with direct DataFrame
        result, metadata = self.file_utils.save_data_to_disk(
            data=self.sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_data",
            include_timestamp=False,
        )

        saved_path = Path(next(iter(result.values())))

        # Load and verify CSV file
        loaded_df = self.file_utils.load_single_file(
            file_path=saved_path.name, input_type="processed"
        )

        pd.testing.assert_frame_equal(loaded_df, self.sample_df)
        self.assertTrue(saved_path.exists())

        # Test with dictionary of DataFrames
        multi_df_data = {"test_data": self.sample_df}
        result, metadata = self.file_utils.save_data_to_disk(
            data=multi_df_data,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_data_dict",
            include_timestamp=False,
        )

    def test_multiple_dataframes_excel(self):
        """Test saving multiple DataFrames to Excel."""
        df_dict = {
            "sheet1": self.sample_df.copy(),  # Use copies to avoid any potential references
            "sheet2": self.sample_df.copy(),
        }

        # Save Excel file
        try:
            result, _ = self.file_utils.save_data_to_disk(
                data=df_dict,
                output_filetype=OutputFileType.XLSX,
                output_type="processed",
                file_name="multi_sheet",
                include_timestamp=False,
            )

            saved_path = Path(next(iter(result.values())))

            # Load and verify Excel file
            loaded_dfs = self.file_utils.load_excel_sheets(
                file_path=saved_path.name, input_type="processed"
            )

            self.assertEqual(len(loaded_dfs), 2)
            pd.testing.assert_frame_equal(loaded_dfs["sheet1"], df_dict["sheet1"])
            pd.testing.assert_frame_equal(loaded_dfs["sheet2"], df_dict["sheet2"])
        finally:
            # Clean up references
            df_dict.clear()
            if "loaded_dfs" in locals():
                loaded_dfs.clear()
            gc.collect()

    def test_timestamp_inclusion(self):
        """Test timestamp inclusion in filenames."""
        result, _ = self.file_utils.save_data_to_disk(
            data=self.sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_data",
            include_timestamp=True,
        )

        saved_path = Path(next(iter(result.values())))
        timestamp_format = datetime.now().strftime("%Y%m%d")

        self.assertTrue(timestamp_format in str(saved_path))

    def test_error_handling(self):
        """Test basic error handling."""
        # Test loading non-existent file
        with self.assertRaises(FileNotFoundError):
            self.file_utils.load_single_file("nonexistent.csv")

        # Test invalid file type
        with self.assertRaises(ValueError):
            self.file_utils.save_data_to_disk(
                data=self.sample_df, output_filetype="invalid_type"
            )

        # Test invalid YAML
        invalid_yaml_path = self.temp_dir / "data" / "processed" / "invalid.yaml"
        invalid_yaml_path.parent.mkdir(parents=True, exist_ok=True)
        with open(invalid_yaml_path, "w") as f:
            f.write("invalid: yaml: content: {[")

        with self.assertRaises(ValueError):
            self.file_utils.load_yaml(invalid_yaml_path.name, "processed")

    def test_config_loading(self):
        """Test configuration loading and validation."""
        self.assertEqual(self.file_utils.config["csv_delimiter"], ",")
        self.assertEqual(self.file_utils.config["encoding"], "utf-8")
        self.assertTrue("data" in self.file_utils.config["directory_structure"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
