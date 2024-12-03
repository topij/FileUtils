# Azure Storage Setup Guide

A comprehensive guide for setting up and using Azure Storage with FileUtils.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Azure Storage Setup](#azure-storage-setup)
- [Environment Configuration](#environment-configuration)
- [Basic Usage](#basic-usage)
- [Advanced Features](#advanced-features)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Prerequisites

1. Azure Account and Subscription
2. Azure Storage Account
3. Python 3.8 or later
4. FileUtils basic installation

## Installation

1. Install FileUtils with Azure support:
```bash
pip install FileUtils[azure]
```

2. Or from GitHub:
```bash
pip install "git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[azure]"
```

## Azure Storage Setup

### 1. Create Storage Account

If you don't have an Azure Storage account:
1. Go to Azure Portal
2. Create a new Storage Account
3. Note down the connection string

### 2. Configure Containers

Use the setup utilities:

```python
from FileUtils.azure_setup import AzureSetupUtils

# Create .env file with connection string
AzureSetupUtils.create_env_file(
    connection_string="your_connection_string",
    env_path=".env",
    overwrite=True
)

# Setup default containers
AzureSetupUtils.setup_azure_storage()

# Or specify custom containers
containers = ['my-raw-data', 'my-processed-data']
AzureSetupUtils.setup_azure_storage(container_names=containers)
```

### 3. Verify Setup

```python
# Validate Azure configuration
is_valid = AzureSetupUtils.validate_azure_setup()
print(f"Azure setup is {'valid' if is_valid else 'invalid'}")
```

## Environment Configuration

### 1. Environment Variables

Option 1: Using .env file:
```
# .env
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

Option 2: System environment variables:
```bash
# Linux/macOS
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Windows (PowerShell)
$env:AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Windows (Command Prompt)
set AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

### 2. Configuration File

```yaml
# config.yaml
azure:
  enabled: true
  container_mapping:
    raw: "raw-data"
    processed: "processed-data"
    interim: "interim-data"
    parameters: "parameters"
    configurations: "configurations"
  retry_settings:
    max_retries: 3
    retry_delay: 1
    max_delay: 30
```

## Basic Usage

### Initialize Azure-enabled FileUtils

```python
# Create Azure-enabled instance
file_utils = FileUtils.create_azure_utils()

# Or with explicit connection string
file_utils = FileUtils.create_azure_utils(
    connection_string="your_connection_string"
)
```

### Basic Operations

```python
import pandas as pd

# Create sample data
df = pd.DataFrame({'A': [1, 2, 3]})

# Save to Azure Storage
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="azure_data"
)

# Load from Azure Storage
loaded_df = file_utils.load_single_file(
    "azure://processed-data/azure_data.csv"
)
```

### Multiple Files

```python
# Save multiple DataFrames
data_dict = {
    'current': df1,
    'historical': df2
}

saved_files, _ = file_utils.save_data_to_disk(
    data=data_dict,
    output_filetype="xlsx",
    output_type="processed",
    file_name="multi_sheet_report"
)
```

## Advanced Features

### Custom Container Mapping

```python
# Configure custom container mapping
custom_mapping = {
    "raw": "custom-raw",
    "processed": "custom-processed",
    "interim": "custom-interim"
}

file_utils = FileUtils.create_azure_utils(
    container_mapping=custom_mapping
)
```

### Retry Settings

```python
# Configure in YAML
"""
azure:
  retry_settings:
    max_retries: 5
    retry_delay: 2
    max_delay: 60
"""

# Or in code
from azure.storage.blob import RetryOptions

retry_options = RetryOptions(max_retries=5, retry_delay=2)
```

### Path Management

```python
# Azure paths can be used directly
azure_path = "azure://processed-data/my_data.csv"
df = file_utils.load_single_file(azure_path)

# Or use automatic path resolution
df = file_utils.load_single_file(
    "my_data.csv",
    input_type="processed"
)
```

## Security Considerations

1. Connection String Management:
   - Never commit .env files to version control
   - Use Azure Key Vault in production
   - Rotate connection strings regularly

2. Container Access:
   - Use separate containers for different data types
   - Implement appropriate access controls
   - Use SAS tokens when sharing data

3. Monitoring:
   - Monitor storage access patterns
   - Set up alerts for unusual activity
   - Regularly audit access logs

## Troubleshooting

### Common Issues

1. Authentication Errors:
```python
# Verify connection string
is_valid = AzureSetupUtils.validate_connection_string()

# Check environment variables
import os
print(bool(os.getenv("AZURE_STORAGE_CONNECTION_STRING")))
```

2. Container Issues:
```python
# Verify container existence
is_valid = AzureSetupUtils.validate_azure_setup(
    container_names=['my-container']
)

# Create missing containers
AzureSetupUtils.setup_azure_storage()
```

3. Permission Issues:
```python
# Test container permissions
from azure.storage.blob import BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(conn_str)
containers = blob_service_client.list_containers()
```

### Error Recovery

```python
try:
    df = file_utils.load_single_file("azure://container/missing.csv")
except FileNotFoundError:
    # Fallback to local storage
    df = file_utils.load_single_file(
        "backup.csv",
        input_type="raw"
    )
```

## Best Practices

1. Storage Organization:
   - Use consistent container naming
   - Organize blobs in logical folders
   - Implement clear versioning strategy

2. Performance:
   - Batch operations when possible
   - Use appropriate file formats (Parquet for large data)
   - Implement caching for frequently accessed data

3. Error Handling:
   - Always implement retry logic
   - Have fallback mechanisms
   - Log all storage operations

4. Testing:
   - Test with Azure Storage Emulator
   - Implement integration tests
   - Verify all error scenarios

## Example Workflow

```python
def process_data_with_azure():
    # Initialize Azure setup
    AzureSetupUtils.setup_azure_storage()
    
    # Create Azure-enabled instance
    file_utils = FileUtils.create_azure_utils()
    
    try:
        # Load raw data
        raw_df = file_utils.load_single_file(
            "input.csv",
            input_type="raw"
        )
        
        # Process data
        processed_df = process_data(raw_df)
        
        # Save to Azure
        saved_files, _ = file_utils.save_data_to_disk(
            data=processed_df,
            output_filetype="parquet",
            output_type="processed",
            file_name="processed_data"
        )
        
        return saved_files
        
    except Exception as e:
        logger.error(f"Azure operation failed: {e}")
        # Implement fallback mechanism
        handle_error(e)
```

For general FileUtils usage, refer to [Usage Guide](USAGE.md).