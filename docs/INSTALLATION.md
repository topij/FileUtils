# Installation Guide for FileUtils

## Installation Methods

### 1. Basic Installation

```bash
# Basic installation (local storage only)
pip install "git+https://github.com/topij/FileUtils.git"
```

### 2. Installation with Optional Features

```bash
# With Azure support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]"

# With Parquet support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[parquet]"

# With Excel support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[excel]"

# With all features
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]"
```

### 3. Development Installation

```bash
# Clone the repository
git clone git@github.com:topij/FileUtils.git
cd FileUtils

# Create and activate conda environment
conda env create -f environment.yaml
conda activate fileutils

# Install in development mode
python scripts/setup_dev.py
```

## Dependencies

### Core Dependencies
```
pandas >= 1.3.0
pyyaml >= 5.4.1
python-dotenv >= 0.19.0
jsonschema >= 3.2.0
```

### Optional Dependencies

Azure Storage:
```
azure-storage-blob >= 12.0.0
azure-identity >= 1.5.0
```

Parquet Support:
```
pyarrow >= 7.0.0
```

Excel Support:
```
openpyxl >= 3.0.9
```

## Configuration

### 1. Basic Configuration

Create a `config.yaml` file:
```yaml
csv_delimiter: ","
encoding: "utf-8"
include_timestamp: true
logging_level: "INFO"

directory_structure:
  data:
    - raw
    - interim
    - processed
    - external
  reports:
    - figures
    - outputs
    - tables
  models:
    - trained
```

### 2. Azure Storage Configuration

For Azure storage, add to your config.yaml:
```yaml
storage:
  default_type: "azure"
  azure:
    enabled: true
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
      interim: "interim-data"
    retry_settings:
      max_retries: 3
      retry_delay: 1
```

Or use environment variables:
```bash
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

## Verification

### 1. Test Installation

```python
from FileUtils import FileUtils

# Create instance
utils = FileUtils()

# Check version
print(FileUtils.__version__)

# Check configuration
print(utils.config)
```

### 2. Test Storage

```python
import pandas as pd

# Create test data
df = pd.DataFrame({'test': [1, 2, 3]})

# Test saving
saved_files, metadata = utils.save_data_to_storage(
    data=df,
    output_filetype="csv",
    output_type="processed",
    file_name="test"
)

# Test loading
loaded_df = utils.load_single_file("test.csv", input_type="processed")
```

## Troubleshooting

### Common Issues

1. Module Not Found
```bash
# Ensure correct environment activation
conda activate fileutils

# Reinstall package
pip install -e ".[all]"
```

2. Azure Connection Issues
```python
# Verify Azure credentials
import os
print(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))

# Test Azure connection explicitly
utils = FileUtils(
    storage_type="azure",
    connection_string="your_connection_string"
)
```

3. Dependency Issues
```bash
# Update all dependencies
conda env update -f environment.yaml

# Reinstall specific dependencies
pip install -r requirements/dev.txt
```

### Environment Setup

1. Using conda:
```bash
# Create new environment
conda env create -f environment.yaml

# Update existing environment
conda env update -f environment.yaml
```

2. Development setup:
```bash
# Install dev dependencies
python scripts/setup_dev.py

# Run tests
pytest

# Build package
python scripts/build_package.py
```

## Version Management

FileUtils uses semantic versioning:
- Major version: Incompatible API changes
- Minor version: Added functionality (backwards-compatible)
- Patch version: Bug fixes (backwards-compatible)

Check your installed version:
```python
from FileUtils import __version__
print(__version__)
```

For more detailed usage instructions, see the [Usage Guide](USAGE.md).