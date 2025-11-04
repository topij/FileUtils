# tests/conftest.py

import warnings

# Suppress PyMuPDF deprecation warnings globally
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPy.*")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*swigvarlink.*"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")

import os
import sys
import tempfile
from pathlib import Path
import csv

import pytest
import pandas as pd

# Add the src directory to Python path
pkg_root = str(Path(__file__).parent.parent / "src")
if pkg_root not in sys.path:
    sys.path.insert(0, pkg_root)

from FileUtils import FileUtils
from FileUtils.core.enums import StorageType


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_df():
    """Create sample DataFrame for tests."""
    return pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "London", "Paris"],
        }
    )


@pytest.fixture
def sample_config(temp_dir):
    """Create sample configuration."""
    config = {
        "csv_delimiter": ",",
        "encoding": "utf-8",
        "quoting": csv.QUOTE_MINIMAL,  # Added required field
        "include_timestamp": False,
        "logging_level": "INFO",  # Added required field
        "disable_logging": False,  # Added required field
        "directory_structure": {
            "data": ["raw", "processed", "interim"],
            "reports": ["figures"],
        },
    }

    config_path = temp_dir / "config.yaml"
    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


# Update file_utils fixture
@pytest.fixture
def file_utils(temp_dir, sample_config):
    """Create FileUtils instance for testing."""
    from FileUtils import FileUtils

    # Create instance without storage_type first
    utils = FileUtils(project_root=temp_dir, config_file=sample_config)

    # If you need to set storage type after initialization:
    # utils.storage = utils._create_storage("local")

    return utils
