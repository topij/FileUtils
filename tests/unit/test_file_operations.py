"""Tests for file_exists, list_directory, and enhanced create_directory methods."""

import os
from pathlib import Path

import pytest

from FileUtils.core.base import StorageError
from FileUtils.core.enums import OutputFileType


class TestFileExists:
    """Tests for file_exists() method."""

    def test_file_exists_basic(self, file_utils, sample_df):
        """Test basic file existence check."""
        # Save a file
        saved_files, _ = file_utils.save_data_to_storage(
            data=sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_file",
            include_timestamp=False,
        )

        # Check that file exists
        assert file_utils.file_exists("test_file.csv", input_type="processed") is True

        # Check non-existent file
        assert (
            file_utils.file_exists("nonexistent.csv", input_type="processed") is False
        )

    def test_file_exists_with_subpath(self, file_utils, sample_df):
        """Test file existence check with sub_path."""
        # Save a file with sub_path
        file_utils.save_data_to_storage(
            data=sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="subpath_file",
            sub_path="customer/ACME",
            include_timestamp=False,
        )

        # Check that file exists with sub_path
        assert (
            file_utils.file_exists(
                "subpath_file.csv", input_type="processed", sub_path="customer/ACME"
            )
            is True
        )

        # Check with wrong sub_path
        assert (
            file_utils.file_exists(
                "subpath_file.csv", input_type="processed", sub_path="customer/WRONG"
            )
            is False
        )

    def test_file_exists_root_level(self, file_utils, temp_dir):
        """Test file existence check with root_level=True."""
        # Create a file in root-level config directory
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "test_config.yml"
        config_file.write_text("test: value")

        # Check that file exists
        assert (
            file_utils.file_exists(
                "test_config.yml", input_type="config", root_level=True
            )
            is True
        )

    def test_file_exists_absolute_path(self, file_utils, temp_dir):
        """Test file existence check with absolute path."""
        # Create a file with absolute path
        abs_file = temp_dir / "absolute_test.txt"
        abs_file.write_text("test")

        # Check that file exists
        assert file_utils.file_exists(str(abs_file)) is True

        # Check non-existent absolute path
        assert file_utils.file_exists(str(temp_dir / "nonexistent.txt")) is False

    def test_file_exists_never_raises(self, file_utils):
        """Test that file_exists never raises exceptions."""
        # Should return False for invalid paths
        assert file_utils.file_exists("/invalid/path/to/file.txt") is False

        # Should return False for invalid input_type
        assert file_utils.file_exists("file.txt", input_type="invalid_type") is False

        # Should return False for permission errors (simulated)
        # On Windows, this might be a different path
        if os.name != "nt":
            assert file_utils.file_exists("/root/nonexistent.txt") is False

    def test_file_exists_with_pattern(self, file_utils, sample_df):
        """Test file existence with various file patterns."""
        # Save multiple files
        for i in range(3):
            file_utils.save_data_to_storage(
                data=sample_df,
                output_filetype=OutputFileType.CSV,
                output_type="processed",
                file_name=f"test_{i}",
                include_timestamp=False,
            )

        # Check each file exists
        for i in range(3):
            assert (
                file_utils.file_exists(f"test_{i}.csv", input_type="processed") is True
            )


class TestListDirectory:
    """Tests for list_directory() method."""

    def test_list_directory_basic(self, file_utils, temp_dir):
        """Test basic directory listing."""
        # Create test directory with files
        test_dir = temp_dir / "data" / "raw" / "test_list"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create some files
        (test_dir / "file1.csv").write_text("test1")
        (test_dir / "file2.csv").write_text("test2")
        (test_dir / "file3.txt").write_text("test3")

        # List directory
        items = file_utils.list_directory(directory_path="test_list", input_type="raw")

        assert len(items) == 3
        assert "file1.csv" in items
        assert "file2.csv" in items
        assert "file3.txt" in items

    def test_list_directory_with_pattern(self, file_utils, temp_dir):
        """Test directory listing with pattern filter."""
        # Create test directory with files
        test_dir = temp_dir / "data" / "raw" / "test_pattern"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Create files with different extensions
        (test_dir / "file1.csv").write_text("test1")
        (test_dir / "file2.csv").write_text("test2")
        (test_dir / "file3.txt").write_text("test3")
        (test_dir / "file4.yml").write_text("test4")

        # List only CSV files
        csv_files = file_utils.list_directory(
            directory_path="test_pattern", input_type="raw", pattern="*.csv"
        )

        assert len(csv_files) == 2
        assert "file1.csv" in csv_files
        assert "file2.csv" in csv_files
        assert "file3.txt" not in csv_files

    def test_list_directory_files_only(self, file_utils, temp_dir):
        """Test directory listing with files_only=True."""
        # Create test directory with files and subdirectories
        test_dir = temp_dir / "data" / "raw" / "test_files_only"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "subdir").mkdir()
        (test_dir / "file1.csv").write_text("test1")
        (test_dir / "file2.txt").write_text("test2")

        # List only files
        files = file_utils.list_directory(
            directory_path="test_files_only", input_type="raw", files_only=True
        )

        assert len(files) == 2
        assert "file1.csv" in files
        assert "file2.txt" in files
        assert "subdir" not in files

    def test_list_directory_directories_only(self, file_utils, temp_dir):
        """Test directory listing with directories_only=True."""
        # Create test directory with files and subdirectories
        test_dir = temp_dir / "data" / "raw" / "test_dirs_only"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "subdir1").mkdir()
        (test_dir / "subdir2").mkdir()
        (test_dir / "file1.csv").write_text("test1")

        # List only directories
        dirs = file_utils.list_directory(
            directory_path="test_dirs_only",
            input_type="raw",
            directories_only=True,
        )

        assert len(dirs) == 2
        assert "subdir1" in dirs
        assert "subdir2" in dirs
        assert "file1.csv" not in dirs

    def test_list_directory_with_subpath(self, file_utils, temp_dir):
        """Test directory listing with sub_path."""
        # Create nested directory structure
        nested_dir = temp_dir / "data" / "raw" / "customer" / "ACME"
        nested_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "file1.yml").write_text("test1")
        (nested_dir / "file2.yml").write_text("test2")

        # List directory with sub_path
        items = file_utils.list_directory(
            input_type="raw", sub_path="customer/ACME", pattern="*.yml"
        )

        assert len(items) == 2
        assert "file1.yml" in items
        assert "file2.yml" in items

    def test_list_directory_root_level(self, file_utils, temp_dir):
        """Test directory listing with root_level=True."""
        # Create root-level config directory
        config_dir = temp_dir / "config" / "ACME"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "config1.yml").write_text("test1")
        (config_dir / "config2.yml").write_text("test2")

        # List root-level directory
        items = file_utils.list_directory(
            input_type="config", sub_path="ACME", root_level=True, pattern="*.yml"
        )

        assert len(items) == 2
        assert "config1.yml" in items
        assert "config2.yml" in items

    def test_list_directory_absolute_path(self, file_utils, temp_dir):
        """Test directory listing with absolute path."""
        # Create test directory
        test_dir = temp_dir / "absolute_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("test1")
        (test_dir / "file2.txt").write_text("test2")

        # List using absolute path
        items = file_utils.list_directory(directory_path=str(test_dir))

        assert len(items) == 2
        assert "file1.txt" in items
        assert "file2.txt" in items

    def test_list_directory_nonexistent(self, file_utils):
        """Test listing non-existent directory returns empty list."""
        items = file_utils.list_directory(
            directory_path="nonexistent_dir", input_type="raw"
        )

        assert items == []

    def test_list_directory_never_raises(self, file_utils):
        """Test that list_directory never raises exceptions."""
        # Should return empty list for invalid paths
        items = file_utils.list_directory(directory_path="/invalid/path")
        assert items == []

        # Should return empty list for invalid input_type
        items = file_utils.list_directory(input_type="invalid_type")
        assert items == []

    def test_list_directory_input_type_only(self, file_utils, temp_dir):
        """Test listing directory using only input_type."""
        # Create files in raw directory (ensure directory exists)
        raw_dir = temp_dir / "data" / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / "file1.csv").write_text("test1")
        (raw_dir / "file2.csv").write_text("test2")

        # List using only input_type
        items = file_utils.list_directory(input_type="raw", pattern="*.csv")

        assert len(items) >= 2
        assert "file1.csv" in items
        assert "file2.csv" in items


class TestEnhancedCreateDirectory:
    """Tests for enhanced create_directory() method."""

    def test_create_directory_new_signature(self, file_utils):
        """Test create_directory with new signature."""
        # Create directory using new signature
        dir_path = file_utils.create_directory(
            "charts", input_type="processed", sub_path="presentations/ACME/run123"
        )

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert "charts" in dir_path
        assert "presentations/ACME/run123" in dir_path.replace("\\", "/")

    def test_create_directory_root_level(self, file_utils):
        """Test create_directory with root_level=True."""
        # Create root-level directory
        dir_path = file_utils.create_directory(
            "output", input_type="reports", root_level=True
        )

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert "reports" in dir_path
        # Should not be under data directory
        assert "/data/reports" not in dir_path.replace("\\", "/")

    def test_create_directory_legacy_compatibility(self, file_utils):
        """Test that legacy create_directory signature still works."""
        # Legacy usage: directory_name and parent_dir
        dir_path = file_utils.create_directory("features", parent_dir="data")

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert "features" in dir_path
        assert "data" in dir_path

    def test_create_directory_exist_ok(self, file_utils):
        """Test create_directory with exist_ok parameter."""
        # Create directory first time
        dir_path1 = file_utils.create_directory(
            "test_exist_ok", input_type="processed", exist_ok=True
        )

        # Create same directory again with exist_ok=True (should not raise)
        dir_path2 = file_utils.create_directory(
            "test_exist_ok", input_type="processed", exist_ok=True
        )

        assert dir_path1 == dir_path2
        assert Path(dir_path1).exists()

    def test_create_directory_exist_ok_false(self, file_utils):
        """Test create_directory with exist_ok=False raises error if exists."""
        # Create directory first time
        file_utils.create_directory(
            "test_exist_ok_false", input_type="processed", exist_ok=True
        )

        # Try to create again with exist_ok=False (should raise)
        with pytest.raises((FileExistsError, StorageError)):
            file_utils.create_directory(
                "test_exist_ok_false",
                input_type="processed",
                exist_ok=False,
            )

    def test_create_directory_absolute_path(self, file_utils, temp_dir):
        """Test create_directory with absolute path."""
        abs_path = temp_dir / "absolute_dir"
        dir_path = file_utils.create_directory(str(abs_path))

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert str(abs_path) == dir_path

    def test_create_directory_nested(self, file_utils):
        """Test creating nested directories."""
        # Create nested directory structure
        dir_path = file_utils.create_directory(
            "level3",
            input_type="processed",
            sub_path="level1/level2",
        )

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert "level1/level2/level3" in dir_path.replace("\\", "/")

    def test_create_directory_returns_string(self, file_utils):
        """Test that create_directory returns string (not Path)."""
        dir_path = file_utils.create_directory("test_return_type", input_type="raw")

        assert isinstance(dir_path, str)
        assert Path(dir_path).exists()

    def test_create_directory_with_subpath_and_root_level(self, file_utils):
        """Test create_directory with both sub_path and root_level."""
        dir_path = file_utils.create_directory(
            "nested",
            input_type="config",
            sub_path="environments/production",
            root_level=True,
        )

        assert Path(dir_path).exists()
        assert Path(dir_path).is_dir()
        assert "config/environments/production/nested" in dir_path.replace("\\", "/")
        # Should be at root level, not under data
        assert "/data/config" not in dir_path.replace("\\", "/")
