# FileUtils

FileUtils is a Python utility class for handling file operations in data science projects. It provides robust methods for loading, saving, and managing data files in various formats, along with project directory structure management and cloud storage support.

## Features

- Support for multiple file formats:
  - CSV (with delimiter inference)
  - Excel (single and multi-sheet)
  - Parquet
  - JSON
  - YAML
- Cloud storage support:
  - Azure Blob Storage integration
  - Transparent fallback to local storage
  - Cloud path handling ("azure://container/path")
- Automated project structure management
- Configurable settings via YAML
- Comprehensive logging
- Timestamp-based file versioning
- Error handling and validation

## Installation

1. Ensure you have Python 3.8 or later installed.

2. Basic installation with local storage support:
```bash
pip install pandas pyyaml xlsxwriter openpyxl pyarrow fastparquet jsonschema
```

3. For Azure support, install additional dependencies:
```bash
pip install azure-storage-blob azure-identity
```

## Basic Usage

### Local Storage

```python
from file_utils import FileUtils, OutputFileType

# Initialize FileUtils
file_utils = FileUtils()  # Automatically detects project root
# Or with specific paths:
# file_utils = FileUtils(project_root="path/to/project", config_file="path/to/config.yaml")

# Load data
df = file_utils.load_single_file("data.csv", input_type="raw")
yaml_data = file_utils.load_yaml("config.yaml", input_type="raw")
json_data = file_utils.load_json("data.json", input_type="raw")

# Save data
file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="output_data"
)

# Save multiple DataFrames to Excel
dfs = {"sheet1": df1, "sheet2": df2}
file_utils.save_data_to_disk(
    data=dfs,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_output"
)
```

### Azure Storage

```python
# Create Azure-enabled instance
azure_utils = FileUtils.create_azure_utils(
    connection_string="your_azure_connection_string"
)

# Save to Azure Blob Storage
saved_files, _ = azure_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="my_data"
)

# Load from Azure Storage
df = azure_utils.load_single_file("azure://processed-data/my_data.csv")

# Save multiple sheets to Excel in Azure
excel_data = {
    'original': df1,
    'processed': df2
}
excel_files, _ = azure_utils.save_data_to_disk(
    data=excel_data,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_report"
)
```

## Configuration

FileUtils uses a YAML configuration file. Default location is `config.yaml` in the project root.

Example configuration:
```yaml
# Basic settings
csv_delimiter: ","
encoding: "utf-8"
quoting: 0  # csv.QUOTE_MINIMAL
include_timestamp: true
logging_level: "INFO"
disable_logging: false

# Directory structure
directory_structure:
  data:
    - raw
    - interim
    - processed
  reports:
    - figures
    - outputs
  models: []
  src: []

# File format settings
parquet_compression: "snappy"

# Azure Storage settings (optional)
azure:
  enabled: false  # Set to true to enable Azure storage
  container_mapping:
    raw: "raw-data"
    processed: "processed-data"
    interim: "interim-data"
    parameters: "parameters"
    configurations: "configurations"
  retry_settings:
    max_retries: 3
    retry_delay: 1
  connection_string: ""  # Set via environment variable
```

## Directory Structure

FileUtils manages the following directory structure by default:
```
project_root/
├── data/
│   ├── raw/         # Original data
│   ├── interim/     # Intermediate processing
│   └── processed/   # Final processed data
├── reports/
│   ├── figures/     # Generated graphics
│   └── outputs/     # Analysis outputs
├── models/          # Trained models
└── src/            # Source code
```

## API Reference

### Storage Initialization
- `FileUtils()`: Create standard FileUtils instance
- `FileUtils.create_azure_utils(connection_string, project_root=None)`: Create Azure-enabled instance

### Loading Data
- `load_single_file(file_path, input_type="raw")`: Load any supported file format
- `load_yaml(file_path, input_type="raw")`: Load YAML file
- `load_json(file_path, input_type="raw")`: Load JSON file
- `load_excel_sheets(file_path, input_type="raw")`: Load all Excel sheets
- `load_multiple_files(file_paths, input_type="raw")`: Load multiple files

### Saving Data
- `save_data_to_disk(data, output_filetype, output_type="processed")`: Save data in any format
- `save_yaml(data, file_path, output_type="processed")`: Save YAML file
- `save_json(data, file_path, output_type="processed")`: Save JSON file
- `save_dataframes_to_excel(dataframes_dict, file_name, output_type="reports")`: Save multiple DataFrames to Excel

### Utility Methods
- `get_data_path(data_type="raw")`: Get path for specific data type
- `get_logger(name)`: Get configured logger instance
- `setup_directory_structure()`: Create project directory structure

## Azure Storage Features

### Container Mapping
Default container mapping for different data types:
```python
container_mapping = {
    "raw": "raw-data",
    "processed": "processed-data",
    "interim": "interim-data",
    "parameters": "parameters",
    "configurations": "configurations"
}
```

### Azure Path Format
Azure storage paths use the format: `azure://container-name/blob-name`
Example: `azure://processed-data/my_data.csv`

### Error Handling and Fallback
- Automatic fallback to local storage if Azure operations fail
- Comprehensive error logging
- Retry mechanism for transient failures

## Error Handling

FileUtils includes comprehensive error handling:
- File existence validation
- Format validation
- Schema validation for configuration
- Azure connectivity validation
- Proper exception handling with logging

## Command Line Interface

```bash
# Set up project structure
python -m file_utils setup --project-root /path/to/project

# Test logging
python -m file_utils test-logging
```

## Testing

Run the test suite:
```bash
python -m unittest test_file_utils.py
```

The test suite includes tests for:
- Local file operations
- Azure storage operations
- Configuration handling
- Error scenarios
- Azure connectivity and fallback behavior
- Directory structure management

## License

This project is open-source and available under the MIT License.