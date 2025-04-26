# Development Guide

This guide explains how to set up the development environment and package the FileUtils project.

## Project Structure

```
FileUtils/
├── src/
│   └── FileUtils/
│       ├── core/       # Core functionality
│       ├── storage/    # Storage implementations
│       ├── config/     # Configuration handling
│       └── utils/      # Utility functions
├── tests/
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── docs/              # Documentation
├── scripts/           # Build and utility scripts
├── pyproject.toml     # Project configuration
└── README.md         # Project overview
```

## Development Setup

### Option 1: Using the provided environment.yaml (Recommended)

The project includes an `environment.yaml` file that defines all required dependencies for development, testing, and building the package.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FileUtils.git
   cd FileUtils
   ```

2. Create a Conda environment from the environment.yaml file:
   ```bash
   # Create and activate the environment from the yaml file
   conda env create -f environment.yaml
   conda activate fileutils
   ```

3. Install the package in development mode:
   ```bash
   # Install in editable mode
   pip install -e .
   ```

4. Verify the installation:
   ```bash
   # Run a simple import test
   python -c "from FileUtils import FileUtils"
   
   # Run the test suite
   pytest tests/unit
   ```

### Option 2: Manual setup

If you prefer to set up the environment manually:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FileUtils.git
   cd FileUtils
   ```

2. Create a Conda environment:
   ```bash
   # Create new environment with Python 3.9+
   conda create -n fileutils python=3.9
   
   # Activate the environment
   conda activate fileutils
   
   # Optional: Install common development tools
   conda install pytest pytest-cov build twine
   ```

3. Install the package in development mode:
   ```bash
   # Install in editable mode with all optional dependencies
   pip install -e ".[all]"
   ```

4. Verify the installation:
   ```bash
   # Run a simple import test
   python -c "from FileUtils import FileUtils"
   
   # Run the test suite
   pytest tests/
   ```

## Managing Dependencies with Conda

### Core Dependencies
```bash
# Install core dependencies
conda install pandas pyyaml python-dotenv
```

### Optional Dependencies
```bash
# Azure support
conda install -c conda-forge azure-storage-blob azure-identity

# Parquet support
conda install pyarrow

# Excel support
conda install openpyxl
```

### Development Dependencies
```bash
# Install development tools
conda install pytest pytest-cov build twine

# Optional: Install documentation tools
conda install -c conda-forge sphinx sphinx_rtd_theme
```

## Package Configuration

The project uses `pyproject.toml` for package configuration. Key sections include:

- **Build System**: Uses `setuptools` for building
- **Project Metadata**: Name, version, description, etc.
- **Dependencies**: 
  - Core dependencies (pandas, pyyaml, etc.)
  - Optional dependencies (azure, parquet, excel)
  - Development dependencies

## Building the Package

The project includes a comprehensive build script (`scripts/build_package.py`) that:

1. Cleans previous builds
2. Verifies directory structure
3. Checks version consistency
4. Validates dependencies
5. Builds the package
6. Tests the installation

To build the package:

```bash
python scripts/build_package.py
```

Or manually:

```bash
python -m build
```

## Installing from GitHub

The package can be installed directly from GitHub using pip:

```bash
pip install git+https://github.com/yourusername/FileUtils.git
```

With optional dependencies:

```bash
# Install with Azure support
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]"

# Install with all optional dependencies
pip install "git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]"
```

## Version Management

Version numbers are maintained in:
- `src/FileUtils/version.py`
- `pyproject.toml`

When updating the version:
1. Update the version in `src/FileUtils/version.py`
2. Update `pyproject.toml`
3. Run the build script to verify version consistency

## Testing

Run tests using pytest:

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=FileUtils
```

## Optional Dependencies

The package uses optional dependency groups:

- **azure**: Azure Blob Storage support
  - azure-storage-blob
  - azure-identity
- **parquet**: Parquet file support
  - pyarrow
- **excel**: Excel file support
  - openpyxl
- **all**: All optional dependencies


## Common Issues

- **Version Mismatch**: Ensure versions match in all files
- **Missing Dependencies**: Install all required dependencies
- **Build Failures**: Check the build script output for details
- **Test Failures**: Run tests with `-v` flag for verbose output
- **License Metadata**: If experiencing build issues related to the license format, ensure the license is specified as a simple string in pyproject.toml (`license = "MIT"` rather than the table format)
- **Conda Environment Issues**:
  - Use `conda list` to verify installed packages
  - If experiencing conflicts, try creating a fresh environment
  - For package conflicts, try installing with `conda-forge`: `conda install -c conda-forge package_name`
  - Use `conda env export > environment.yml` to save your environment configuration
  - Restore environment with `conda env create -f environment.yaml` 