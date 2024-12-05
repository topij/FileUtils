# Azure Storage Setup Guide

## Quick Start

```python
from FileUtils import FileUtils

# Initialize with Azure storage
utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)

# Save data
df = pd.DataFrame({'data': range(100)})
saved_files, metadata = utils.save_data_to_storage(
    data=df,
    output_filetype="parquet",
    output_type="processed",
    file_name="azure_data"
)

# Load data using Azure URI
loaded_df = utils.load_single_file(saved_files['data'])
```

## Azure Setup Process

### 1. Azure Prerequisites

- Azure account with active subscription
- Storage Account
  - Create in Azure Portal or using Azure CLI
  - Performance tier: Standard
  - Account kind: StorageV2 (recommended)
  - Replication: LRS/GRS based on needs
- Required permissions:
  - Storage Blob Data Contributor
  - Storage Account Contributor

### 2. Connection Configuration

Choose one of these methods:

#### Environment Variables
```bash
# Windows
set AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."

# Linux/macOS
export AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
```

#### Configuration File
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

#### Direct Initialization
```python
utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)
```

### 3. Container Structure

FileUtils automatically manages these containers:
- raw-data: Original data
- processed-data: Final processed data
- interim-data: Intermediate processing
- external-data: External data sources

Configure container names:
```yaml
storage:
  azure:
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
      interim: "interim-data"
      external: "external-data"
```

## Usage Examples

### Basic Operations

```python
# Save DataFrame
saved_files, metadata = utils.save_data_to_storage(
    data=df,
    output_filetype="parquet",
    output_type="processed",
    file_name="data"
)

# Load using Azure URI
azure_path = saved_files['data']  # Contains azure:// URI
loaded_df = utils.load_single_file(azure_path)
```

### Multiple Files

```python
# Save multiple DataFrames
data_dict = {
    'sales': sales_df,
    'inventory': inventory_df
}

saved_files, metadata = utils.save_data_to_storage(
    data=data_dict,
    output_filetype="xlsx",
    output_type="processed",
    file_name="report"
)

# Load Excel sheets
sheets = utils.load_excel_sheets(saved_files['report'])
```

### Metadata Handling

```python
# Save with metadata
saved_files, metadata_path = utils.save_with_metadata(
    data=data_dict,
    output_filetype="csv",
    output_type="processed",
    file_name="data_with_metadata"
)

# Load using metadata
loaded_data = utils.load_from_metadata(metadata_path)
```

## Performance Optimization

### 1. File Format Selection

```python
# Large datasets: Use Parquet
utils.save_data_to_storage(
    data=large_df,
    output_filetype="parquet",
    output_type="processed"
)

# Small, readable data: Use CSV
utils.save_data_to_storage(
    data=small_df,
    output_filetype="csv",
    output_type="processed"
)
```

### 2. Batch Operations

```python
# Efficient: Save multiple files at once
utils.save_data_to_storage(
    data={"file1": df1, "file2": df2},
    output_filetype="parquet"
)

# Less efficient: Save files individually
# for df in dataframes:
#     utils.save_data_to_storage(data=df, ...)
```

### 3. Retry Settings

```yaml
storage:
  azure:
    retry_settings:
      max_retries: 3
      retry_delay: 1
      max_delay: 30
```

## Security Best Practices

### 1. Connection String Management

```python
# Use environment variables (preferred)
import os
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Or use dotenv file
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
```

### 2. Access Control

- Use Azure RBAC (Role-Based Access Control)
- Assign minimum required permissions
- Use SAS tokens for temporary access
- Enable secure transfer (HTTPS)
- Configure network rules

## Troubleshooting

### Connection Issues
```python
try:
    utils = FileUtils(
        storage_type="azure",
        connection_string="connection_string"
    )
except StorageConnectionError as e:
    print(f"Connection error: {e}")
    # Handle connection error
```

### Permission Issues
```python
try:
    utils.save_data_to_storage(
        data=df,
        output_type="restricted"
    )
except StorageError as e:
    if "AuthorizationFailure" in str(e):
        print("Permission denied")
```

### Debug Mode
```python
utils = FileUtils(
    storage_type="azure",
    connection_string="connection_string",
    log_level="DEBUG"
)
```

For general usage instructions, see the [Usage Guide](USAGE.md).