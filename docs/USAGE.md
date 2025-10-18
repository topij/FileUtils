# Usage Guide

## Basic Usage

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with default configuration
file_utils = FileUtils()

# Load data from different formats
df_csv = file_utils.load_single_file("data.csv", input_type="raw")
df_excel = file_utils.load_single_file("data.xlsx", input_type="raw")
df_parquet = file_utils.load_single_file("data.parquet", input_type="raw")
df_json = file_utils.load_single_file("data.json", input_type="raw")
df_yaml = file_utils.load_single_file("data.yaml", input_type="raw")
v
# Save data
file_utils.save_data_to_storage(
    data=df,  # Single DataFrame
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.CSV
)

# Save multiple DataFrames
file_utils.save_data_to_storage(
    data={"Sheet1": df1, "Sheet2": df2},  # Dictionary of DataFrames
    file_name="multi_output",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)

# Save to a specific subdirectory dynamically
file_utils.save_data_to_storage(
    data=df,
    file_name="report_summary",
    output_type="processed",
    output_filetype=OutputFileType.CSV,
    sub_path="run_1/results" # Creates data/processed/run_1/results/
)

# Load data from the specific subdirectory
loaded_df = file_utils.load_single_file(
    file_path="report_summary.csv", # Just the filename
    input_type="processed",
    sub_path="run_1/results" # Specify the sub_path
)

# Load multiple files from a subdirectory
# Assume data_a.csv and data_b.csv exist in data/raw/source_x/files/
multi_loaded = file_utils.load_multiple_files(
    file_paths=["data_a.csv", "data_b.csv"], # Filenames only
    input_type="raw",
    sub_path="source_x/files"
)
```

## File Format Support

### CSV Files
```python
# Save CSV with custom delimiter
file_utils.save_data_to_storage(
    data=df,
    file_name="output",
    output_filetype=OutputFileType.CSV,
    encoding="utf-8",
    sep="|"  # Custom delimiter
)

# Load CSV (delimiter is auto-detected)
df = file_utils.load_single_file("data.csv")
```

### Excel Files
```python
# Save multiple sheets to Excel
data_dict = {
    "Sheet1": df1,
    "Sheet2": df2
}
file_utils.save_data_to_storage(
    data=data_dict,
    file_name="multi_sheet",
    output_filetype=OutputFileType.XLSX
)

# Load all sheets from Excel
sheets_dict = file_utils.load_excel_sheets("multi_sheet.xlsx")
```

### JSON Files
```python
# Save JSON in different formats
file_utils.save_data_to_storage(
    data=df,
    file_name="records",
    output_filetype=OutputFileType.JSON,
    orient="records"  # List of records format
)

file_utils.save_data_to_storage(
    data=df,
    file_name="index",
    output_filetype=OutputFileType.JSON,
    orient="index"  # Dictionary format with index as keys
)

# Load JSON (format is auto-detected)
df = file_utils.load_single_file("data.json")

# Load raw JSON data
data = file_utils.load_json("config.json")
```

### YAML Files
```python
# Save YAML with custom options
file_utils.save_data_to_storage(
    data=df,
    file_name="output",
    output_filetype=OutputFileType.YAML,
    yaml_options={
        "default_flow_style": False,
        "sort_keys": True,
        "indent": 4
    },
    orient="records"  # or "index"
)

# Load YAML as DataFrame
df = file_utils.load_single_file("data.yaml")

# Load raw YAML data
data = file_utils.load_yaml("config.yaml")
```

### Parquet Files
```python
# Save Parquet with compression
file_utils.save_data_to_storage(
    data=df,
    file_name="output",
    output_filetype=OutputFileType.PARQUET,
    compression="snappy"  # or "gzip", "brotli", etc.
)

# Load Parquet
df = file_utils.load_single_file("data.parquet")
```

## Document Handling

FileUtils now supports rich document formats perfect for AI/agentic workflows:

### Markdown Files
```python
# Save simple markdown
markdown_content = """# Analysis Report

## Key Findings
- Model accuracy: 95.2%
- Processing time: 2.3 seconds

## Recommendations
1. Implement additional training data
2. Optimize inference pipeline
"""

saved_path, _ = file_utils.save_document_to_storage(
    content=markdown_content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="analysis_report"
)

# Save markdown with YAML frontmatter
structured_content = {
    "frontmatter": {
        "title": "AI Analysis Report",
        "author": "AI Agent",
        "confidence": 0.95,
        "timestamp": "2024-01-15T10:30:00Z"
    },
    "body": """# Analysis Results

## Summary
The analysis identified 3 key insights.

## Key Findings
- Pattern detected with 94.2% confidence
- 3 anomalies identified
- Recommended actions: Update model, retrain
"""
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="structured_report",
    sub_path="reports/2024"
)

# Load markdown
loaded_content = file_utils.load_document_from_storage(
    file_path="analysis_report.md",
    input_type="processed"
)
```

### DOCX Files
```python
# Save simple DOCX document
docx_content = "This is a test document for DOCX format."

saved_path, _ = file_utils.save_document_to_storage(
    content=docx_content,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="simple_document"
)

# Save structured DOCX with headings and tables
structured_docx = {
    "title": "Project Report",
    "sections": [
        {
            "heading": "Executive Summary",
            "level": 1,
            "text": "Project completed successfully."
        },
        {
            "heading": "Results",
            "level": 2,
            "table": [
                ["Metric", "Value", "Unit"],
                ["Accuracy", "95.2", "%"],
                ["Speed", "2.3", "seconds"],
                ["Memory", "512", "MB"]
            ]
        }
    ]
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_docx,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="project_report"
)

# Load DOCX (extracts text content)
loaded_content = file_utils.load_document_from_storage(
    file_path="simple_document.docx",
    input_type="processed"
)
```

### PDF Files
```python
# Save simple PDF
pdf_content = "This is a test document for PDF format."

saved_path, _ = file_utils.save_document_to_storage(
    content=pdf_content,
    output_filetype=OutputFileType.PDF,
    output_type="processed",
    file_name="simple_pdf"
)

# Save structured PDF
structured_pdf = {
    "title": "Technical Documentation",
    "sections": [
        {
            "heading": "Introduction",
            "text": "This document provides technical specifications."
        },
        {
            "heading": "Architecture",
            "text": "The system follows a microservices architecture."
        }
    ]
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_pdf,
    output_filetype=OutputFileType.PDF,
    output_type="processed",
    file_name="technical_doc"
)

# Load PDF (extracts text content)
loaded_content = file_utils.load_document_from_storage(
    file_path="simple_pdf.pdf",
    input_type="processed"
)
```

### Document Dependencies

Document functionality requires optional dependencies:

```bash
# Install document support
pip install 'FileUtils[documents]'

# Or install specific dependencies
pip install python-docx markdown PyMuPDF
```

**Note**: Markdown functionality works without additional dependencies. DOCX and PDF require the optional packages.

## Directory Management

FileUtils manages data in a structured directory layout:
```
project_root/
├── data/
│   ├── raw/          # Raw data files
│   ├── processed/    # Processed data files
│   └── interim/      # Intermediate data files
└── reports/
    └── figures/      # Generated figures
```

You can create new directories within this structure:

```python
# Create new directory under data/
features_dir = file_utils.create_directory("features")

# Create directory under specific parent
reports_dir = file_utils.create_directory("monthly", parent_dir="reports")

# Directory is added to configuration structure
print(file_utils.config["directory_structure"]["data"])  # Shows ['raw', 'processed', 'interim', 'features']
```

## Configuration

You can override default settings using a `config.yaml` file:

```yaml
# File handling
csv_delimiter: ","
encoding: "utf-8"
quoting: "minimal"
include_timestamp: false

# Logging
logging_level: "INFO"

# Directory structure
directory_structure:
  data:
    - raw
    - processed
    - interim
  reports:
    - figures
  models:
    - trained
```

## Azure Storage

For Azure Blob Storage operations, see [AZURE_SETUP.md](AZURE_SETUP.md).

## Error Handling

FileUtils provides detailed error messages through custom exceptions:
- `StorageError`: Base exception for storage operations
- `StorageOperationError`: Specific operation failures (e.g., file not found, invalid format)
- `ConfigurationError`: Configuration-related issues

Example error handling:
```python
from FileUtils.core.base import StorageError

try:
    df = file_utils.load_single_file("nonexistent.csv")
except StorageError as e:
    print(f"Failed to load file: {e}")
```

## Logging

Logging is configurable through the config file or at runtime:
```yaml
# In config.yaml
logging_level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

```python
# At runtime
file_utils.set_logging_level("DEBUG")
```

The logger provides information about:
- File operations (save/load)
- Directory creation
- Configuration changes
- Error details