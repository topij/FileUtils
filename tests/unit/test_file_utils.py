# tests / unit / test_file_utils.py

import pytest
import pandas as pd
from pathlib import Path
import csv
import yaml
import json

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
    assert new_dir.exists()
    assert new_dir.is_dir()
    assert new_dir == file_utils.project_root / "data" / "features"
    assert "features" in file_utils.config["directory_structure"]["data"]

    # Create directory under reports
    reports_dir = file_utils.create_directory("monthly", parent_dir="reports")
    assert reports_dir.exists()
    assert reports_dir.is_dir()
    assert reports_dir == file_utils.project_root / "reports" / "monthly"
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
    assert dir1.exists()


def test_save_yaml_dataframe_records(file_utils, sample_df):
    """Test saving DataFrame to YAML in records format."""
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="test_yaml_records",
        yaml_options={"default_flow_style": False, "sort_keys": True},
        orient="records"
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file("test_yaml_records.yaml", input_type="processed")
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1)
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
        orient="index"
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file("test_yaml_index.yaml", input_type="processed")
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
        check_index_type=False  # Index type may change for YAML
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
        orient="records"
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file("test_json_records.json", input_type="processed")
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1)
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
        orient="index"
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file("test_json_index.json", input_type="processed")
    
    # Convert index to integers if possible
    if loaded_df.index.dtype == 'O' and all(idx.isdigit() for idx in loaded_df.index):
        loaded_df.index = loaded_df.index.astype(int)
    
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1),
        check_index_type=False  # Index type may change for JSON
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
            orient="invalid_orient"
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
            orient="invalid_orient"
        )
    assert "Invalid value 'invalid_orient' for option 'orient'" in str(exc_info.value)


def test_yaml_custom_options(file_utils, sample_df):
    """Test saving DataFrame to YAML with custom options."""
    yaml_options = {
        "default_flow_style": True,
        "sort_keys": True,
        "width": 80,
        "indent": 4
    }
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="test_yaml_custom",
        yaml_options=yaml_options
    )

    assert len(saved_files) == 1
    saved_path = Path(next(iter(saved_files.values())))
    assert saved_path.exists()

    # Verify content
    loaded_df = file_utils.load_single_file("test_yaml_custom.yaml", input_type="processed")
    pd.testing.assert_frame_equal(
        loaded_df.reindex(sorted(loaded_df.columns), axis=1),
        sample_df.reindex(sorted(sample_df.columns), axis=1)
    )


def test_save_multiple_dataframes_yaml(file_utils, sample_df):
    """Test saving multiple DataFrames to YAML files."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="multi_yaml",
        yaml_options={"default_flow_style": False}
    )

    assert len(saved_files) == len(data_dict)
    for sheet_name, file_path in saved_files.items():
        assert Path(file_path).exists()
        loaded_df = file_utils.load_single_file(Path(file_path).name, input_type="processed")
        pd.testing.assert_frame_equal(
            loaded_df.reindex(sorted(loaded_df.columns), axis=1),
            data_dict[sheet_name].reindex(sorted(data_dict[sheet_name].columns), axis=1)
        )


def test_save_multiple_dataframes_json(file_utils, sample_df):
    """Test saving multiple DataFrames to JSON files."""
    data_dict = {"sheet1": sample_df, "sheet2": sample_df.copy()}
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="multi_json",
        orient="records"
    )

    assert len(saved_files) == len(data_dict)
    for sheet_name, file_path in saved_files.items():
        assert Path(file_path).exists()
        loaded_df = file_utils.load_single_file(Path(file_path).name, input_type="processed")
        pd.testing.assert_frame_equal(
            loaded_df.reindex(sorted(loaded_df.columns), axis=1),
            data_dict[sheet_name].reindex(sorted(data_dict[sheet_name].columns), axis=1)
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

    assert len(saved_files) == 1 # Excel saves as one file
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
        output_filetype=OutputFileType.CSV, # Non-Excel saves separate files
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
    # Create an absolute path unlikely to exist, but valid structure
    abs_sub_path = Path("/abs/path/to/reports")
    relative_equivalent = "abs/path/to/reports" # How it should be treated
    file_name = "abs_subpath_test"
    output_type = "processed"

    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=file_name,
        sub_path=abs_sub_path, # Pass the absolute path
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
        include_timestamp=False # Disable timestamp for predictable filename
    )

    # Now, load using sub_path
    loaded_df = file_utils.load_single_file(
        file_path=file_name, # Just the filename
        input_type=output_type,
        sub_path=sub_path # Specify the sub_path
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
        include_timestamp=False
    )

    # Load using sub_path
    loaded_sheets = file_utils.load_excel_sheets(
        file_path=file_name, # Just the filename
        input_type=output_type,
        sub_path=sub_path
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
        file_path=file_name,
        input_type=input_type,
        sub_path=sub_path
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
        file_path=file_name,
        input_type=input_type,
        sub_path=sub_path
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
            include_timestamp=False
        )

    # Load using load_multiple_files with sub_path
    loaded_data = file_utils.load_multiple_files(
        file_paths=filenames, # List of filenames only
        input_type=output_type,
        sub_path=sub_path,
        file_type=OutputFileType.CSV # Optional: enforce type
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
            file_path="some_dir/some_file.csv", # Nested file_path
            input_type="processed",
            sub_path="another_dir" # Also providing sub_path
        )
    assert "already contains directory separators" in str(exc_info.value)

    # Also test with Azure path
    with pytest.raises(ValueError) as exc_info:
        file_utils.load_single_file(
            file_path="azure://container/blob/path/file.csv", # Azure path
            input_type="processed", # input_type is ignored for azure path
            sub_path="a_sub_path" # sub_path is invalid here
        )
    assert "Cannot use sub_path with an absolute Azure path" in str(exc_info.value)


def test_load_multiple_files_subpath_validation(file_utils):
    """Test ValueError when sub_path and nested file_paths are mixed in list."""
    with pytest.raises(ValueError) as exc_info:
        file_utils.load_multiple_files(
            file_paths=["file1.csv", "subdir/file2.csv"], # One path is nested
            input_type="processed",
            sub_path="target_dir" # Also providing sub_path
        )
    assert "already contains directory separators" in str(exc_info.value)


def test_load_single_file_backward_compatibility(file_utils, sample_df):
    """Test loading with nested file_path and NO sub_path works as before."""
    sub_path = "bc_level1/bc_level2"
    file_name = "bc_test.csv"
    nested_file_path = f"{sub_path}/{file_name}" # Path provided in file_path arg
    output_type = "processed"

    # Save a file normally (using our new save feature)
    file_utils.save_data_to_storage(
        data=sample_df,
        output_filetype=OutputFileType.CSV,
        output_type=output_type,
        file_name=Path(file_name).stem,
        sub_path=sub_path,
        include_timestamp=False
    )

    # Load using the OLD way: nested path in file_path, sub_path=None
    loaded_df = file_utils.load_single_file(
        file_path=nested_file_path,
        input_type=output_type,
        # sub_path=None # Default
    )
    pd.testing.assert_frame_equal(loaded_df, sample_df)
