# Azure Setup Guide

## Prerequisites

1. Azure subscription
2. Azure Storage account
3. Azure Blob Storage container
4. Required Python packages:
   - azure-storage-blob
   - azure-identity

## Authentication

1. Using Connection String:
```python
from FileUtils import FileUtils

# Initialize with Azure storage
file_utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)
```

2. Using Environment Variables:
```bash
# Set in .env file or environment
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

## Usage with Azure Storage

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with Azure storage
file_utils = FileUtils(storage_type="azure")

# Load from Azure (using azure:// URL)
df = file_utils.load_single_file("azure://container-name/path/to/file.xlsx")

# Save to Azure
file_utils.save_data_to_storage(
    data={"Sheet1": df},
    file_name="azure://container-name/path/to/output",
    output_filetype=OutputFileType.XLSX
)
```

## Supported Operations

Azure storage supports all the same file formats as local storage:
- CSV (.csv)
- Excel (.xlsx, .xls)
- Parquet (.parquet)
- JSON (.json)
- YAML (.yaml)

## Configuration

Azure-specific configuration in config.yaml:
```yaml
azure:
  default_container: "your-container-name"
  connection_timeout: 300
  max_retries: 3
```

## Error Handling

Azure operations include specific error handling for:
- Connection issues
- Authentication failures
- Container/blob not found
- Permission errors

## Retry Settings

```yaml
storage:
  azure:
    retry_settings:
      max_retries: 3
      retry_delay: 1
      max_delay: 30
```

## Security Best Practices

### Connection String Management

```python
# Use environment variables
import os
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Or use dotenv file
from dotenv import load_dotenv
load_dotenv()
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
```

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