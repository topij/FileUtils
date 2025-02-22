# FileUtils

A Python utility package for consistent file operations across local and Azure storage, with enhanced support for various data formats and flexible configuration options.

## Features

- **Unified Storage Interface**
  - Seamless operations across local and Azure Blob Storage
  - Consistent API regardless of storage backend
  - Automatic directory structure management

- **Comprehensive File Format Support**
  - CSV (with delimiter auto-detection)
  - Excel (.xlsx, .xls) with multi-sheet support
  - Parquet (with compression options)
  - JSON (records and index formats)
  - YAML (with customizable formatting)

- **Advanced Data Handling**
  - Single and multi-DataFrame operations
  - Automatic format detection
  - Flexible data orientation options
  - Customizable save/load options per format

- **Robust Infrastructure**
  - YAML-based configuration system
  - Comprehensive error handling
  - Detailed logging with configurable levels
  - Type hints throughout the codebase

## Quick Start

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with local storage
file_utils = FileUtils()

# Load data (format is auto-detected)
df = file_utils.load_single_file("data.csv", input_type="raw")

# Save as JSON with custom options
file_utils.save_data_to_storage(
    data=df,
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.JSON,
    orient="records",  # Save as list of records
)

# Save multiple DataFrames to Excel
data_dict = {
    "Sheet1": df1,
    "Sheet2": df2
}
file_utils.save_data_to_storage(
    data=data_dict,
    file_name="multi_sheet",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)
```

## Key Benefits

- **Consistency**: Same interface for local and cloud storage operations
- **Flexibility**: Extensive options for each file format
- **Reliability**: Robust error handling and logging
- **Simplicity**: Intuitive API with sensible defaults

## Background

This package was developed to streamline data operations across various projects, particularly in data science and analysis workflows. It eliminates the need to rewrite common file handling code and provides a consistent interface regardless of the storage backend.

For a practical example, check out my [semantic text analyzer](https://www.github.com/topij/text-analyzer) project, which uses FileUtils for seamless data handling across local and Azure environments.

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Usage Guide](docs/USAGE.md) - Comprehensive examples and API documentation
- [Azure Setup Guide](docs/AZURE_SETUP.md) - Azure Blob Storage configuration
- [Development Guide](docs/DEVELOPMENT.md) - Setup, building, and contributing to the project

## Requirements

- Python 3.9+
- Core dependencies:
  - pandas
  - pyyaml
  - azure-storage-blob (for Azure support)
  - openpyxl (for Excel support)
  - pyarrow (for Parquet support)

## Notes from the Author

This package prioritizes functionality and ease of use over performance optimization. While I use it in all of my projects, it's maintained as a side project. 

## License

MIT License