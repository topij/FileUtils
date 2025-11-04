"""
Example: Working with Root-Level Directories

This example demonstrates how to use FileUtils to work with directories
outside the data directory, such as config, logs, or other project-level folders.
"""

from FileUtils import FileUtils, OutputFileType
import pandas as pd

# Initialize FileUtils
file_utils = FileUtils()

# Example 1: Save configuration file to config directory at project root
config_data = {
    "database": {"host": "localhost", "port": 5432, "name": "analytics"},
    "api": {"timeout": 30, "retries": 3, "base_url": "https://api.example.com"},
}

# Save to config directory at project root (not under data/)
saved_path, _ = file_utils.save_document_to_storage(
    content=config_data,
    output_filetype=OutputFileType.JSON,
    output_type="config",
    file_name="app_config",
    root_level=True,  # This creates/config directory at project root
)
print(f"✅ Saved config to: {saved_path}")

# Load configuration from root-level config directory
loaded_config = file_utils.load_json(
    file_path="app_config.json", input_type="config", root_level=True
)
print(f"✅ Loaded config: {loaded_config['database']['host']}")

# Example 2: Save logs/data to logs directory at project root
log_data = pd.DataFrame(
    {
        "timestamp": pd.date_range("2024-01-01", periods=5, freq="H"),
        "level": ["INFO", "WARNING", "ERROR", "INFO", "DEBUG"],
        "message": ["Started", "Low memory", "Crash!", "Recovered", "Cleanup"],
    }
)

saved_files, _ = file_utils.save_data_to_storage(
    data=log_data,
    output_filetype=OutputFileType.CSV,
    output_type="logs",
    file_name="application_logs",
    root_level=True,  # Creates logs/ directory at project root
)
print(f"✅ Saved logs to: {saved_files}")

# Load logs from root-level logs directory
loaded_logs = file_utils.load_single_file(
    file_path="application_logs.csv", input_type="logs", root_level=True
)
print(f"✅ Loaded {len(loaded_logs)} log entries")

# Example 3: Working with YAML config files at root level
yaml_config = {
    "project": {"name": "MyProject", "version": "1.0.0"},
    "settings": {"debug": True, "workers": 4},
}

saved_yaml_path, _ = file_utils.save_document_to_storage(
    content=yaml_config,
    output_filetype=OutputFileType.YAML,
    output_type="config",
    file_name="project_config",
    root_level=True,
)
print(f"✅ Saved YAML config to: {saved_yaml_path}")

# Example 4: Compare root-level vs data directory
# Save to data directory (default behavior)
saved_data_dir, _ = file_utils.save_data_to_storage(
    data=log_data,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="logs_in_data",
    root_level=False,  # Goes to data/processed/
)

# Save to root-level logs directory
saved_root_dir, _ = file_utils.save_data_to_storage(
    data=log_data,
    output_filetype=OutputFileType.CSV,
    output_type="logs",
    file_name="logs_at_root",
    root_level=True,  # Goes to logs/ at project root
)

print(f"📁 Data directory: {saved_data_dir}")
print(f"📁 Root directory: {saved_root_dir}")

# Example 5: Using sub_path with root-level directories
saved_with_subpath, _ = file_utils.save_document_to_storage(
    content={"key": "value"},
    output_filetype=OutputFileType.JSON,
    output_type="config",
    file_name="nested_config",
    sub_path="environments/production",
    root_level=True,  # Creates config/environments/production/ at root
)
print(f"✅ Saved nested config to: {saved_with_subpath}")

print("\n✨ All examples completed successfully!")
print("\nSummary:")
print("- root_level=True: Files go to <project_root>/<directory_type>/")
print("- root_level=False (default): Files go to <project_root>/data/<directory_type>/")
