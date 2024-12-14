# Usage Guide

## Basic Usage

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with default configuration
file_utils = FileUtils()

# Load data from different formats
df_csv = file_utils.load_single_file("data.csv", input_type="raw")
df_excel = file_utils.load_single_file("data.xlsx", input_type="raw")
df_parquet = file_utils.load_single_file("data.parquet", input_type="raw")
df_json = file_utils.load_single_file("data.json", input_type="raw")
df_yaml = file_utils.load_single_file("data.yaml", input_type="raw")

# Save data
file_utils.save_data_to_storage(
    data={"Sheet1": df},
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)

# Create new directory in the project structure
features_dir = file_utils.create_directory("features")  # Creates under data/
models_dir = file_utils.create_directory("trained", parent_dir="models")  # Creates under models/
```

## Directory Management

FileUtils manages data in a structured directory layout:
```
project_root/
├── data/
│   ├── raw/          # Raw data files
│   ├── processed/    # Processed data files
│   └── interim/      # Intermediate data files
└── reports/
    └── figures/      # Generated figures
```

You can create new directories within this structure using `create_directory()`:

```python
# Create new directory under data/
features_dir = file_utils.create_directory("features")

# Create directory under specific parent
reports_dir = file_utils.create_directory("monthly", parent_dir="reports")

# Directory is added to configuration structure
print(file_utils.config["directory_structure"]["data"])  # Shows ['raw', 'processed', 'interim', 'features']
```

## Configuration

You can override default settings using a `config.yaml` file:

```yaml
csv_delimiter: ","
encoding: "utf-8"
quoting: "minimal"
include_timestamp: false
logging_level: "INFO"
directory_structure:
  data:
    - raw
    - processed
    - interim
  reports:
    - figures
```

## Azure Storage

For Azure Blob Storage operations, see [AZURE_SETUP.md](AZURE_SETUP.md).

## Error Handling

FileUtils provides detailed error messages through custom exceptions:
- `StorageError`: Base exception for storage operations
- `StorageOperationError`: Specific operation failures
- `ConfigurationError`: Configuration-related issues

## Logging

Logging is configurable through the config file:
```yaml
logging_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```