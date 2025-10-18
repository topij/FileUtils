# Getting Started with FileUtils

This guide provides a quick overview of how to use FileUtils for common data handling scenarios. It's aimed at helping developers get up and running quickly with the most essential features.

## Installation

```bash
# For basic usage (local storage only)
pip install FileUtils

# Or with all features
pip install 'FileUtils[all]'
```

## Core Use Cases

### 1. Simple Data Loading and Saving

```python
from FileUtils import FileUtils, OutputFileType
import pandas as pd

# Initialize FileUtils with default settings
file_utils = FileUtils()

# Create sample data
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
})

# Save as CSV in the "processed" directory
file_utils.save_data_to_storage(
    data=df,
    file_name="people",
    output_type="processed",
    output_filetype=OutputFileType.CSV
)

# Load CSV file from the "raw" directory
df = file_utils.load_single_file("data.csv", input_type="raw")
```

> **Important Note**: The `input_type` and `output_type` parameters specify the directory where files are stored (like "raw", "processed", "interim"), NOT the file format. These directory names indicate the purpose or stage of the data.

### 2. Handling Multiple File Formats

FileUtils automatically detects and handles multiple file formats based on file extension. You don't need to specify the file format when loading - it's determined from the file extension:

```python
# Save in different formats
file_utils.save_data_to_storage(df, file_name="people", output_type="processed", output_filetype=OutputFileType.CSV)
file_utils.save_data_to_storage(df, file_name="people", output_type="processed", output_filetype=OutputFileType.XLSX)
file_utils.save_data_to_storage(df, file_name="people", output_type="processed", output_filetype=OutputFileType.JSON)
file_utils.save_data_to_storage(df, file_name="people", output_type="processed", output_filetype=OutputFileType.PARQUET)
file_utils.save_data_to_storage(df, file_name="people", output_type="processed", output_filetype=OutputFileType.YAML)

# Load files of different formats - FileUtils automatically detects the format from the file extension
# No need to specify file type when loading
df_csv = file_utils.load_single_file("people.csv", input_type="processed")
df_excel = file_utils.load_single_file("people.xlsx", input_type="processed")
df_json = file_utils.load_single_file("people.json", input_type="processed")
df_parquet = file_utils.load_single_file("people.parquet", input_type="processed")
df_yaml = file_utils.load_single_file("people.yaml", input_type="processed")
```

### 3. Working with Excel Spreadsheets

```python
# Save multiple DataFrames to different Excel sheets
data_dict = {
    "People": df1,
    "Departments": df2,
    "Projects": df3
}

file_utils.save_data_to_storage(
    data=data_dict,
    file_name="company_data",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)

# Load all sheets from an Excel file
# FileUtils automatically detects this is an Excel file from the extension
sheets_dict = file_utils.load_excel_sheets("company_data.xlsx", input_type="processed")

# Access individual sheets
people_df = sheets_dict["People"]
departments_df = sheets_dict["Departments"]
```

### 4. Data with Metadata Tracking

Track files and their metadata for reproducible workflows:

```python
# Save data with metadata
saved_files, metadata_path = file_utils.save_with_metadata(
    data={"main_data": df1, "reference_data": df2},
    file_name="analysis_dataset",
    output_type="processed",
    output_filetype=OutputFileType.PARQUET
)

# Later, load everything using just the metadata file
all_data = file_utils.load_from_metadata(metadata_path)
main_df = all_data["main_data"]
reference_df = all_data["reference_data"]
```

### 5. Configuration Options

FileUtils can be configured in multiple ways:

```python
# Specify configuration directly
file_utils = FileUtils(
    project_root="/path/to/project",
    log_level="INFO",
    config_override={
        "csv_delimiter": ",",
        "encoding": "utf-8",
        "include_timestamp": True
    }
)

# Or use a configuration file
file_utils = FileUtils(config_file="path/to/config.yaml")
```

### 6. Loading Non-DataFrame Data

Access raw YAML and JSON data:

```python
# Load configuration or other structured data
# File format is automatically detected from extension
config = file_utils.load_yaml("config.yaml", input_type="raw")
settings = file_utils.load_json("settings.json", input_type="raw")
```

### 7. Document Handling

FileUtils supports rich document formats perfect for AI/agentic workflows:

```python
# Save AI analysis as Markdown with metadata
analysis_content = {
    "frontmatter": {
        "title": "AI Analysis Report",
        "model": "GPT-4",
        "confidence": 0.95
    },
    "body": """# Analysis Results

## Key Findings
- Pattern detected with 94.2% confidence
- 3 anomalies identified
- Recommended actions: Update model, retrain

## Next Steps
1. Review findings
2. Implement recommendations
3. Schedule follow-up
"""
}

saved_path, _ = file_utils.save_document_to_storage(
    content=analysis_content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="ai_analysis",
    sub_path="reports/2024"
)

# Load the document
loaded_content = file_utils.load_document_from_storage(
    file_path="ai_analysis.md",
    input_type="processed",
    sub_path="reports/2024"
)
```

**Note**: Document functionality requires optional dependencies. Install with `pip install 'FileUtils[documents]'`. Markdown works without additional dependencies.

## Common Patterns and Best Practices

### Organizing Data Files

FileUtils encourages organizing data by purpose or stage in the data processing pipeline:

```
project_root/
├── data/
│   ├── raw/          # Original, immutable data
│   ├── processed/    # Cleaned, transformed data
│   └── interim/      # Intermediate data
```

These directory names are what you pass to the `input_type` and `output_type` parameters:

```python
# Getting paths to these directories
raw_dir = file_utils.get_data_path("raw")  # "raw" is the directory name
processed_dir = file_utils.get_data_path("processed")  # "processed" is the directory name

# Loading a file from the raw directory
df = file_utils.load_single_file("data.csv", input_type="raw")  # "raw" refers to the directory

# Saving a file to the processed directory
file_utils.save_data_to_storage(df, file_name="output", output_type="processed")  # "processed" refers to the directory
```

### Error Handling

```python
from FileUtils.core.base import StorageError

try:
    df = file_utils.load_single_file("nonexistent.csv")
except StorageError as e:
    print(f"Failed to load file: {e}")
    # Take appropriate action
```

## Next Steps

- Check the [Usage Guide](USAGE.md) for more detailed examples
- See [Azure Setup Guide](AZURE_SETUP.md) for cloud storage options
- For comprehensive API details, refer to [API Reference](API_REFERENCE.md) 