# FileUtils

FileUtils is a Python utility package for managing data files in data science projects. It provides robust file operations with local and cloud storage support, focusing on reproducibility and ease of use.

## Key Features

- **Multiple Format Support**: CSV, Excel, Parquet, JSON, YAML
- **Azure Storage Integration**: Seamless cloud storage operations
- **Project Structure Management**: Automated directory creation and management
- **Flexible Configuration**: YAML-based configuration with sensible defaults
- **Type Safety**: Full type hinting and validation
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Error Handling**: Robust error handling with informative messages
- **Azure Blob Storage**: Direct integration with Azure Storage

## Quick Start

```python
from FileUtils import FileUtils
import pandas as pd

# Initialize
file_utils = FileUtils()

# Save DataFrame
df = pd.DataFrame({'A': [1, 2, 3]})
saved_files, _ = file_utils.save_data_to_disk(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="my_data"
)

# Load data
loaded_df = file_utils.load_single_file("my_data.csv", input_type="processed")
```

## Installation

There are two ways to install FileUtils:

### 1. Install as a Package Using pip

Install directly from GitHub:
```bash
# Basic installation
pip install "git+ssh://git@github.com/topij/FileUtils.git"

# With Azure support
pip install "git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[azure]"

# With all optional features (Azure, Parquet, Excel)
pip install "git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[all]"
```

Add to your project's requirements.txt:
```
git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[azure,parquet,excel]
```

### 2. Clone and Install Locally

Clone the repository and install in development mode:
```bash
# Clone the repository
git clone git@github.com:topij/FileUtils.git
cd FileUtils

# Install in development mode
pip install -e ".[all]"  # All features
# or
pip install -e ".[azure]"  # Azure support only
```

### Dependencies

Core dependencies (installed automatically):
- pandas >= 1.3.0
- pyyaml >= 5.4.1
- python-dotenv >= 0.19.0
- jsonschema >= 3.2.0

Optional dependencies:
- Azure Storage: azure-storage-blob, azure-identity
- Parquet support: pyarrow
- Excel support: openpyxl

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Getting Started](docs/GETTING_STARTED.md) - Comprehensive getting started guide
- [Usage Guide](docs/USAGE.md) - Core functionality and common use cases
- [Azure Setup](docs/AZURE_SETUP.md) - Azure storage setup and usage
- [Contributing](docs/CONTRIBUTING.md) - Guidelines for contributors
- [Development](docs/DEVELOPMENT.md) - Development setup and testing

## Basic Example

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with custom configuration
file_utils = FileUtils(
    project_root="/path/to/project",
    config_file="config.yaml"
)

# Save multiple DataFrames to Excel
data_dict = {
    'sheet1': df1,
    'sheet2': df2
}

saved_files, _ = file_utils.save_data_to_disk(
    data=data_dict,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_report"
)
```

## Azure Storage Example

```python
# Initialize Azure setup
from FileUtils.azure_setup import AzureSetupUtils
AzureSetupUtils.setup_azure_storage()

# Create Azure-enabled instance
azure_utils = FileUtils.create_azure_utils()

# Save to Azure Storage
saved_files, _ = azure_utils.save_data_to_disk(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="cloud_data"
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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<!-- ## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](docs/CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## Development

For development setup and guidelines, see our [Development Guide](docs/DEVELOPMENT.md). -->