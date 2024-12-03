"""Example showing configuration options and customization in FileUtils."""

import yaml
from pathlib import Path
from FileUtils import FileUtils


def create_custom_config():
    """Create a custom configuration file."""
    config = {
        "csv_delimiter": "|",
        "encoding": "utf-8",
        "quoting": 0,
        "include_timestamp": True,
        "logging_level": "DEBUG",
        "disable_logging": False,
        "directory_structure": {
            "data": ["raw", "interim", "processed", "external"],
            "reports": ["figures", "tables", "presentations"],
            "models": ["trained", "evaluations"],
            "documentation": ["specs", "api"],
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

    # Show other settings
    print("\nOther settings:")
    for key, value in file_utils.config.items():
        if key != "directory_structure":
            print(f"{key}: {value}")


if __name__ == "__main__":
    demonstrate_configuration()
