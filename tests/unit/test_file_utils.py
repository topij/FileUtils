# tests / unit / test_file_utils.py

import pytest
import pandas as pd
from pathlib import Path
import csv

from FileUtils import FileUtils
from FileUtils.core.enums import OutputFileType, StorageType
from FileUtils.core.base import StorageError


def test_initialization(temp_dir, sample_config):
    """Test FileUtils initialization."""
    utils = FileUtils(project_root=temp_dir, config_file=sample_config)

    assert utils.project_root == temp_dir
    assert utils.config["csv_delimiter"] == ","  # This should now pass
    assert utils.config["quoting"] == csv.QUOTE_MINIMAL
    assert not utils.config["include_timestamp"]


def test_save_single_dataframe(file_utils, sample_df):
    """Test saving single DataFrame."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="test_data",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = pd.read_csv(saved_path)
    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_multiple_dataframes(file_utils, sample_df):
    """Test saving multiple DataFrames."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="multi_sheet",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_sheets = pd.read_excel(saved_path, sheet_name=None)
    assert set(loaded_sheets.keys()) == set(data_dict.keys())
    for name, df in data_dict.items():
        pd.testing.assert_frame_equal(loaded_sheets[name], df)


def test_load_single_file(file_utils, sample_df):
    """Test loading single file."""
    # Save file first
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="test_load",
    )

    # Load and verify
    loaded_df = file_utils.load_single_file("test_load.csv", input_type="processed")

    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_load_excel_sheets(file_utils, sample_df):
    """Test loading Excel sheets."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}

    # Save file first
    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="test_excel",
    )

    # Load and verify
    loaded_sheets = file_utils.load_excel_sheets(
        "test_excel.xlsx", input_type="processed"
    )

    assert set(loaded_sheets.keys()) == set(data_dict.keys())
    for name, df in data_dict.items():
        pd.testing.assert_frame_equal(loaded_sheets[name], df)


def test_deprecated_method_warning(file_utils, sample_df):
    """Test deprecated method warning."""
    with pytest.warns(DeprecationWarning):
        file_utils.save_data_to_disk(
            data=sample_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_deprecated",
        )


def test_invalid_file_type(file_utils, sample_df):
    """Test invalid file type handling."""
    with pytest.raises(ValueError):
        file_utils.save_data_to_storage(
            data=sample_df,
            output_filetype="invalid",
            output_type="processed",
            file_name="test_invalid",
        )


def test_file_not_found(file_utils):
    """Test file not found handling."""
    with pytest.raises(StorageError):
        file_utils.load_single_file("nonexistent.csv", input_type="processed")
