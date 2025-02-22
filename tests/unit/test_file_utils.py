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
