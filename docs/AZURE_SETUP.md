# Azure Storage Setup Guide

Complete guide for setting up and using Azure Storage with FileUtils.

## Quick Start

```python
from FileUtils import FileUtils, StorageType

# Initialize with Azure storage
file_utils = FileUtils(
    storage_type=StorageType.AZURE,
    connection_string="your_connection_string"
)

# Save data directly to Azure
saved_files, _ = file_utils.save_data_to_storage(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="azure_data"
)
```

## Azure Storage Setup

### 1. Prerequisites
- Azure account with active subscription
- Storage Account created in Azure
- Required permissions:
  - `Storage Blob Data Contributor`
  - `Storage Account Contributor`

### 2. Connection Configuration

Choose one of these methods:

1. Environment Variable:
```bash
# Windows
set AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."

# Linux/macOS
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
```

2. Configuration File:
```yaml
# config.yaml
storage:
  default_type: "azure"
  azure:
    enabled: true
    connection_string: "DefaultEndpointsProtocol=https;AccountName=..."
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
      interim: "interim-data"
    retry_settings:
      max_retries: 3
      retry_delay: 1
      max_delay: 30
```

3. Direct initialization:
```python
file_utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string",
    config_file="config.yaml"
)
```

### 3. Container Setup

Containers are automatically created based on configuration:

```yaml
# config.yaml
storage:
  azure:
    container_mapping:
      raw: "raw-data"        # for raw data
      processed: "processed-data"    # for processed data
      interim: "interim-data"      # for intermediate data
      configurations: "config"    # for configuration files
```

Manual container verification:
```python
from FileUtils.storage.azure import AzureStorage

# Verify containers exist
storage = file_utils.storage
if isinstance(storage, AzureStorage):
    print("Container status:")
    for output_type, container in storage.container_mapping.items():
        exists = storage.container_exists(container)
        print(f"{output_type}: {container} - {'exists' if exists else 'missing'}")
```

## Usage Examples

### Basic Operations

```python
# Save DataFrame to Azure
saved_files, _ = file_utils.save_data_to_storage(
    data=df,
    output_filetype="parquet",
    output_type="processed",
    file_name="azure_data"
)

# Load from Azure
azure_path = saved_files["data"]  # Contains azure:// URI
loaded_df = file_utils.load_single_file(azure_path)
```

### Multiple Files

```python
# Save multiple DataFrames
data_dict = {
    'sales': sales_df,
    'inventory': inventory_df
}

saved_files, _ = file_utils.save_data_to_storage(
    data=data_dict,
    output_filetype="xlsx",
    output_type="processed",
    file_name="report"
)

# Load Excel sheets
sheets = file_utils.load_excel_sheets(saved_files["report"])
```

### Fallback Handling

```python
try:
    # Try Azure first
    file_utils = FileUtils(
        storage_type="azure",
        connection_string="your_connection_string"
    )
except StorageConnectionError:
    # Fallback to local storage
    print("Azure connection failed, using local storage")
    file_utils = FileUtils(storage_type="local")
```

## Performance Optimization

1. Use appropriate file formats:
```python
# For large datasets
file_utils.save_data_to_storage(
    data=large_df,
    output_filetype="parquet",  # Better compression
    output_type="processed"
)

# For smaller, human-readable data
file_utils.save_data_to_storage(
    data=small_df,
    output_filetype="csv",
    output_type="processed"
)
```

2. Batch operations:
```python
# Better performance
file_utils.save_data_to_storage(
    data={"file1": df1, "file2": df2},
    output_filetype="parquet"
)

# Avoid multiple individual saves
# for df in dataframes:
#     file_utils.save_data_to_storage(data=df, ...)
```

3. Configure retry settings:
```yaml
storage:
  azure:
    retry_settings:
      max_retries: 3
      retry_delay: 1
      max_delay: 30
```

## Security Best Practices

1. Connection String Management:
```python
# Use environment variables (preferred)
import os
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Or use dotenv file
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
```

2. Container Access:
```yaml
storage:
  azure:
    container_mapping:
      sensitive: "restricted-access"
      public: "public-access"
```

## Troubleshooting

### Common Issues

1. Connection Errors:
```python
from FileUtils.core.base import StorageConnectionError

try:
    file_utils = FileUtils(
        storage_type="azure",
        connection_string="invalid_string"
    )
except StorageConnectionError as e:
    print(f"Connection error: {e}")
    # Handle connection error
```

2. Permission Issues:
```python
try:
    file_utils.save_data_to_storage(
        data=df,
        output_type="restricted"
    )
except StorageError as e:
    if "AuthorizationFailure" in str(e):
        print("Permission denied - check Azure role assignments")
```

3. Container Issues:
```python
# Verify container exists
if not file_utils.storage.container_exists("my-container"):
    print("Container missing - check configuration")
```

### Debug Mode

Enable detailed logging:
```python
file_utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string",
    log_level="DEBUG"
)
```

### Validation Steps

1. Test connection:
```python
def test_azure_connection(connection_string: str) -> bool:
    try:
        utils = FileUtils(
            storage_type="azure",
            connection_string=connection_string
        )
        # Try a simple operation
        utils.save_data_to_storage(
            data=pd.DataFrame({"test": [1]}),
            output_type="processed",
            file_name="connection_test"
        )
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False
```

2. Verify permissions:
```python
def verify_azure_permissions(file_utils: FileUtils) -> dict:
    results = {}
    for operation in ["list", "read", "write"]:
        try:
            if operation == "list":
                _ = file_utils.storage.list_files("processed")
            elif operation == "read":
                _ = file_utils.load_single_file("test.csv")
            else:
                _ = file_utils.save_data_to_storage(
                    data=pd.DataFrame({"test": [1]}),
                    file_name="test"
                )
            results[operation] = "success"
        except Exception as e:
            results[operation] = f"failed: {str(e)}"
    return results
```

For general usage instructions, see [Usage Guide](USAGE.md).