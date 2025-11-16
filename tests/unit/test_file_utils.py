# tests / unit / test_file_utils.py

import csv
import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from FileUtils import FileUtils
from FileUtils.core.base import StorageError
from FileUtils.core.enums import OutputFileType, StorageType


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

    # Excel files return a mapping of sheet names to the same file path
    assert len(saved_files) == 2  # One entry per sheet
    saved_path = Path(next(iter(saved_files.values())))  # All sheets point to same file
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


def test_load_yaml(file_utils, temp_dir):
    """Test loading YAML file."""
    # Create test YAML file
    yaml_data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
    yaml_path = temp_dir / "data" / "raw" / "test.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    # Test loading
    loaded_data = file_utils.load_yaml("test.yaml")
    assert loaded_data == yaml_data

    # Test loading non-existent file
    with pytest.raises(StorageError):
        file_utils.load_yaml("nonexistent.yaml")

    # Test loading invalid YAML
    invalid_yaml = temp_dir / "data" / "raw" / "invalid.yaml"
    with open(invalid_yaml, "w") as f:
        f.write("invalid: yaml: content]")

    with pytest.raises(StorageError):
        file_utils.load_yaml("invalid.yaml")


def test_load_json(file_utils, temp_dir):
    """Test loading JSON file."""
    # Create test JSON file
    json_data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
    json_path = temp_dir / "data" / "raw" / "test.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(json_data, f)

    # Test loading
    loaded_data = file_utils.load_json("test.json")
    assert loaded_data == json_data

    # Test loading non-existent file
    with pytest.raises(StorageError):
        file_utils.load_json("nonexistent.json")

    # Test loading invalid JSON
    invalid_json = temp_dir / "data" / "raw" / "invalid.json"
    with open(invalid_json, "w") as f:
        f.write("invalid json content")

    with pytest.raises(StorageError):
        file_utils.load_json("invalid.json")


def test_load_yaml_dataframe(file_utils, temp_dir):
    """Test loading YAML file as DataFrame."""
    # Create test YAML file with list of records
    yaml_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    yaml_path = temp_dir / "data" / "raw" / "test_df.yaml"
    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    # Test loading as DataFrame
    df = file_utils.load_single_file("test_df.yaml")
    assert len(df) == 2
    assert sorted(df.columns) == ["age", "name"]  # Check sorted column names
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [25, 30]


def test_load_json_dataframe(file_utils, temp_dir):
    """Test loading JSON file as DataFrame."""
    # Create test JSON file with list of records
    json_data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    json_path = temp_dir / "data" / "raw" / "test_df.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(json_data, f)

    # Test loading as DataFrame
    df = file_utils.load_single_file("test_df.json")
    assert len(df) == 2
    assert sorted(df.columns) == ["age", "name"]  # Check sorted column names
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [25, 30]


def test_create_directory(file_utils):
    """Test directory creation."""
    # Create directory under data
    new_dir = file_utils.create_directory("features")
    new_dir_path = Path(new_dir)  # Now returns string, convert to Path for assertions
    assert new_dir_path.exists()
    assert new_dir_path.is_dir()
    assert new_dir_path == file_utils.project_root / "data" / "features"
    assert "features" in file_utils.config["directory_structure"]["data"]

    # Create directory under reports
    reports_dir = file_utils.create_directory("monthly", parent_dir="reports")
    reports_dir_path = Path(reports_dir)  # Now returns string, convert to Path for assertions
    assert reports_dir_path.exists()
    assert reports_dir_path.is_dir()
    assert reports_dir_path == file_utils.project_root / "reports" / "monthly"
    assert "monthly" in file_utils.config["directory_structure"]["reports"]


def test_create_directory_invalid_parent(file_utils):
    """Test directory creation with invalid parent directory."""
    with pytest.raises(ValueError) as exc_info:
        file_utils.create_directory("test", parent_dir="invalid_parent")
    assert "Invalid parent directory" in str(exc_info.value)


def test_create_directory_exists(file_utils):
    """Test creating directory that already exists."""
    # Create directory twice should not raise error
    dir1 = file_utils.create_directory("test_dir")
    dir2 = file_utils.create_directory("test_dir")
    assert dir1 == dir2
    assert Path(dir1).exists()


def test_save_yaml_dataframe_records(file_utils, sample_df):
    """Test saving DataFrame to YAML in records format."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="test_yaml_records",
        yaml_options={"default_flow_style": False, "sort_keys": True},
        orient="records",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file(
        "test_yaml_records.yaml", input_type="processed"
    )
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
    )

    # Verify YAML format
    with open(saved_path, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
        assert isinstance(yaml_content, list)  # Should be list of records
        assert len(yaml_content) == len(sample_df)


def test_save_yaml_dataframe_index(file_utils, sample_df):
    """Test saving DataFrame to YAML in index format."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="test_yaml_index",
        yaml_options={"default_flow_style": False},
        orient="index",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file(
        "test_yaml_index.yaml", input_type="processed"
    )
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
        check_index_type=False,  # Index type may change for YAML
    )

    # Verify YAML format
    with open(saved_path, "r", encoding="utf-8") as f:
        yaml_content = yaml.safe_load(f)
        assert isinstance(yaml_content, dict)  # Should be dictionary
        assert len(yaml_content) == len(sample_df)


def test_save_json_dataframe_records(file_utils, sample_df):
    """Test saving DataFrame to JSON in records format."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="test_json_records",
        orient="records",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file(
        "test_json_records.json", input_type="processed"
    )
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
    )

    # Verify JSON format
    with open(saved_path, "r", encoding="utf-8") as f:
        json_content = json.load(f)
        assert isinstance(json_content, list)  # Should be list of records
        assert len(json_content) == len(sample_df)


def test_save_json_dataframe_index(file_utils, sample_df):
    """Test saving DataFrame to JSON in index format."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="test_json_index",
        orient="index",
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file(
        "test_json_index.json", input_type="processed"
    )

    # Convert index to integers if possible
    if loaded_df.index.dtype == "O" and all(idx.isdigit() for idx in loaded_df.index):
        loaded_df.index = loaded_df.index.astype(int)

    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
        check_index_type=False,  # Index type may change for JSON
    )

    # Verify JSON format
    with open(saved_path, "r", encoding="utf-8") as f:
        json_content = json.load(f)
        assert isinstance(json_content, dict)  # Should be dictionary
        assert len(json_content) == len(sample_df)


def test_save_yaml_invalid_orient(file_utils, sample_df):
    """Test saving DataFrame to YAML with invalid orientation."""
    with pytest.raises(StorageError) as exc_info:
        file_utils.save_data_to_storage(
            data=sample_df,
            output_filetype=OutputFileType.YAML,
            output_type="processed",
            file_name="test_yaml_invalid",
            orient="invalid_orient",
        )
    assert "Unsupported YAML orientation" in str(exc_info.value)


def test_save_json_invalid_orient(file_utils, sample_df):
    """Test saving DataFrame to JSON with invalid orientation."""
    with pytest.raises(StorageError) as exc_info:
        file_utils.save_data_to_storage(
            data=sample_df,
            output_filetype=OutputFileType.JSON,
            output_type="processed",
            file_name="test_json_invalid",
            orient="invalid_orient",
        )
    assert "Invalid value 'invalid_orient' for option 'orient'" in str(exc_info.value)


def test_yaml_custom_options(file_utils, sample_df):
    """Test saving DataFrame to YAML with custom options."""
    yaml_options = {
        "default_flow_style": True,
        "sort_keys": True,
        "width": 80,
        "indent": 4,
    }

    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="test_yaml_custom",
        yaml_options=yaml_options,
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file(
        "test_yaml_custom.yaml", input_type="processed"
    )
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
    )


def test_save_multiple_dataframes_yaml(file_utils, sample_df):
    """Test saving multiple DataFrames to YAML files."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="multi_yaml",
        yaml_options={"default_flow_style": False},
    )

    assert len(saved_files) == len(data_dict)
    for sheet_name, file_path in saved_files.items():
        assert Path(file_path).exists()
        loaded_df = file_utils.load_single_file(
            Path(file_path).name, input_type="processed"
        )
        pd.testing.assert_frame_equal(
            loaded_df.reindex(sorted(loaded_df.columns), axis=1),
            data_dict[sheet_name].reindex(
                sorted(data_dict[sheet_name].columns), axis=1
            ),
        )


def test_save_multiple_dataframes_json(file_utils, sample_df):
    """Test saving multiple DataFrames to JSON files."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="multi_json",
        orient="records",
    )

    assert len(saved_files) == len(data_dict)
    for sheet_name, file_path in saved_files.items():
        assert Path(file_path).exists()
        loaded_df = file_utils.load_single_file(
            Path(file_path).name, input_type="processed"
        )
        pd.testing.assert_frame_equal(
            loaded_df.reindex(sorted(loaded_df.columns), axis=1),
            data_dict[sheet_name].reindex(
                sorted(data_dict[sheet_name].columns), axis=1
            ),
        )


# Tests for sub_path functionality
def test_save_single_dataframe_with_subpath(file_utils, sample_df):
    """Test saving single DataFrame with sub_path."""
    sub_path = "level1/level2"
    file_name = "subpath_test"
    output_type = "processed"

    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=file_name,
        sub_path=sub_path,
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify path structure
    expected_dir = file_utils.project_root / "data" / output_type / sub_path
    assert saved_path.parent == expected_dir
    assert saved_path.name == f"{file_name}.csv"

    # Verify content
    loaded_df = pd.read_csv(saved_path)
    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_save_excel_with_subpath(file_utils, sample_df):
    """Test saving multi-sheet Excel file with sub_path."""
    sub_path = "excel_reports"
    file_name = "excel_subpath"
    output_type = "processed"
    data_dict = {"sheetA": sample_df, "sheetB": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.XLSX,
        output_type=output_type,
        file_name=file_name,
        sub_path=sub_path,
    )

    # Excel files return a mapping of sheet names to the same file path
    assert len(saved_files) == 2  # One entry per sheet
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify path structure
    expected_dir = file_utils.project_root / "data" / output_type / sub_path
    assert saved_path.parent == expected_dir
    assert saved_path.name == f"{file_name}.xlsx"

    # Verify content
    loaded_sheets = pd.read_excel(saved_path, sheet_name=None)
    assert set(loaded_sheets.keys()) == set(data_dict.keys())
    for name, df in data_dict.items():
        pd.testing.assert_frame_equal(loaded_sheets[name], df)


def test_save_multiple_csv_with_subpath(file_utils, sample_df):
    """Test saving multiple DataFrames as separate CSVs with sub_path."""
    sub_path = "csv_reports/run1"
    file_name = "multi_csv"
    output_type = "processed"
    data_dict = {"data1": sample_df, "data2": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.CSV,  # Non-Excel saves separate files
        output_type=output_type,
        file_name=file_name,
        sub_path=sub_path,
    )

    assert len(saved_files) == 2
    expected_dir = file_utils.project_root / "data" / output_type / sub_path

    for sheet_name, saved_path_str in saved_files.items():
        saved_path = Path(saved_path_str)
        assert saved_path.exists()
        assert saved_path.parent == expected_dir
        # Check filename format: base_sheetname.ext
        assert saved_path.name == f"{file_name}_{sheet_name}.csv"

        # Verify content
        loaded_df = pd.read_csv(saved_path)
        pd.testing.assert_frame_equal(loaded_df, data_dict[sheet_name])


def test_save_with_absolute_subpath(file_utils, sample_df):
    """Test that an absolute sub_path is handled correctly (made relative)."""
    import os

    # Create an absolute path unlikely to exist, but valid structure
    # Use platform-appropriate absolute path
    if os.name == "nt":  # Windows
        abs_sub_path = Path("C:/abs/path/to/reports")
    else:  # Unix-like
        abs_sub_path = Path("/abs/path/to/reports")
    relative_equivalent = "abs/path/to/reports"  # How it should be treated
    file_name = "abs_subpath_test"
    output_type = "processed"

    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=file_name,
        sub_path=abs_sub_path,  # Pass the absolute path
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify path structure uses the relative equivalent
    expected_dir = file_utils.project_root / "data" / output_type / relative_equivalent
    assert saved_path.parent == expected_dir
    assert saved_path.name == f"{file_name}.csv"


# --- Tests for loading with sub_path ---


def test_load_single_file_with_subpath(file_utils, sample_df):
    """Test loading single file with sub_path."""
    sub_path = "load_level1/load_level2"
    file_name = "load_subpath_test.csv"
    output_type = "processed"

    # First, save a file using sub_path
    file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=Path(file_name).stem,
        sub_path=sub_path,
        include_timestamp=False,  # Disable timestamp for predictable filename
    )

    # Now, load using sub_path
    loaded_df = file_utils.load_single_file(
        file_path=file_name,  # Just the filename
        input_type=output_type,
        sub_path=sub_path,  # Specify the sub_path
    )

    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_load_excel_sheets_with_subpath(file_utils, sample_df):
    """Test loading Excel sheets with sub_path."""
    sub_path = "load_excel_reports"
    file_name = "load_excel_subpath.xlsx"
    output_type = "processed"
    data_dict = {"sheetA": sample_df, "sheetB": sample_df.copy()}

    # Save the Excel file first
    file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.XLSX,
        output_type=output_type,
        file_name=Path(file_name).stem,
        sub_path=sub_path,
        include_timestamp=False,
    )

    # Load using sub_path
    loaded_sheets = file_utils.load_excel_sheets(
        file_path=file_name,  # Just the filename
        input_type=output_type,
        sub_path=sub_path,
    )

    assert set(loaded_sheets.keys()) == set(data_dict.keys())
    for name, df in data_dict.items():
        pd.testing.assert_frame_equal(loaded_sheets[name], df)


def test_load_yaml_with_subpath(file_utils, temp_dir):
    """Test loading YAML file with sub_path."""
    sub_path = "config_files/yaml"
    file_name = "test_load.yaml"
    input_type = "raw"
    yaml_data = {"key": "value", "items": [1, 2]}

    # Create test YAML file in the sub_path
    full_dir = temp_dir / "data" / input_type / sub_path
    full_dir.mkdir(parents=True, exist_ok=True)
    with open(full_dir / file_name, "w") as f:
        yaml.safe_dump(yaml_data, f)

    # Load using sub_path
    loaded_data = file_utils.load_yaml(
        file_path=file_name, input_type=input_type, sub_path=sub_path
    )
    assert loaded_data == yaml_data


def test_load_json_with_subpath(file_utils, temp_dir):
    """Test loading JSON file with sub_path."""
    sub_path = "config_files/json"
    file_name = "test_load.json"
    input_type = "raw"
    json_data = {"key": "value", "items": [1, 2]}

    # Create test JSON file in the sub_path
    full_dir = temp_dir / "data" / input_type / sub_path
    full_dir.mkdir(parents=True, exist_ok=True)
    with open(full_dir / file_name, "w") as f:
        json.dump(json_data, f)

    # Load using sub_path
    loaded_data = file_utils.load_json(
        file_path=file_name, input_type=input_type, sub_path=sub_path
    )
    assert loaded_data == json_data


def test_load_multiple_files_with_subpath(file_utils, sample_df):
    """Test loading multiple files with sub_path."""
    sub_path = "multi_load/runX"
    output_type = "processed"
    filenames = ["data_a.csv", "data_b.csv"]
    data_dict = {Path(fn).stem: sample_df.assign(id=Path(fn).stem) for fn in filenames}

    # Save the files first
    for fn, df_to_save in data_dict.items():
        file_utils.save_data_to_storage(
            data=df_to_save,
            output_filetype=OutputFileType.CSV,
            output_type=output_type,
            file_name=fn,
            sub_path=sub_path,
            include_timestamp=False,
        )

    # Load using load_multiple_files with sub_path
    loaded_data = file_utils.load_multiple_files(
        file_paths=filenames,  # List of filenames only
        input_type=output_type,
        sub_path=sub_path,
        file_type=OutputFileType.CSV,  # Optional: enforce type
    )

    assert len(loaded_data) == len(filenames)
    assert set(loaded_data.keys()) == set(data_dict.keys())
    for name, loaded_df in loaded_data.items():
        pd.testing.assert_frame_equal(loaded_df, data_dict[name])


# --- Tests for validation and backward compatibility ---


def test_load_single_file_subpath_validation(file_utils):
    """Test ValueError when sub_path and nested file_path are mixed."""
    with pytest.raises(ValueError) as exc_info:
        file_utils.load_single_file(
            file_path="some_dir/some_file.csv",  # Nested file_path
            input_type="processed",
            sub_path="another_dir",  # Also providing sub_path
        )
    assert "already contains directory separators" in str(exc_info.value)

    # Also test with Azure path
    with pytest.raises(ValueError) as exc_info:
        file_utils.load_single_file(
            file_path="azure://container/blob/path/file.csv",  # Azure path
            input_type="processed",  # input_type is ignored for azure path
            sub_path="a_sub_path",  # sub_path is invalid here
        )
    assert "Cannot use sub_path with an absolute Azure path" in str(exc_info.value)


def test_load_multiple_files_subpath_validation(file_utils):
    """Test ValueError when sub_path and nested file_paths are mixed in list."""
    with pytest.raises(ValueError) as exc_info:
        file_utils.load_multiple_files(
            file_paths=["file1.csv", "subdir/file2.csv"],  # One path is nested
            input_type="processed",
            sub_path="target_dir",  # Also providing sub_path
        )
    assert "already contains directory separators" in str(exc_info.value)


def test_load_single_file_backward_compatibility(file_utils, sample_df):
    """Test loading with nested file_path and NO sub_path works as before."""
    sub_path = "bc_level1/bc_level2"
    file_name = "bc_test.csv"
    nested_file_path = f"{sub_path}/{file_name}"  # Path provided in file_path arg
    output_type = "processed"

    # Save a file normally (using our new save feature)
    file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=Path(file_name).stem,
        sub_path=sub_path,
        include_timestamp=False,
    )

    # Load using the OLD way: nested path in file_path, sub_path=None
    loaded_df = file_utils.load_single_file(
        file_path=nested_file_path,
        input_type=output_type,
        # sub_path=None # Default
    )
    pd.testing.assert_frame_equal(loaded_df, sample_df)


# New tests for document functionality
def test_save_json_as_document(file_utils):
    """Test saving JSON as structured document."""
    config_data = {
        "database": {"host": "localhost", "port": 5432, "name": "test_db"},
        "api": {"timeout": 30, "retries": 3, "base_url": "https://api.example.com"},
        "features": {"enable_caching": True, "cache_ttl": 3600},
    }

    saved_path, _ = file_utils.save_document_to_storage(
        content=config_data,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="app_config",
        include_timestamp=False,
    )

    assert Path(saved_path).exists()
    assert saved_path.endswith(".json")

    # Load and verify
    loaded_config = file_utils.load_json(
        file_path="app_config.json", input_type="processed"
    )

    assert loaded_config["database"]["host"] == "localhost"
    assert loaded_config["api"]["timeout"] == 30
    assert loaded_config["features"]["enable_caching"] is True


def test_save_yaml_as_document(file_utils):
    """Test saving YAML as structured document."""
    pipeline_config = {
        "project": {"name": "Test Pipeline", "version": "1.0.0"},
        "data_sources": {
            "primary": {
                "type": "database",
                "connection": "postgresql://localhost:5432/test",
            }
        },
        "processing": {"batch_size": 1000, "parallel_workers": 4},
    }

    saved_path, _ = file_utils.save_document_to_storage(
        content=pipeline_config,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="pipeline_config",
        include_timestamp=False,
    )

    assert Path(saved_path).exists()
    assert saved_path.endswith(".yaml")

    # Load and verify
    loaded_config = file_utils.load_yaml(
        file_path="pipeline_config.yaml", input_type="processed"
    )

    assert loaded_config["project"]["name"] == "Test Pipeline"
    assert loaded_config["processing"]["batch_size"] == 1000


def test_json_yaml_document_with_subpath(file_utils):
    """Test saving JSON/YAML documents with subpath."""
    config_data = {"test": "value", "nested": {"key": "value"}}

    # Test JSON with subpath
    saved_path, _ = file_utils.save_document_to_storage(
        content=config_data,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="test_config",
        sub_path="configs/app",
        include_timestamp=False,
    )

    assert Path(saved_path).exists()
    assert "configs/app" in str(saved_path).replace("\\", "/")

    # Load and verify
    loaded_config = file_utils.load_json(
        file_path="test_config.json", input_type="processed", sub_path="configs/app"
    )

    assert loaded_config["test"] == "value"
    assert loaded_config["nested"]["key"] == "value"


def test_automatic_pandas_type_conversion(file_utils, sample_df):
    """Test automatic conversion of pandas types in JSON."""
    # Create data with pandas types that need conversion
    df_with_types = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "timestamp": pd.Timestamp.now(),
            "int64": pd.Series([1, 2, 3], dtype="int64"),
            "float64": pd.Series([1.1, 2.2, 3.3], dtype="float64"),
            "category": pd.Categorical(["A", "B", "C"]),
        }
    )

    # Create JSON data with pandas types
    json_data = {
        "metadata": {"created": pd.Timestamp.now(), "version": "1.0"},
        "summary": {
            "total_rows": len(df_with_types),
            "date_range": {
                "start": df_with_types["date"].min(),
                "end": df_with_types["date"].max(),
            },
        },
        "data": df_with_types.to_dict("records"),
    }

    # This should work without manual conversion due to PandasJSONEncoder
    saved_path, _ = file_utils.save_document_to_storage(
        content=json_data,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="pandas_types_test",
        include_timestamp=False,
    )

    assert Path(saved_path).exists()

    # Load and verify types are properly converted
    loaded_data = file_utils.load_json(
        file_path="pandas_types_test.json", input_type="processed"
    )

    # Check that pandas types were converted to JSON-serializable types
    assert isinstance(loaded_data["metadata"]["created"], str)  # Timestamp -> string
    assert isinstance(
        loaded_data["summary"]["date_range"]["start"], str
    )  # Timestamp -> string
    assert isinstance(
        loaded_data["summary"]["date_range"]["end"], str
    )  # Timestamp -> string
    assert isinstance(loaded_data["summary"]["total_rows"], int)  # int64 -> int
    assert isinstance(loaded_data["data"][0]["int64"], int)  # int64 -> int
    assert isinstance(loaded_data["data"][0]["float64"], float)  # float64 -> float


def test_intelligent_timestamp_handling(file_utils, sample_df):
    """Test intelligent timestamp handling in load methods."""
    # Save file with timestamp
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="timestamped_file",
        include_timestamp=True,  # This will add a timestamp
    )

    # The file will be saved as something like "timestamped_file_20241019_123456.csv"
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Load using base filename (should find the timestamped version)
    loaded_df = file_utils.load_single_file(
        file_path="timestamped_file.csv",  # Base name without timestamp
        input_type="processed",
    )

    pd.testing.assert_frame_equal(loaded_df, sample_df)


def test_multiindex_dataframe_excel(file_utils):
    """Test MultiIndex DataFrame handling in Excel."""
    # Create MultiIndex DataFrame
    data = {
        ("Sales", "Q1"): [100, 200, 300],
        ("Sales", "Q2"): [150, 250, 350],
        ("Marketing", "Q1"): [50, 75, 100],
        ("Marketing", "Q2"): [60, 80, 110],
    }

    df_multiindex = pd.DataFrame(data, index=["Product A", "Product B", "Product C"])
    df_multiindex.columns = pd.MultiIndex.from_tuples(df_multiindex.columns)

    # Save as Excel (should handle MultiIndex automatically)
    saved_files, _ = file_utils.save_data_to_storage(
        data={"multi_sheet": df_multiindex},
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="multiindex_test",
        include_timestamp=False,
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Load and verify MultiIndex was handled correctly
    loaded_df = file_utils.load_single_file(
        file_path="multiindex_test.xlsx", input_type="processed"
    )

    # The MultiIndex columns should be flattened, and index should be included
    expected_columns = [
        "Unnamed: 0",
        "Sales_Q1",
        "Sales_Q2",
        "Marketing_Q1",
        "Marketing_Q2",
    ]
    assert list(loaded_df.columns) == expected_columns

    # Verify the data is correct (excluding the index column)
    data_columns = ["Sales_Q1", "Sales_Q2", "Marketing_Q1", "Marketing_Q2"]
    assert loaded_df[data_columns].iloc[0].tolist() == [100, 150, 50, 60]
    assert loaded_df[data_columns].iloc[1].tolist() == [200, 250, 75, 80]
    assert loaded_df[data_columns].iloc[2].tolist() == [300, 350, 100, 110]


def test_enhanced_json_encoder_edge_cases(file_utils):
    """Test enhanced JSON encoder with edge cases."""
    from datetime import datetime

    import numpy as np

    # Test various edge cases
    edge_case_data = {
        "numpy_int": np.int64(42),
        "numpy_float": np.float64(3.14),
        "numpy_array": np.array([1, 2, 3]),
        "datetime_obj": datetime.now(),
        "pandas_timestamp": pd.Timestamp("2024-01-01"),
        "nested_dict": {
            "inner_timestamp": pd.Timestamp.now(),
            "inner_numpy": np.int32(100),
        },
        "list_with_types": [pd.Timestamp.now(), np.float32(2.5), datetime.now()],
    }

    # This should work without errors due to PandasJSONEncoder
    saved_path, _ = file_utils.save_document_to_storage(
        content=edge_case_data,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="edge_cases_test",
        include_timestamp=False,
    )

    assert Path(saved_path).exists()

    # Load and verify all types were converted
    loaded_data = file_utils.load_json(
        file_path="edge_cases_test.json", input_type="processed"
    )

    # All pandas/numpy types should be converted to JSON-serializable types
    assert isinstance(loaded_data["numpy_int"], int)
    assert isinstance(loaded_data["numpy_float"], float)
    assert isinstance(loaded_data["numpy_array"], list)
    assert isinstance(loaded_data["datetime_obj"], str)
    assert isinstance(loaded_data["pandas_timestamp"], str)
    assert isinstance(loaded_data["nested_dict"]["inner_timestamp"], str)
    assert isinstance(loaded_data["nested_dict"]["inner_numpy"], int)
    assert isinstance(loaded_data["list_with_types"][0], str)
    assert isinstance(loaded_data["list_with_types"][1], float)
    assert isinstance(loaded_data["list_with_types"][2], str)


# Excel ↔ CSV Conversion Tests


def test_convert_excel_to_csv_with_structure_basic(file_utils, sample_df):
    """Test basic Excel to CSV conversion with structure preservation."""
    # Create a multi-sheet Excel workbook
    workbook_data = {"Sheet1": sample_df, "Sheet2": sample_df.copy()}

    # Save Excel workbook first
    saved_files, _ = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="test_workbook",
    )

    excel_file_path = list(saved_files.values())[0]

    # Convert Excel to CSV with structure
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="converted_workbook",
    )

    # Verify CSV files were created
    assert len(csv_files) == 2
    assert "Sheet1" in csv_files
    assert "Sheet2" in csv_files

    # Verify CSV files exist and have correct content
    for sheet_name, csv_path in csv_files.items():
        assert Path(csv_path).exists()
        loaded_df = pd.read_csv(csv_path)
        pd.testing.assert_frame_equal(loaded_df, sample_df)

    # Verify structure file exists and has correct content
    assert Path(structure_file).exists()
    with open(structure_file, "r") as f:
        structure_data = json.load(f)

    assert "workbook_info" in structure_data
    assert "sheets" in structure_data
    assert structure_data["workbook_info"]["total_sheets"] == 2
    assert len(structure_data["sheets"]) == 2

    # Verify sheet metadata
    for sheet_name in ["Sheet1", "Sheet2"]:
        assert sheet_name in structure_data["sheets"]
        sheet_info = structure_data["sheets"][sheet_name]
        assert "csv_file" in sheet_info
        assert "dimensions" in sheet_info
        assert "columns" in sheet_info
        assert "data_info" in sheet_info
        assert sheet_info["dimensions"]["rows"] == len(sample_df)
        assert sheet_info["dimensions"]["columns"] == len(sample_df.columns)


def test_convert_excel_to_csv_with_structure_no_preserve(file_utils, sample_df):
    """Test Excel to CSV conversion without structure preservation."""
    # Create a multi-sheet Excel workbook
    workbook_data = {"Sheet1": sample_df, "Sheet2": sample_df.copy()}

    # Save Excel workbook first
    saved_files, _ = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="test_workbook_no_structure",
    )

    excel_file_path = list(saved_files.values())[0]

    # Convert Excel to CSV without structure preservation
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="converted_workbook_no_structure",
        preserve_structure=False,
    )

    # Verify CSV files were created
    assert len(csv_files) == 2

    # Verify no structure file was created
    assert structure_file == ""


def test_convert_csv_to_excel_workbook_basic(file_utils, sample_df):
    """Test basic CSV to Excel workbook reconstruction."""
    # First create CSV files with structure
    workbook_data = {"Sheet1": sample_df, "Sheet2": sample_df.copy()}

    # Save Excel workbook first
    saved_files, _ = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="test_workbook_reconstruction",
    )

    excel_file_path = list(saved_files.values())[0]

    # Convert Excel to CSV with structure
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="test_workbook_reconstruction",
    )

    # Now reconstruct Excel workbook from CSV files
    reconstructed_excel = file_utils.convert_csv_to_excel_workbook(
        structure_json_path=structure_file,
        input_type="processed",
        output_type="processed",
        file_name="reconstructed_workbook",
    )

    # Verify reconstructed Excel file exists
    assert Path(reconstructed_excel).exists()

    # Verify reconstructed Excel has correct content
    reconstructed_sheets = file_utils.load_excel_sheets(
        Path(reconstructed_excel).name, input_type="processed"
    )

    assert len(reconstructed_sheets) == 2
    assert "Sheet1" in reconstructed_sheets
    assert "Sheet2" in reconstructed_sheets

    # Verify content matches original
    for sheet_name, df in reconstructed_sheets.items():
        pd.testing.assert_frame_equal(df, sample_df)


def test_excel_csv_roundtrip_workflow(file_utils, sample_df):
    """Test complete Excel ↔ CSV round-trip workflow."""
    # Step 1: Create Excel workbook
    workbook_data = {
        "Sales": sample_df,
        "Customers": sample_df.copy(),
        "Products": sample_df.copy(),
    }

    saved_files, _ = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="roundtrip_workbook",
    )

    excel_file_path = list(saved_files.values())[0]

    # Step 2: Convert Excel to CSV
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="roundtrip_workbook",
    )

    # Step 3: Modify CSV data
    modified_df = sample_df.copy()
    modified_df["processed"] = True

    # Save modified Sales data
    file_utils.save_data_to_storage(
        data=modified_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="roundtrip_workbook_Sales",
        include_timestamp=False,
    )

    # Step 4: Reconstruct Excel workbook
    reconstructed_excel = file_utils.convert_csv_to_excel_workbook(
        structure_json_path=structure_file,
        input_type="processed",
        output_type="processed",
        file_name="roundtrip_reconstructed",
    )

    # Step 5: Verify round-trip
    assert Path(reconstructed_excel).exists()

    reconstructed_sheets = file_utils.load_excel_sheets(
        Path(reconstructed_excel).name, input_type="processed"
    )

    assert len(reconstructed_sheets) == 3
    assert "Sales" in reconstructed_sheets
    assert "Customers" in reconstructed_sheets
    assert "Products" in reconstructed_sheets

    # Verify Sales sheet has modifications
    assert "processed" in reconstructed_sheets["Sales"].columns
    assert all(reconstructed_sheets["Sales"]["processed"] == True)

    # Verify other sheets are unchanged
    pd.testing.assert_frame_equal(reconstructed_sheets["Customers"], sample_df)
    pd.testing.assert_frame_equal(reconstructed_sheets["Products"], sample_df)


# Configurable Directory Tests


def test_configurable_directory_default(file_utils, sample_df):
    """Test default directory configuration."""
    # Test default configuration
    dir_config = file_utils._get_directory_config()

    assert dir_config["data_directory"] == "data"
    assert dir_config["raw"] == "raw"
    assert dir_config["processed"] == "processed"
    assert dir_config["templates"] == "templates"

    # Test path generation
    raw_path = file_utils.get_data_path("raw")
    processed_path = file_utils.get_data_path("processed")

    assert "data/raw" in str(raw_path).replace("\\", "/")
    assert "data/processed" in str(processed_path).replace("\\", "/")
    assert raw_path.exists()
    assert processed_path.exists()


def test_configurable_directory_custom(temp_dir, sample_df):
    """Test custom directory configuration."""
    # Create custom config
    custom_config = {
        "directories": {
            "data_directory": "documents",
            "subdirectories": {
                "raw": "product_docs",
                "processed": "cs_documents",
                "templates": "templates",
            },
        }
    }

    file_utils = FileUtils(project_root=temp_dir, config_override=custom_config)

    # Test custom configuration
    dir_config = file_utils._get_directory_config()

    assert dir_config["data_directory"] == "documents"
    assert dir_config["raw"] == "product_docs"
    assert dir_config["processed"] == "cs_documents"
    assert dir_config["templates"] == "templates"

    # Test path generation
    raw_path = file_utils.get_data_path("raw")
    processed_path = file_utils.get_data_path("processed")

    assert "documents/product_docs" in str(raw_path).replace("\\", "/")
    assert "documents/cs_documents" in str(processed_path).replace("\\", "/")
    assert raw_path.exists()
    assert processed_path.exists()


def test_configurable_directory_file_operations(temp_dir, sample_df):
    """Test file operations with custom directory configuration."""
    # Create custom config
    custom_config = {
        "directories": {
            "data_directory": "documents",
            "subdirectories": {
                "raw": "product_docs",
                "processed": "cs_documents",
                "templates": "templates",
            },
        }
    }

    file_utils = FileUtils(project_root=temp_dir, config_override=custom_config)

    # Test saving data
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="test_data",
    )

    # Verify file was saved in custom directory
    saved_path = list(saved_files.values())[0]
    assert "documents/product_docs" in str(saved_path).replace("\\", "/")
    assert Path(saved_path).exists()

    # Test loading data
    loaded_df = file_utils.load_single_file("test_data.csv", input_type="raw")
    pd.testing.assert_frame_equal(loaded_df, sample_df)

    # Test saving to processed directory
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="processed_data",
    )

    # Verify file was saved in custom processed directory
    saved_path = list(saved_files.values())[0]
    assert "documents/cs_documents" in str(saved_path).replace("\\", "/")
    assert Path(saved_path).exists()


def test_configurable_directory_excel_csv_conversion(temp_dir, sample_df):
    """Test Excel ↔ CSV conversion with custom directory configuration."""
    # Create custom config
    custom_config = {
        "directories": {
            "data_directory": "documents",
            "subdirectories": {
                "raw": "product_docs",
                "processed": "cs_documents",
                "templates": "templates",
            },
        }
    }

    file_utils = FileUtils(project_root=temp_dir, config_override=custom_config)

    # Create Excel workbook
    workbook_data = {"Sheet1": sample_df, "Sheet2": sample_df.copy()}

    saved_files, _ = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="test_workbook",
    )

    excel_file_path = list(saved_files.values())[0]
    assert "documents/product_docs" in str(excel_file_path).replace("\\", "/")

    # Convert Excel to CSV
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="converted_workbook",
    )

    # Verify CSV files were created in custom processed directory
    assert len(csv_files) == 2
    for sheet_name, csv_path in csv_files.items():
        assert "documents/cs_documents" in str(csv_path).replace("\\", "/")
        assert Path(csv_path).exists()

    # Verify structure file was created in custom processed directory
    assert "documents/cs_documents" in str(structure_file).replace("\\", "/")
    assert Path(structure_file).exists()

    # Test CSV to Excel reconstruction
    reconstructed_excel = file_utils.convert_csv_to_excel_workbook(
        structure_json_path=structure_file,
        input_type="processed",
        output_type="processed",
        file_name="reconstructed_workbook",
    )

    # Verify reconstructed Excel was created in custom processed directory
    assert "documents/cs_documents" in str(reconstructed_excel).replace("\\", "/")
    assert Path(reconstructed_excel).exists()


def test_configurable_directory_create_directory(temp_dir):
    """Test create_directory with custom directory configuration."""
    # Create custom config
    custom_config = {
        "directories": {
            "data_directory": "documents",
            "subdirectories": {
                "raw": "product_docs",
                "processed": "cs_documents",
                "templates": "templates",
            },
        }
    }

    file_utils = FileUtils(project_root=temp_dir, config_override=custom_config)

    # Test creating directory with default parent (should use configured data directory)
    custom_dir = file_utils.create_directory("ai_plans")
    custom_dir_path = Path(custom_dir)  # Now returns string, convert to Path

    assert "documents/ai_plans" in str(custom_dir_path).replace("\\", "/")
    assert custom_dir_path.exists()

    # Test creating directory with explicit parent
    custom_dir2 = file_utils.create_directory("reports", parent_dir="documents")
    custom_dir2_path = Path(custom_dir2)  # Now returns string, convert to Path

    assert "documents/reports" in str(custom_dir2_path).replace("\\", "/")
    assert custom_dir2_path.exists()


def test_configurable_directory_backward_compatibility(file_utils, sample_df):
    """Test backward compatibility with existing projects."""
    # Test that existing projects still work with default configuration
    raw_path = file_utils.get_data_path("raw")
    processed_path = file_utils.get_data_path("processed")

    # Should still use "data" directory
    assert "data/raw" in str(raw_path).replace("\\", "/")
    assert "data/processed" in str(processed_path).replace("\\", "/")

    # Test file operations still work
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="compatibility_test",
    )

    saved_path = list(saved_files.values())[0]
    assert "data/raw" in str(saved_path).replace("\\", "/")
    assert Path(saved_path).exists()


def test_configurable_directory_partial_config(temp_dir, sample_df):
    """Test partial directory configuration (only data_directory specified)."""
    # Create partial config (only data_directory)
    partial_config = {
        "directories": {
            "data_directory": "documents"
            # subdirectories not specified - should use defaults
        }
    }

    file_utils = FileUtils(project_root=temp_dir, config_override=partial_config)

    # Test configuration
    dir_config = file_utils._get_directory_config()

    assert dir_config["data_directory"] == "documents"
    assert dir_config["raw"] == "raw"  # Default
    assert dir_config["processed"] == "processed"  # Default
    assert dir_config["templates"] == "templates"  # Default

    # Test path generation
    raw_path = file_utils.get_data_path("raw")
    processed_path = file_utils.get_data_path("processed")

    assert "documents/raw" in str(raw_path).replace("\\", "/")
    assert "documents/processed" in str(processed_path).replace("\\", "/")
    assert raw_path.exists()
    assert processed_path.exists()


def test_root_level_save_and_load(temp_dir, sample_df):
    """Test saving and loading files to/from root-level directories."""
    file_utils = FileUtils(project_root=temp_dir)

    # Save to root-level config directory
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="config",
        file_name="test_config",
        root_level=True,
    )

    saved_path = list(saved_files.values())[0]
    # Should be in project_root/config/, not project_root/data/config/
    assert "config" in str(saved_path)
    assert "data" not in str(saved_path) or "/data/config" not in str(saved_path)
    assert Path(saved_path).exists()
    assert (temp_dir / "config").exists()

    # Load from root-level config directory
    loaded_df = file_utils.load_single_file(
        file_path="test_config.csv", input_type="config", root_level=True
    )

    assert len(loaded_df) == len(sample_df)
    assert list(loaded_df.columns) == list(sample_df.columns)


def test_root_level_document_operations(temp_dir):
    """Test saving and loading documents from root-level directories."""
    file_utils = FileUtils(project_root=temp_dir)

    config_data = {
        "database": {"host": "localhost", "port": 5432},
        "api": {"timeout": 30},
    }

    # Save JSON config to root-level config directory
    saved_path, _ = file_utils.save_document_to_storage(
        content=config_data,
        output_filetype=OutputFileType.JSON,
        output_type="config",
        file_name="app_config",
        root_level=True,
    )

    assert "config" in str(saved_path)
    assert Path(saved_path).exists()
    assert (temp_dir / "config").exists()

    # Load from root-level config directory
    loaded_config = file_utils.load_json(
        file_path="app_config.json", input_type="config", root_level=True
    )

    assert loaded_config["database"]["host"] == "localhost"
    assert loaded_config["api"]["timeout"] == 30


def test_root_level_with_subpath(temp_dir, sample_df):
    """Test root-level directories with sub_path."""
    file_utils = FileUtils(project_root=temp_dir)

    # Save to root-level config with subpath
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="config",
        file_name="nested_config",
        sub_path="environments/production",
        root_level=True,
    )

    saved_path = list(saved_files.values())[0]
    assert "config/environments/production" in str(saved_path).replace("\\", "/")
    assert Path(saved_path).exists()
    assert (temp_dir / "config" / "environments" / "production").exists()


def test_root_level_vs_data_directory(temp_dir, sample_df):
    """Test that root_level=True creates directories at root, not under data."""
    file_utils = FileUtils(project_root=temp_dir)

    # Save with root_level=True
    saved_root, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="logs",
        file_name="root_logs",
        root_level=True,
    )

    # Save with root_level=False (default)
    saved_data, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type="logs",
        file_name="data_logs",
        root_level=False,
    )

    root_path = list(saved_root.values())[0]
    data_path = list(saved_data.values())[0]

    # Root-level should be in logs/ at project root
    assert str(temp_dir / "logs") in str(root_path)
    assert "data" not in str(root_path) or not str(root_path).replace(
        str(temp_dir), ""
    ).startswith("/data")

    # Data-level should be in data/logs/
    assert str(temp_dir / "data" / "logs") in str(data_path)

    # Both should exist
    assert Path(root_path).exists()
    assert Path(data_path).exists()


def test_root_level_yaml_operations(temp_dir):
    """Test YAML operations with root-level directories."""
    file_utils = FileUtils(project_root=temp_dir)

    yaml_config = {
        "project": {"name": "TestProject", "version": "1.0.0"},
        "settings": {"debug": True},
    }

    # Save YAML to root-level config directory
    saved_path, _ = file_utils.save_document_to_storage(
        content=yaml_config,
        output_filetype=OutputFileType.YAML,
        output_type="config",
        file_name="project_config",
        root_level=True,
    )

    assert "config" in str(saved_path)
    assert Path(saved_path).exists()

    # Load YAML from root-level config directory
    loaded_config = file_utils.load_yaml(
        file_path="project_config.yaml", input_type="config", root_level=True
    )

    assert loaded_config["project"]["name"] == "TestProject"
    assert loaded_config["settings"]["debug"] is True


def test_root_level_get_base_path(temp_dir):
    """Test the _get_base_path helper method."""
    file_utils = FileUtils(project_root=temp_dir)

    # Root-level directory
    root_path = file_utils._get_base_path("config", root_level=True)
    assert root_path == temp_dir / "config"
    assert root_path.exists()

    # Data-level directory (default)
    data_path = file_utils._get_base_path("processed", root_level=False)
    assert "data" in str(data_path)
    assert data_path.exists()

    # Root-level None (project root itself)
    project_root_path = file_utils._get_base_path(None, root_level=True)
    assert project_root_path == temp_dir
