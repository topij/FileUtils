# FileUtils

FileUtils is a Python utility package for managing data files in data science projects. It provides robust file operations with local and cloud storage support, focusing on reproducibility and ease of use.

## Key Features

- **Multiple Storage Backends**: 
  - Local filesystem storage
  - Azure Blob Storage support
  - Extensible storage abstraction for future backends
- **Multiple Format Support**: 
  - CSV with delimiter inference
  - Excel (single and multi-sheet)
  - Parquet for large datasets
  - JSON and YAML for configuration
- **Project Structure Management**: 
  - Automated directory creation
  - Standardized project layout
  - Configurable structure
- **Advanced Features**:
  - Automatic metadata tracking
  - Timestamp support for versioning
  - Batch file operations
  - Format conversion
- **Developer Friendly**:
  - Full type hints
  - Comprehensive logging
  - Extensive documentation
  - Test coverage

## Quick Start

```python
from FileUtils import FileUtils
import pandas as pd

# Local storage
file_utils = FileUtils()

# Azure storage
azure_utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)

# Save DataFrame
df = pd.DataFrame({'A': [1, 2, 3]})
saved_files, metadata = file_utils.save_data_to_storage(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="my_data"
)

# Save multiple DataFrames
data_dict = {
    'data1': df1,
    'data2': df2
}
saved_files, metadata = file_utils.save_data_to_storage(
    data=data_dict,
    output_filetype="xlsx",
    output_type="processed",
    file_name="multi_sheet_data"
)

# Load data
loaded_df = file_utils.load_single_file("my_data.csv", input_type="processed")
```

## Installation

```bash
# Basic installation
pip install "git+https://github.com/topij/FileUtils.git"

# With Azure support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]"

# With Parquet support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[parquet]"

# With Excel support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[excel]"

# With all features
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]"
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - Core functionality and common use cases
- [Azure Setup](docs/AZURE_SETUP.md) - Azure storage setup and configuration

## Project Structure

FileUtils creates and manages the following default directory structure (can be changed as needed):
```
project_root/
├── data/
│   ├── raw/         # Original data
│   ├── interim/     # Intermediate processing
│   ├── processed/   # Final processed data
│   └── external/    # External data sources
├── reports/
│   ├── figures/     # Generated graphics
│   ├── tables/      # Generated tables
│   └── outputs/     # Analysis outputs
├── models/          # Trained models
└── src/            # Source code
```

## Development

For development installation:

```bash
# Clone repository
git clone git@github.com:topij/FileUtils.git
cd FileUtils

# Create conda environment
conda env create -f environment.yaml

# Activate environment
conda activate fileutils

# Install in development mode
python scripts/setup_dev.py
```

Run tests:
```bash
pytest
```

## Requirements

- Python 3.8 or later
- Core dependencies:
  - pandas>=1.3.0
  - PyYAML>=5.4.1
  - python-dotenv>=0.19.0
  - jsonschema>=3.2.0

Optional dependencies:
- Azure: azure-storage-blob, azure-identity
- Parquet: pyarrow
- Excel: openpyxl

## License

This project is licensed under the MIT License.