# FileUtils Usage Guide

This guide covers the core functionality and common use cases for FileUtils.

## Table of Contents
- [Basic Usage](#basic-usage)
- [Working with Different File Formats](#working-with-different-file-formats)
- [Multiple DataFrame Operations](#multiple-dataframe-operations)
- [Directory Management](#directory-management)
- [Configuration Options](#configuration-options)
- [Logging and Error Handling](#logging-and-error-handling)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

## Basic Usage

### Initialization

```python
from FileUtils import FileUtils, OutputFileType

# Basic initialization
file_utils = FileUtils()

# With specific project root
file_utils = FileUtils(project_root="/path/to/project")

# With custom configuration
file_utils = FileUtils(
    project_root="/path/to/project",
    config_file="config.yaml"
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
saved_files, _ = file_utils.save_data_to_disk(
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

## Working with Different File Formats

### CSV Files

```python
# Save as CSV with timestamp
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="data_with_timestamp",
    include_timestamp=True
)

# Save without timestamp
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="data_no_timestamp",
    include_timestamp=False
)
```

### Excel Files

```python
# Save single DataFrame to Excel
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="excel_data"
)

# Load Excel file
df = file_utils.load_single_file(
    "excel_data.xlsx",
    input_type="processed"
)
```

### Parquet Files

```python
# Save as Parquet
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.PARQUET,
    output_type="processed",
    file_name="parquet_data"
)

# Load Parquet file
df = file_utils.load_single_file(
    "parquet_data.parquet",
    input_type="processed"
)
```

## Multiple DataFrame Operations

### Multiple Sheets in Excel

```python
# Create multiple DataFrames
data_dict = {
    'raw_data': df1,
    'processed_data': df2,
    'summary': df3
}

# Save to Excel with multiple sheets
saved_files, _ = file_utils.save_data_to_disk(
    data=data_dict,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_report"
)

# Load all sheets
sheets_dict = file_utils.load_excel_sheets(
    "multi_sheet_report.xlsx",
    input_type="processed"
)
```

### Working with Multiple CSV Files

```python
# Save multiple CSVs with metadata
data_dict = {
    'sales': sales_df,
    'customers': customers_df,
    'products': products_df
}

saved_files, metadata_path = file_utils.save_data_to_disk(
    data=data_dict,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="dataset"
)

# Load CSVs using metadata
dataframes = file_utils.load_csvs_from_metadata(
    metadata_path,
    input_type="processed"
)
```

## Directory Management

### Custom Directory Structure

```python
# Create custom directory structure
custom_structure = {
    'data': ['raw', 'interim', 'processed', 'external'],
    'reports': ['figures', 'tables', 'presentations'],
    'models': ['trained', 'evaluations'],
    'documentation': ['specs', 'api']
}

# Configure in YAML
"""
# config.yaml
directory_structure:
  data:
    - raw
    - interim
    - processed
    - external
  reports:
    - figures
    - tables
    - presentations
  models:
    - trained
    - evaluations
  documentation:
    - specs
    - api
"""

# Initialize with custom structure
file_utils = FileUtils(config_file="config.yaml")
```

## Configuration Options

### Basic Configuration

```yaml
# config.yaml
csv_delimiter: ","
encoding: "utf-8"
include_timestamp: true
logging_level: "INFO"
```

### Advanced Configuration

```yaml
# Advanced config.yaml
parquet_compression: "snappy"
excel_engine: "openpyxl"

logging:
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  file_logging: true
  log_directory: "logs"

error_handling:
  raise_on_missing_file: true
  strict_type_checking: true
  auto_create_directories: true
```

## Logging and Error Handling

### Configuring Logging

```python
# Initialize with specific log level
file_utils = FileUtils(log_level="DEBUG")

# Get logger for specific module
logger = file_utils.get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
```

### Error Handling

```python
# Handle missing files
try:
    df = file_utils.load_single_file("nonexistent.csv")
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")

# Handle invalid formats
try:
    file_utils.save_data_to_disk(
        data=df,
        output_filetype="invalid"
    )
except ValueError as e:
    logger.error(f"Invalid file type: {e}")
```

## Best Practices

1. Directory Organization:
   - Use `raw` for original, immutable data
   - Use `interim` for intermediate processing steps
   - Use `processed` for final, cleaned data

2. File Naming:
   - Use lowercase with underscores
   - Include timestamps for versioning
   - Use descriptive names

3. Error Handling:
   - Always wrap file operations in try-except blocks
   - Log errors appropriately
   - Provide meaningful error messages

4. Configuration:
   - Use separate configs for different environments
   - Version control your configs
   - Document configuration changes

## Common Patterns

### Data Pipeline Pattern

```python
def process_data_pipeline():
    # Load raw data
    raw_df = file_utils.load_single_file(
        "raw_data.csv",
        input_type="raw"
    )
    
    # Process data
    interim_df = process_step_1(raw_df)
    file_utils.save_data_to_disk(
        data=interim_df,
        output_type="interim",
        file_name="step_1_output"
    )
    
    final_df = process_step_2(interim_df)
    file_utils.save_data_to_disk(
        data=final_df,
        output_type="processed",
        file_name="final_output"
    )
```

### Batch Processing Pattern

```python
def batch_process_files():
    # Load multiple files
    files = ["data1.csv", "data2.csv", "data3.csv"]
    dataframes = []
    
    for file in files:
        df = file_utils.load_single_file(
            file,
            input_type="raw"
        )
        processed_df = process_data(df)
        dataframes.append(processed_df)
    
    # Save combined results
    combined_df = pd.concat(dataframes)
    file_utils.save_data_to_disk(
        data=combined_df,
        output_type="processed",
        file_name="combined_output"
    )
```

For Azure-specific usage, please refer to [Azure Setup Guide](AZURE_SETUP.md).