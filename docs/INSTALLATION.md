# Installation Guide for FileUtils

### Requirements

- Python 3.9+
- pip or conda

## Installation Methods


### Basic Installation

1. Using pip

```bash
pip install "FileUtils @ git+https://github.com/topij/FileUtils.git"
```

### Installation with Optional Features
```bash
# Azure support
pip install "FileUtils[azure] @ git+https://github.com/topij/FileUtils.git"

# Parquet support
pip install "FileUtils[parquet] @ git+https://github.com/topij/FileUtils.git"

# Excel support
pip install "FileUtils[excel] @ git+https://github.com/topij/FileUtils.git"

# All features
pip install "FileUtils[all] @ git+https://github.com/topij/FileUtils.git"
```

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/username/FileUtils.git
cd FileUtils
```

2. Create and activate conda environment:
```bash
conda env create -f environment.yaml
conda activate fileutils
```

3. Install in development mode:
```bash
pip install -e .
```

## Azure Support

For Azure Blob Storage support, ensure the following dependencies are installed:
```bash
pip install azure-storage-blob azure-identity
```

See [AZURE_SETUP.md](AZURE_SETUP.md) for Azure configuration details.

## Configuration

The package will look for a `config.yaml` file in your project root. Create one if needed:

```yaml
# config.yaml
csv_delimiter: ","
encoding: "utf-8"
include_timestamp: false
logging_level: "INFO"
directory_structure:
  data:
    - raw
    - processed
    - interim
  reports:
    - figures
```