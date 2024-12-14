# FileUtils

A Python utility package for consistent file operations across local and Azure storage.

## Features

- Unified interface for both local and Azure Blob Storage operations
- Automatic directory structure management
- Support for multiple file formats:
  - CSV
  - Excel (.xlsx, .xls)
  - Parquet
  - JSON
  - YAML
- Configurable file operations with YAML configuration
- Type hints and comprehensive error handling
- Logging system with configurable levels
- Azure Blob Storage integration

## Installation

See [INSTALLATION.md](docs/INSTALLATION.md) for detailed installation instructions.

## Usage

See [USAGE.md](docs/USAGE.md) for usage examples and API documentation.

For Azure Blob Storage setup and configuration, see [AZURE_SETUP.md](docs/AZURE_SETUP.md).

## Quick Start

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with local storage
file_utils = FileUtils()

# Load DataFrame from various formats
df_csv = file_utils.load_single_file("data.csv", input_type="raw")
df_excel = file_utils.load_single_file("data.xlsx", input_type="raw")
df_parquet = file_utils.load_single_file("data.parquet", input_type="raw")
df_json = file_utils.load_single_file("data.json", input_type="raw")
df_yaml = file_utils.load_single_file("data.yaml", input_type="raw")

# Save DataFrame
file_utils.save_data_to_storage(
    data={"Sheet1": df},
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)
```

## Requirements

- Python 3.9+
- Dependencies listed in pyproject.toml/environment.yaml

## License

MIT License