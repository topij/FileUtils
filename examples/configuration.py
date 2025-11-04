"""Example showing configuration options and customization in FileUtils."""

import yaml
from pathlib import Path
import pandas as pd
from FileUtils import FileUtils, OutputFileType


def create_custom_config():
    """Create a custom configuration file."""
    config = {
        "csv_delimiter": "|",
        "encoding": "utf-8",
        "quoting": 0,  # csv.QUOTE_MINIMAL
        "include_timestamp": True,
        "logging_level": "DEBUG",
        # Directory structure
        "directory_structure": {
            "data": ["raw", "interim", "processed", "external"],
            "reports": ["figures", "tables", "presentations"],
            "models": ["trained", "evaluations"],
            "docs": ["api", "guides"],
        },
        # Storage settings
        "storage": {
            "default_type": "local",
            "azure": {
                "enabled": False,
                "container_mapping": {
                    "raw": "raw-data",
                    "processed": "processed-data",
                    "interim": "interim-data",
                },
                "retry_settings": {
                    "max_retries": 3,
                    "retry_delay": 1,
                    "max_delay": 30,
                },
            },
        },
    }

    config_path = Path("custom_config.yaml")
    with open(config_path, "w") as f:
        yaml.dump(config, f)

    return config_path


def demonstrate_configuration():
    """Demonstrate configuration options."""
    # Create custom config
    config_path = create_custom_config()
    print(f"Created custom config at: {config_path}")

    # Initialize FileUtils with custom config
    file_utils = FileUtils(config_file=config_path)

    # Show configured directories
    print("\nConfigured directories:")
    for main_dir, sub_dirs in file_utils.config["directory_structure"].items():
        print(f"\n{main_dir}/")
        for sub_dir in sub_dirs:
            print(f"  ├── {sub_dir}/")

    # Test with sample data
    df = pd.DataFrame({"name": ["Alice", "Bob"], "score": [95, 87]})

    # Save with custom delimiter
    saved_files, metadata = file_utils.save_data_to_storage(
        data=df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="custom_delim_test",
    )

    # Show file contents
    print("\nFile with custom delimiter:")
    with open(list(saved_files.values())[0], "r") as f:
        print(f.read())

    # Clean up
    config_path.unlink()
    print("\nConfiguration test completed")


if __name__ == "__main__":
    demonstrate_configuration()
