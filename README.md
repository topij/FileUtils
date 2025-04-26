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

## Installation

Choose the installation option that best suits your needs:

```bash
# Basic installation (local storage only)
pip install FileUtils

# Install with Azure support
pip install 'FileUtils[azure]'

# Install with Parquet support
pip install 'FileUtils[parquet]'

# Install with Excel support
pip install 'FileUtils[excel]'

# Install with all optional dependencies
pip install 'FileUtils[all]'
```

You can also install directly from GitHub:
```bash
# Basic installation
pip install git+https://github.com/topij/FileUtils.git

# With specific features
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]'
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]'
```

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

- [Getting Started Guide](docs/GETTING_STARTED_GUIDE.md) - Quick introduction to key use cases
- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - Comprehensive examples and patterns
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Azure Setup Guide](docs/AZURE_SETUP.md) - Azure Blob Storage configuration
- [Development Guide](docs/DEVELOPMENT.md) - Setup, building, and contributing to the project

## Requirements

### Core Dependencies (automatically installed)
- Python 3.9+
- pandas
- pyyaml
- python-dotenv
- jsonschema

### Optional Dependencies
Choose the dependencies you need based on your use case:

- **Azure Storage** (`[azure]`):
  - azure-storage-blob
  - azure-identity
- **Parquet Support** (`[parquet]`):
  - pyarrow
- **Excel Support** (`[excel]`):
  - openpyxl

Install optional dependencies using the corresponding extras tag (e.g., `pip install 'FileUtils[azure]'`).

## Notes from the Author

This package prioritizes functionality and ease of use over performance optimization. While I use it in all of my projects, it's maintained as a side project. 

## License

MIT License