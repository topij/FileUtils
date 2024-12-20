# tests/integration/test_azure_storage.py

import os
from pathlib import Path
import json
import yaml
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError

from FileUtils import FileUtils
from FileUtils.core.enums import OutputFileType, StorageType
from FileUtils.core.base import StorageError


# Fixtures
@pytest.fixture
def azure_credentials():
    """Get Azure credentials from environment or skip test."""
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        pytest.skip("Azure Storage connection string not available")
    return connection_string


@pytest.fixture
def azure_utils(azure_credentials, temp_dir):
    """Create FileUtils instance with Azure storage."""
    return FileUtils(
        project_root=temp_dir,
        storage_type=StorageType.AZURE,
        connection_string=azure_credentials,
    )


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "London", "Paris"],
        }
    )


# Mock Tests
def test_azure_fallback_on_error(temp_dir):
    """Test fallback to local storage when Azure fails."""
    with patch("azure.storage.blob.BlobServiceClient") as mock_client:
        mock_client.from_connection_string.side_effect = Exception(
            "Azure connection failed"
        )

        utils = FileUtils(
            project_root=temp_dir,
            storage_type=StorageType.AZURE,
            connection_string="invalid_connection_string",
        )

        assert utils.storage.__class__.__name__ == "LocalStorage"


def test_azure_container_creation(azure_credentials):
    """Test Azure container creation."""
    with patch("azure.storage.blob.BlobServiceClient") as mock_client:
        mock_service = MagicMock()
        mock_client.from_connection_string.return_value = mock_service

        utils = FileUtils(
            storage_type=StorageType.AZURE, connection_string=azure_credentials
        )

        # Verify container creation calls
        mock_service.create_container.assert_called()


# Real Azure Integration Tests
def test_save_single_file(azure_utils, sample_data):
    """Test saving single file to Azure."""
    saved_files, _ = azure_utils.save_data_to_storage(
        data=sample_data,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="test_azure_single",
    )

    assert len(saved_files) == 1
    azure_path = next(iter(saved_files.values()))
    assert azure_path.startswith("azure://")

    # Verify we can load it back
    loaded_df = azure_utils.load_single_file(azure_path)
    pd.testing.assert_frame_equal(loaded_df, sample_data)


def test_save_multiple_files(azure_utils, sample_data):
    """Test saving multiple files to Azure."""
    data_dict = {"first": sample_data, "second": sample_data.copy()}

    saved_files, _ = azure_utils.save_data_to_storage(
        data=data_dict,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="test_azure_multi",
    )

    assert len(saved_files) == 1  # One Excel file with multiple sheets
    azure_path = next(iter(saved_files.values()))

    # Load and verify
    loaded_sheets = azure_utils.load_excel_sheets(azure_path)
    assert set(loaded_sheets.keys()) == set(data_dict.keys())
    for name, df in data_dict.items():
        pd.testing.assert_frame_equal(loaded_sheets[name], df)


def test_azure_file_not_found(azure_utils):
    """Test handling of missing files."""
    with pytest.raises(StorageError):
        azure_utils.load_single_file("azure://nonexistent-container/nonexistent.csv")


def test_azure_invalid_container(azure_utils, sample_data):
    """Test handling of invalid container."""
    with pytest.raises(StorageError):
        azure_utils.save_data_to_storage(
            data=sample_data,
            output_filetype=OutputFileType.CSV,
            output_type="invalid_container",
            file_name="test_invalid",
        )


@pytest.mark.parametrize(
    "file_format", [OutputFileType.CSV, OutputFileType.XLSX, OutputFileType.PARQUET]
)
def test_azure_file_formats(azure_utils, sample_data, file_format):
    """Test different file formats with Azure storage."""
    saved_files, _ = azure_utils.save_data_to_storage(
        data=sample_data,
        output_filetype=file_format,
        output_type="processed",
        file_name=f"test_format_{file_format.value}",
    )

    azure_path = next(iter(saved_files.values()))
    loaded_df = azure_utils.load_single_file(azure_path)
    pd.testing.assert_frame_equal(loaded_df, sample_data)


def test_azure_large_file(azure_utils):
    """Test handling of larger files."""
    large_df = pd.DataFrame(
        {"data": range(100000), "more_data": [f"data_{i}" for i in range(100000)]}
    )

    saved_files, _ = azure_utils.save_data_to_storage(
        data=large_df,
        output_filetype=OutputFileType.PARQUET,  # Use Parquet for efficiency
        output_type="processed",
        file_name="test_large_file",
    )

    azure_path = next(iter(saved_files.values()))
    loaded_df = azure_utils.load_single_file(azure_path)
    pd.testing.assert_frame_equal(loaded_df, large_df)


@pytest.mark.integration
def test_azure_load_yaml(azure_utils):
    """Test loading YAML file from Azure storage."""
    # Create and upload test YAML
    yaml_data = {"test": "data", "list": [1, 2, 3]}
    container_client = azure_utils.storage._get_container_client("raw")
    yaml_content = yaml.safe_dump(yaml_data)
    blob_client = container_client.get_blob_client("test.yaml")
    blob_client.upload_blob(yaml_content.encode("utf-8"), overwrite=True)

    # Test loading
    loaded_data = azure_utils.load_yaml("azure://raw/test.yaml")
    assert loaded_data == yaml_data


@pytest.mark.integration
def test_azure_load_json(azure_utils):
    """Test loading JSON file from Azure storage."""
    # Create and upload test JSON
    json_data = {"test": "data", "list": [1, 2, 3]}
    container_client = azure_utils.storage._get_container_client("raw")
    json_content = json.dumps(json_data)
    blob_client = container_client.get_blob_client("test.json")
    blob_client.upload_blob(json_content.encode("utf-8"), overwrite=True)

    # Test loading
    loaded_data = azure_utils.load_json("azure://raw/test.json")
    assert loaded_data == json_data


# Clean up test files after tests
@pytest.fixture(autouse=True)
def cleanup_azure(request, azure_utils):
    """Clean up Azure test files after tests."""
    yield
    if (
        hasattr(azure_utils, "storage")
        and azure_utils.storage.__class__.__name__ == "AzureStorage"
    ):
        try:
            # Clean up test containers or files here
            containers = ["processed", "raw", "interim"]
            for container in containers:
                container_client = azure_utils.storage._get_container_client(container)
                for blob in container_client.list_blobs():
                    if blob.name.startswith("test_"):
                        container_client.delete_blob(blob.name)
        except Exception as e:
            print(f"Warning: Failed to clean up Azure test files: {e}")


@pytest.mark.integration
def test_load_yaml_dataframe_azure(azure_storage, temp_container):
    """Test loading YAML file from Azure."""
    # Create test data
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    blob_name = "test_df.yaml"

    # Upload test data
    blob_client = azure_storage.blob_service_client.get_blob_client(
        container=temp_container, blob=blob_name
    )
    blob_client.upload_blob(yaml.safe_dump(data), overwrite=True)

    # Load and verify
    azure_path = f"azure://{temp_container}/{blob_name}"
    df = azure_storage.load_dataframe(azure_path)

    assert len(df) == 2
    assert sorted(df.columns) == ["age", "name"]
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [25, 30]


@pytest.mark.integration
def test_load_json_dataframe_azure(azure_storage, temp_container):
    """Test loading JSON file from Azure."""
    # Create test data
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
    blob_name = "test_df.json"

    # Upload test data
    blob_client = azure_storage.blob_service_client.get_blob_client(
        container=temp_container, blob=blob_name
    )
    blob_client.upload_blob(json.dumps(data), overwrite=True)

    # Load and verify
    azure_path = f"azure://{temp_container}/{blob_name}"
    df = azure_storage.load_dataframe(azure_path)

    assert len(df) == 2
    assert sorted(df.columns) == ["age", "name"]
    assert df["name"].tolist() == ["Alice", "Bob"]
    assert df["age"].tolist() == [25, 30]


@pytest.mark.integration
def test_save_json_dataframe_azure(azure_storage, temp_container):
    """Test saving DataFrame as JSON to Azure."""
    df = pd.DataFrame([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])

    # Save to Azure
    blob_name = "test_df.json"
    azure_path = f"azure://{temp_container}/{blob_name}"
    azure_storage.save_dataframe(df, azure_path)

    # Verify saved data
    blob_client = azure_storage.blob_service_client.get_blob_client(
        container=temp_container, blob=blob_name
    )
    content = blob_client.download_blob().readall()
    loaded_data = json.loads(content)

    assert len(loaded_data) == 2
    assert loaded_data[0]["name"] == "Alice"
    assert loaded_data[1]["age"] == 30


@pytest.mark.integration
def test_save_yaml_dataframe_azure(azure_storage, temp_container):
    """Test saving DataFrame as YAML to Azure."""
    df = pd.DataFrame([{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}])

    # Save to Azure
    blob_name = "test_df.yaml"
    azure_path = f"azure://{temp_container}/{blob_name}"
    azure_storage.save_dataframe(df, azure_path)

    # Verify saved data
    blob_client = azure_storage.blob_service_client.get_blob_client(
        container=temp_container, blob=blob_name
    )
    content = blob_client.download_blob().readall()
    loaded_data = yaml.safe_load(content)

    assert len(loaded_data) == 2
    assert loaded_data[0]["name"] == "Alice"
    assert loaded_data[1]["age"] == 30
