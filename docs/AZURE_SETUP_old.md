# Azure Storage Setup Guide

This guide explains how to set up and use Azure Storage capabilities with FileUtils.

## Prerequisites

1. Azure Storage Account
2. Azure Storage Connection String
3. Python 3.8 or later

## Installation

Install FileUtils with Azure support:

```bash
pip install FileUtils[azure]
```

## Environment Setup

There are several ways to configure your Azure Storage connection string:

### 1. Using a .env File (Recommended)

Create a .env file with your connection string:

```python
from FileUtils.azure_setup import AzureSetupUtils

# Create/update .env file
AzureSetupUtils.create_env_file(
    connection_string="your_connection_string",
    env_path=".env",  # Optional, defaults to current directory
    overwrite=True    # Optional, defaults to False
)
```

Or manually create a .env file:
```
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

### 2. Using Environment Variables

```bash
# Linux/macOS
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Windows (Command Prompt)
set AZURE_STORAGE_CONNECTION_STRING=your_connection_string

# Windows (PowerShell)
$env:AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

### 3. Container Setup

Create required containers using AzureSetupUtils:

```python
from FileUtils.azure_setup import AzureSetupUtils

# Setup with default containers using .env file
AzureSetupUtils.setup_azure_storage()

# Or specify custom containers and env file location
containers = ['my-raw-data', 'my-processed-data']
AzureSetupUtils.setup_azure_storage(
    container_names=containers,
    env_path=".env"  # Optional
)
```

### 4. Validate Setup

```python
is_valid = AzureSetupUtils.validate_azure_setup(env_path=".env")
print(f"Azure setup is {'valid' if is_valid else 'invalid'}")
```

## Configuration

Create a `config.yaml` file with Azure settings:

```yaml
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
```

## Usage

```python
from FileUtils import FileUtils
import pandas as pd

# Create Azure-enabled instance (will automatically load .env)
file_utils = FileUtils.create_azure_utils()

# Save DataFrame to Azure Storage
df = pd.DataFrame({'A': [1, 2, 3]})
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="my_data"
)

# Load from Azure Storage
df = file_utils.load_single_file("azure://processed-data/my_data.csv")
```

## Environment File (.env) Best Practices

1. Never commit .env files to version control
2. Add .env to your .gitignore file
3. Provide a .env.example template without sensitive values
4. Use different .env files for different environments (e.g., .env.development, .env.production)
5. Regularly rotate connection strings in production

## Troubleshooting

1. Connection String Issues:
   - Check if .env file exists and is properly formatted
   - Use `AzureSetupUtils.validate_connection_string()` to verify
   - Ensure .env file is in the correct location

2. Container Access Issues:
   - Verify container existence with `AzureSetupUtils.validate_azure_setup()`
   - Check container permissions in Azure Portal

3. Common Error Messages:
   - "No .env file found": Create .env file or specify path
   - "Container does not exist": Run setup utilities again
   - "Authentication failed": Check connection string
   - "Blob not found": Verify file path format

## Security Considerations

1. Never commit .env files or connection strings to version control
2. Use Azure Key Vault for production deployments
3. Implement appropriate access controls on containers
4. Monitor storage access patterns
5. Regularly rotate connection strings and update .env files

## Additional Resources

- [Azure Blob Storage Documentation](https://docs.microsoft.com/azure/storage/blobs/)
- [Azure Storage Security Guide](https://docs.microsoft.com/azure/storage/common/storage-security-guide)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)