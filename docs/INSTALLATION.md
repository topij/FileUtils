# Installation Guide for FileUtils

Complete installation guide for FileUtils with all options and configurations.

## Basic Installation

### From GitHub

```bash
# Basic installation (local storage only)
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

### Development Installation

For development work:
```bash
# Clone the repository
git clone git@github.com:topij/FileUtils.git
cd FileUtils

# Install in development mode
pip install -e ".[all]"  # All features
# or
pip install -e ".[azure]"  # Azure support only
```

## Configuration

### Basic Configuration

Create a config.yaml file:
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
  reports:
    - figures
    - outputs
```

### Storage Configuration

For Azure Storage:
```yaml
storage:
  default_type: "azure"
  azure:
    enabled: true
    container_mapping:
      raw: "raw-data"
      processed: "processed-data"
      interim: "interim-data"
```

Or set via environment variables:
```bash
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

## Dependencies

### Core Dependencies
- pandas >= 1.3.0
- pyyaml >= 5.4.1
- python-dotenv >= 0.19.0
- jsonschema >= 3.2.0

### Optional Dependencies
- Azure Storage: azure-storage-blob, azure-identity
- Parquet support: pyarrow
- Excel support: openpyxl

## Verification

Verify your installation:
```python
import FileUtils
print(FileUtils.__version__)

# Test configuration
from FileUtils import FileUtils
utils = FileUtils()
print(utils.config)
```

## Troubleshooting

### Common Issues

1. Package not found:
```bash
pip install -e .  # Install in development mode
```

2. Missing dependencies:
```bash
pip install -r requirements/all.txt
```

3. Azure Storage issues:
```bash
pip install ".[azure]"  # Install Azure dependencies
```

### Environment Setup

1. Using virtual environments:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

2. Using conda:
```bash
conda create -n fileutils python=3.8
conda activate fileutils
pip install -e ".[all]"
```

For more detailed usage instructions, see the [Usage Guide](USAGE.md).