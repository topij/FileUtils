# FileUtils Usage Guide

A comprehensive guide for using FileUtils in data science projects.

## Basic Usage

### Initialization and Storage Selection

```python
from FileUtils import FileUtils, OutputFileType, StorageType

# Local storage (default)
file_utils = FileUtils(
    project_root="/path/to/project",
    config_file="config.yaml"
)

# Azure storage
azure_utils = FileUtils(
    project_root="/path/to/project",
    storage_type=StorageType.AZURE,
    connection_string="your_connection_string"
)
```

### Basic File Operations

```python
import pandas as pd

# Create sample data
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Charlie'],
    'age': [25, 30, 35]
})

# Save data
saved_files, _ = file_utils.save_data_to_storage(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="sample_data"
)

# Load data
loaded_df = file_utils.load_single_file(
    "sample_data.csv",
    input_type="processed"
)
```

## Configuration

### YAML Configuration

```yaml
# config.yaml
csv_delimiter: ","
encoding: "utf-8"
quoting: 0  # csv.QUOTE_MINIMAL
include_timestamp: true
logging_level: "INFO"

# Storage settings
storage:
  default_type: "local"  # or "azure"
  azure:
    enabled: true
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
      interim: "interim-data"
    retry_settings:
      max_retries: 3
      retry_delay: 1

# Directory structure
directory_structure:
  data:
    - raw
    - interim
    - processed
    - external
  reports:
    - figures
    - outputs
    - tables
  models:
    - trained
    - evaluations

# Logging settings
logging:
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  file_logging: false
  log_directory: "logs"
```

### Environment Variables

```bash
# Azure credentials
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Optional configuration
export FILEUTILS_LOG_LEVEL="DEBUG"
export FILEUTILS_CONFIG_PATH="/path/to/config.yaml"
```

## Advanced Usage

### Working with Multiple Formats

```python
# Save in different formats
formats = {
    OutputFileType.CSV: "csv_data",
    OutputFileType.XLSX: "excel_data",
    OutputFileType.PARQUET: "parquet_data"
}

for format_type, filename in formats.items():
    saved_files, _ = file_utils.save_data_to_storage(
        data=df,
        output_filetype=format_type,
        output_type="processed",
        file_name=filename
    )
```

### Multiple DataFrames

```python
# Save multiple sheets to Excel
data_dict = {
    'raw_data': df1,
    'processed': df2,
    'summary': df3
}

saved_files, _ = file_utils.save_data_to_storage(
    data=data_dict,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_report"
)

# Load all sheets
sheets = file_utils.load_excel_sheets(
    "multi_sheet_report.xlsx",
    input_type="processed"
)
```

### Error Handling

```python
from FileUtils.core.base import StorageError, StorageConnectionError

try:
    file_utils.save_data_to_storage(
        data=df,
        output_filetype=OutputFileType.PARQUET,
        output_type="processed",
        file_name="data"
    )
except StorageConnectionError as e:
    print(f"Connection failed: {e}")
    # Handle connection error
except StorageError as e:
    print(f"Storage operation failed: {e}")
    # Handle general storage error
```

## Best Practices

### Project Organization

1. Use consistent directory structure:
```python
file_utils = FileUtils(project_root="project_root")
```

2. Maintain data lineage:
```python
# Raw data
saved_files, _ = file_utils.save_data_to_storage(
    data=raw_df,
    output_type="raw",
    file_name="original_data"
)

# Processed data
processed_df = process_data(raw_df)
saved_files, _ = file_utils.save_data_to_storage(
    data=processed_df,
    output_type="processed",
    file_name="processed_data"
)
```

### Performance Tips

1. Use appropriate formats:
   - Parquet for large datasets
   - CSV for simple tabular data
   - Excel for human-readable reports

2. Batch operations when possible:
```python
# Better
file_utils.save_data_to_storage(
    data={'month1': df1, 'month2': df2},
    output_filetype=OutputFileType.XLSX
)

# Avoid multiple single saves
# for df in dataframes:
#     file_utils.save_data_to_storage(data=df, ...)
```

## Troubleshooting

### Common Issues

1. Storage Connection Issues:
```python
# Check storage type
print(file_utils.storage.__class__.__name__)

# Verify Azure connection
if isinstance(file_utils.storage, AzureStorage):
    print("Azure Storage configured")
```

2. File Not Found:
```python
# Check file path resolution
try:
    df = file_utils.load_single_file("missing.csv")
except FileNotFoundError as e:
    print(f"File path attempted: {e}")
    # Handle missing file
```

3. Configuration Issues:
```python
# Print effective configuration
print(file_utils.config)

# Verify directory structure
for dir_type, paths in file_utils.config["directory_structure"].items():
    print(f"{dir_type}:")
    for path in paths:
        full_path = file_utils.project_root / dir_type / path
        print(f"  {path}: {'exists' if full_path.exists() else 'missing'}")
```

### Debug Mode

```python
import logging

# Enable debug logging
file_utils = FileUtils(log_level="DEBUG")

# Or update existing instance
file_utils.logger.setLevel(logging.DEBUG)
```

### Common Error Messages

1. "Storage type not supported":
   - Verify storage_type parameter
   - Check optional dependencies installation

2. "Configuration validation failed":
   - Check config.yaml format
   - Verify all required fields are present

3. "Unable to determine file type":
   - Specify output_filetype explicitly
   - Check file extension matching

For Azure-specific setup and troubleshooting, see [Azure Setup Guide](AZURE_SETUP.md).