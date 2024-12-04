# FileUtils

FileUtils is a Python utility package for managing data files in data science projects. It provides robust file operations with local and cloud storage support, focusing on reproducibility and ease of use.

## Key Features

- **Multiple Storage Backends**: 
  - Local filesystem storage
  - Azure Blob Storage support
  - Extensible storage abstraction for future backends
- **Multiple Format Support**: CSV, Excel, Parquet, JSON, YAML
- **Project Structure Management**: Automated directory creation and management
- **Flexible Configuration**: YAML-based configuration with sensible defaults
- **Type Safety**: Full type hinting and validation
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Error Handling**: Robust error handling with informative messages

## Quick Start

```python
from FileUtils import FileUtils
import pandas as pd

# Local storage
file_utils = FileUtils()

# Or with Azure storage
azure_utils = FileUtils(storage_type="azure", connection_string="your_connection_string")

# Save DataFrame
df = pd.DataFrame({'A': [1, 2, 3]})
saved_files, _ = file_utils.save_data_to_storage(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="my_data"
)

# Load data
loaded_df = file_utils.load_single_file("my_data.csv", input_type="processed")
```

## Installation

Install directly from GitHub:
```bash
# Basic installation
pip install "git+https://github.com/topij/FileUtils.git"

# With Azure support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]"

# With all optional features (Azure, Parquet, Excel)
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]"
```

For detailed installation instructions, see [Installation Guide](docs/INSTALLATION.md).

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - Core functionality and common use cases
- [Azure Setup](docs/AZURE_SETUP.md) - Azure storage setup and usage

## Basic Example

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with custom configuration
file_utils = FileUtils(
    project_root="/path/to/project",
    config_file="config.yaml",
    storage_type="local"  # or "azure"
)

# Save multiple DataFrames to Excel
data_dict = {
    'sheet1': df1,
    'sheet2': df2
}

saved_files, _ = file_utils.save_data_to_storage(
    data=data_dict,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_report"
)
```

## Project Structure

FileUtils manages the following directory structure by default:
```
project_root/
├── data/
│   ├── raw/         # Original data
│   ├── interim/     # Intermediate processing
│   ├── processed/   # Final processed data
│   └── configurations/  # Configuration files
├── reports/
│   ├── figures/     # Generated graphics
│   └── outputs/     # Analysis outputs
├── models/          # Trained models
└── src/            # Source code
```

## Requirements

- Python 3.8 or later
- Core dependencies: pandas, PyYAML, python-dotenv, jsonschema
- Optional: azure-storage-blob, pyarrow, openpyxl

## License

This project is licensed under the MIT License.