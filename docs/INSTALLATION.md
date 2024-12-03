# Installation Guide for FileUtils

This guide covers all installation methods and configurations for FileUtils.

## Table of Contents
- [Basic Installation](#basic-installation)
- [Installation with Optional Features](#installation-with-optional-features)
- [Development Installation](#development-installation)
- [Environment Setup](#environment-setup)
- [Troubleshooting](#troubleshooting)
- [System Requirements](#system-requirements)

## Basic Installation

### Using pip

For basic functionality (local storage only):
```bash
pip install FileUtils
```

### Using pip with Git

Install directly from GitHub:
```bash
pip install "git+ssh://git@github.com/topij/FileUtils.git"
```

## Installation with Optional Features

FileUtils provides several optional feature sets:

### Azure Storage Support
```bash
pip install FileUtils[azure]
```

### Parquet Support
```bash
pip install FileUtils[parquet]
```

### Excel Support
```bash
pip install FileUtils[excel]
```

### All Optional Features
```bash
pip install FileUtils[all]
```

### Multiple Optional Features
```bash
pip install FileUtils[azure,parquet,excel]
```

### From GitHub with Features
```bash
# All features
pip install "git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[all]"

# Specific features
pip install "git+ssh://git@github.com/topij/FileUtils.git#egg=FileUtils[azure,parquet]"
```

## Development Installation

For development work:

1. Clone the repository:
```bash
git clone git@github.com:topij/FileUtils.git
cd FileUtils
```

2. Install in development mode:
```bash
# Basic installation
pip install -e .

# With all features
pip install -e ".[all]"
```

## Environment Setup

1. Create and activate a virtual environment (recommended):
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Using conda
conda create -n fileutils python=3.8
conda activate fileutils
```

2. Optional: Create a `.env` file for Azure credentials:
```bash
# .env
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

## System Requirements

### Minimum Requirements
- Python 3.8 or later
- pip 19.0 or later

### Core Dependencies
- pandas >= 1.3.0
- PyYAML >= 5.4.1
- python-dotenv >= 0.19.0
- jsonschema >= 3.2.0

### Optional Dependencies
- Azure Storage:
  - azure-storage-blob >= 12.0.0
  - azure-identity >= 1.5.0
- Parquet Support:
  - pyarrow >= 7.0.0
- Excel Support:
  - openpyxl >= 3.0.9

## Troubleshooting

### Common Issues

1. Package not found
```bash
# Make sure you're using the correct package name
pip install FileUtils  # Note the capital F and U
```

2. Dependency conflicts
```bash
# Try installing in a clean environment
python -m venv fresh_env
source fresh_env/bin/activate
pip install FileUtils[all]
```

3. Git installation issues
```bash
# Ensure you have Git installed and SSH keys configured
git --version
# Configure SSH if needed
ssh-keygen -t rsa -b 4096
```

4. Permission issues
```bash
# Try installing for current user only
pip install --user FileUtils

# Or use a virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install FileUtils
```

### Version Verification

Verify your installation:
```python
import FileUtils
print(FileUtils.__version__)
```

## Next Steps

After installation:
1. Read the [Getting Started Guide](GETTING_STARTED.md)
2. Configure your [Azure Storage](AZURE_SETUP.md) if needed
3. Check the [Usage Guide](USAGE.md) for examples

<!-- ## Support



If you encounter any issues:
1. Check the [GitHub Issues](https://github.com/topij/FileUtils/issues)
2. Search for similar problems in closed issues
3. Create a new issue with:
   - Python version (`python --version`)
   - FileUtils version (`pip show FileUtils`)
   - Full error message
   - Minimal reproducible example -->