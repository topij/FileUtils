# FileUtils Usage Guide

## Basic Usage

### Initialization

```python
from FileUtils import FileUtils

# Local storage (default)
utils = FileUtils()

# Azure storage
azure_utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)

# With custom configuration
utils = FileUtils(
    project_root="/path/to/project",
    config_file="config.yaml",
    log_level="INFO"
)
```

### File Operations

#### Single DataFrame
```python
import pandas as pd

# Save DataFrame
df = pd.DataFrame({'A': [1, 2, 3]})
saved_files, metadata = utils.save_data_to_storage(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="data"
)

# Load DataFrame
loaded_df = utils.load_single_file(
    "data.csv",
    input_type="processed"
)
```

#### Multiple DataFrames
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
    file_name="multi_sheet_report"
)

# Load all sheets
sheets = utils.load_excel_sheets(
    "multi_sheet_report.xlsx",
    input_type="processed"
)
```

## Advanced Features

### Metadata Tracking

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

### File Formats

```python
# CSV with automatic delimiter inference
utils.save_data_to_storage(
    data=df,
    output_filetype="csv"
)

# Parquet for large datasets
utils.save_data_to_storage(
    data=df,
    output_filetype="parquet"
)

# Excel with multiple sheets
utils.save_data_to_storage(
    data=data_dict,
    output_filetype="xlsx"
)
```

### Directory Management

```python
# Get path for data type
raw_path = utils.get_data_path("raw")
processed_path = utils.get_data_path("processed")

# Custom directory structure in config.yaml
directory_structure:
  data:
    - raw
    - interim
    - processed
    - external
  reports:
    - figures
    - outputs
  models:
    - trained
```

## Configuration

### YAML Configuration

```yaml
# config.yaml
csv_delimiter: ","
encoding: "utf-8"
include_timestamp: true
logging_level: "INFO"

storage:
  default_type: "local"
  azure:
    enabled: false
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
    retry_settings:
      max_retries: 3
      retry_delay: 1

directory_structure:
  data:
    - raw
    - interim
    - processed
  reports:
    - figures
    - outputs
```

### Environment Variables

```bash
# Storage settings
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Logging
export FILEUTILS_LOG_LEVEL="DEBUG"
```

## Error Handling

### Basic Error Handling
```python
from FileUtils.core.base import StorageError

try:
    utils.save_data_to_storage(
        data=df,
        output_filetype="csv",
        file_name="data"
    )
except StorageError as e:
    print(f"Storage error: {e}")
```

### Specific Errors
```python
from FileUtils.core.base import StorageConnectionError, StorageOperationError

try:
    # Connection errors
    utils = FileUtils(
        storage_type="azure",
        connection_string="invalid"
    )
except StorageConnectionError as e:
    print(f"Connection failed: {e}")

try:
    # Operation errors
    utils.load_single_file("nonexistent.csv")
except StorageOperationError as e:
    print(f"Operation failed: {e}")
```

## Best Practices

### Project Organization

```python
# Use consistent directory structure
utils = FileUtils(project_root="project_root")

# Maintain data lineage
saved_files, _ = utils.save_data_to_storage(
    data=raw_df,
    output_type="raw",
    file_name="original"
)

processed_df = process_data(raw_df)
saved_files, _ = utils.save_data_to_storage(
    data=processed_df,
    output_type="processed",
    file_name="processed"
)
```

### Performance Tips

1. Format Selection:
   - Use Parquet for large datasets
   - Use CSV for simple, readable data
   - Use Excel for human-readable reports

2. Batch Operations:
```python
# Efficient
utils.save_data_to_storage(
    data={'month1': df1, 'month2': df2},
    output_filetype="parquet"
)

# Less efficient
# for df in dataframes:
#     utils.save_data_to_storage(data=df, ...)
```

3. Memory Management:
```python
# Process large files in chunks
for chunk in pd.read_csv("large_file.csv", chunksize=10000):
    processed = process_chunk(chunk)
    utils.save_data_to_storage(
        data=processed,
        output_type="processed"
    )
```

## Debug and Testing

### Debug Mode
```python
# Enable debug logging
utils = FileUtils(log_level="DEBUG")

# Or update existing instance
utils.logger.setLevel("DEBUG")
```

### Testing Setup
```python
# Create test data directory
test_utils = FileUtils(project_root="test_dir")

# Clean up after tests
import shutil
shutil.rmtree("test_dir")
```

For Azure-specific setup and configuration, see [Azure Setup Guide](AZURE_SETUP.md).