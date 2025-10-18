# Installation Guide

This guide explains how to install FileUtils and its dependencies for different use cases.

## Basic Installation

For basic local storage operations:

```bash
pip install FileUtils
```

This installs the core package with support for:
- Basic file operations
- CSV file handling
- JSON and YAML file handling
- Directory management
- Configuration system

## Feature-Specific Installation

FileUtils uses optional dependencies to keep the base installation light. Choose the features you need:

### Azure Blob Storage Support

```bash
pip install 'FileUtils[azure]'
```

This adds:
- Azure Blob Storage operations
- Azure authentication handling
- Transparent fallback to local storage if connection fails

### Parquet Support

```bash
pip install 'FileUtils[parquet]'
```

This adds:
- Parquet file reading/writing
- Compression options
- Arrow-based optimizations

### Excel Support

```bash
pip install 'FileUtils[excel]'
```

This adds:
- Excel file reading/writing
- Multi-sheet support
- OpenPyXL engine integration

### Document Support

```bash
pip install 'FileUtils[documents]'
```

This adds:
- Microsoft Word (.docx) file support
- Markdown (.md) file support with YAML frontmatter
- PDF file support (read-only text extraction)
- Rich document content handling

**Note**: Markdown functionality works without additional dependencies. DOCX and PDF require the optional packages.

### All Features

To install all optional dependencies:

```bash
pip install 'FileUtils[all]'
```

## Installation from GitHub

For the latest development version:

```bash
# Basic installation
pip install git+https://github.com/topij/FileUtils.git

# With specific features
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]'
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]'
```

## Conda Environment

If you're using Conda, create a new environment first:

```bash
# Create new environment
conda create -n fileutils python=3.9

# Activate environment
conda activate fileutils

# Install FileUtils with pip
pip install 'FileUtils[all]'  # or any other installation option
```

## Dependency Management

### Core Dependencies
These are installed automatically with the base package:
- pandas
- pyyaml
- python-dotenv
- jsonschema

### Optional Dependencies
Choose based on your needs:

- Azure Storage (`[azure]`):
  - azure-storage-blob
  - azure-identity
- Parquet Support (`[parquet]`):
  - pyarrow
- Excel Support (`[excel]`):
  - openpyxl
- Document Support (`[documents]`):
  - python-docx (Microsoft Word documents)
  - markdown (Markdown processing)
  - PyMuPDF (PDF read/write, supports multiple formats)

## Verifying Installation

Test your installation:

```python
from FileUtils import FileUtils

# Basic functionality (works with any installation)
file_utils = FileUtils()

# Azure functionality (requires [azure] extra)
file_utils_azure = FileUtils(storage_type="azure", connection_string="your_connection_string")
```

## Troubleshooting

### Missing Azure Dependencies
If you see an error like:
```
ModuleNotFoundError: No module named 'azure'
```
Install Azure dependencies:
```bash
pip install 'FileUtils[azure]'
```

### Missing Excel Support
If you see an error about `openpyxl`:
```bash
pip install 'FileUtils[excel]'
```

### Missing Parquet Support
If you see an error about `pyarrow`:
```bash
pip install 'FileUtils[parquet]'
```

### Missing Document Support
If you see errors about document dependencies:
```bash
# Install all document support
pip install 'FileUtils[documents]'

# Or install specific dependencies
pip install python-docx markdown PyMuPDF
```

**Note**: Markdown functionality works without additional dependencies. Only DOCX and PDF require optional packages.

### Conda Environment Issues
If you encounter package conflicts in Conda:
```bash
# Try installing from conda-forge
conda install -c conda-forge azure-storage-blob
conda install -c conda-forge pyarrow
conda install -c conda-forge openpyxl

# Then install FileUtils
pip install FileUtils
```