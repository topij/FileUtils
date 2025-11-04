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
#
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

# Enhanced DOCX with Template Support
markdown_content = """# Project Report

## Executive Summary
This is a comprehensive analysis of our project progress.

## Key Findings
- **Important**: We've achieved 95% completion
- [ ] Complete final testing
- [x] Update documentation

| Metric | Value | Status |
|--------|-------|--------|
| Progress | 95% | ✅ On Track |
| Budget | $45,000 | ✅ Under Budget |
"""

# Convert markdown to DOCX with template
saved_path, _ = file_utils.save_document_to_storage(
    content=markdown_content,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="project_report",
    template="review",  # Use specific template
    add_provenance=True,
    add_reviewer_instructions=True
)

# Load multiple files from a subdirectory
# Assume data_a.csv and data_b.csv exist in data/raw/source_x/files/
multi_loaded = file_utils.load_multiple_files(
    file_paths=["data_a.csv", "data_b.csv"], # Filenames only
    input_type="raw",
    sub_path="source_x/files"
)
```

## New conveniences

### Saving bytes (artifacts)

```python
from FileUtils.core.enums import OutputArea

chart_path = file_utils.save_bytes(
    content=png_bytes,
    file_stem="chart_q1",
    sub_path="runs/acme/images",
    output_type=OutputArea.PROCESSED,  # or "processed"
    file_ext="png",
)
```

### Structured results

```python
from FileUtils import SaveResult

res_map, _ = file_utils.save_data_to_storage(
    data={"Sheet1": df1, "Sheet2": df2},
    output_filetype=OutputFileType.XLSX,
    file_name="multi_sheet",
    structured_result=True,
)
assert isinstance(next(iter(res_map.values())), SaveResult)
```

### Using typed enums for directories

```python
from FileUtils.core.enums import InputType, OutputArea

file_utils.load_document_from_storage("readme.md", input_type=InputType.RAW)
file_utils.save_document_to_storage("# notes", OutputFileType.MARKDOWN, output_type=OutputArea.PROCESSED)
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

### Excel to CSV Conversion

Convert Excel workbooks with multiple worksheets to CSV files while preserving workbook structure and metadata.

```python
# Convert Excel workbook to CSV files with structure preservation
csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
    excel_file_path="workbook.xlsx",
    file_name="converted_workbook",
    preserve_structure=True
)

# Result:
# csv_files = {
#     "Sheet1": "data/processed/converted_workbook_Sheet1.csv",
#     "Sheet2": "data/processed/converted_workbook_Sheet2.csv"
# }
# structure_file = "data/processed/converted_workbook_structure.json"

# Load converted data
employees_df = file_utils.load_single_file(
    "converted_workbook_Employees.csv", 
    input_type="processed"
)
```

**Structure JSON includes:**
- Workbook metadata (source file, conversion timestamp, sheet count)
- Sheet details (dimensions, columns, data types, null counts)
- Data quality metrics (memory usage, index information)

### CSV to Excel Reconstruction

Reconstruct Excel workbooks from modified CSV files using the structure JSON created during conversion.

```python
# Reconstruct Excel workbook from modified CSV files
excel_path = file_utils.convert_csv_to_excel_workbook(
    structure_json_path=structure_file,
    file_name="reconstructed_workbook"
)

# The method creates:
# - Excel workbook with all sheets
# - Reconstruction metadata JSON
# - Handles missing files gracefully
```

**Reconstruction Features:**
- Uses structure JSON to locate and load CSV files
- Handles missing or modified CSV files gracefully
- Creates reconstruction metadata for audit trail
- Maintains original sheet names and structure

### Configurable Directory Names

Customize directory names to match your project domain and workflow.

#### Basic Configuration

```yaml
# config.yaml
directories:
  data_directory: "documents"  # Main directory name
  subdirectories:
    raw: "product_docs"        # Input directory
    processed: "cs_documents"  # Output directory
    templates: "templates"     # Template directory
```

#### Usage Examples

```python
# Initialize with custom configuration
file_utils = FileUtils(config_file="config.yaml")

# All operations automatically use custom directories
file_utils.save_data_to_storage(data, output_filetype=OutputFileType.CSV, 
                                output_type="raw")  # → documents/product_docs/

file_utils.load_single_file("data.csv", input_type="raw")  # → documents/product_docs/data.csv

# Excel ↔ CSV conversion works seamlessly
csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
    "workbook.xlsx", input_type="raw", output_type="processed"
)
# → documents/product_docs/workbook.xlsx → documents/cs_documents/*.csv
```

#### Domain-Specific Examples

**Document Processing:**
```yaml
directories:
  data_directory: "documents"
  subdirectories:
    raw: "source_docs"
    processed: "ai_processed"
    templates: "templates"
```

**Content Creation:**
```yaml
directories:
  data_directory: "assets"
  subdirectories:
    raw: "source_materials"
    processed: "final_content"
    templates: "brand_templates"
```

**Research Projects:**
```yaml
directories:
  data_directory: "experiments"
  subdirectories:
    raw: "data_collection"
    processed: "analysis_results"
    templates: "report_templates"
```

#### Backward Compatibility

Existing projects continue to work unchanged. The default configuration uses the traditional `data/` directory structure:

```python
# Default behavior (unchanged)
file_utils = FileUtils()
# Uses: project_root/data/raw/ and project_root/data/processed/
```

### JSON Files

JSON files can be used in two ways: as DataFrame storage or as structured documents.

#### JSON as DataFrame Storage
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
```

#### JSON as Structured Documents
```python
# Save structured configuration as JSON document
config_data = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "analytics"
    },
    "api": {
        "timeout": 30,
        "retries": 3,
        "base_url": "https://api.example.com"
    },
    "features": {
        "enable_caching": True,
        "cache_ttl": 3600,
        "max_connections": 100
    }
}

saved_path, _ = file_utils.save_document_to_storage(
    content=config_data,
    output_filetype=OutputFileType.JSON,
    output_type="processed",
    file_name="app_config"
)

# Load configuration
loaded_config = file_utils.load_json(
    file_path="app_config.json",
    input_type="processed"
)

print(f"Database host: {loaded_config['database']['host']}")
```

#### Automatic Type Conversion
```python
import pandas as pd
import numpy as np

# Create data with pandas types
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=5),
    'value': np.random.randn(5),
    'category': ['A', 'B', 'C', 'D', 'E']
})

# This works without manual conversion!
json_data = {
    'metadata': {
        'created': pd.Timestamp.now(),
        'version': '1.0',
        'total_records': len(df)
    },
    'data': df.to_dict('records')  # Pandas Timestamps automatically converted
}

saved_path, _ = file_utils.save_document_to_storage(
    content=json_data,
    output_filetype=OutputFileType.JSON,
    output_type="processed",
    file_name="data_with_types"
)

# Load the data
loaded_data = file_utils.load_json(
    file_path="data_with_types.json",
    input_type="processed"
)

print(f"Created: {loaded_data['metadata']['created']}")  # ISO format string
```

### YAML Files

YAML files can be used in two ways: as DataFrame storage or as structured documents.

#### YAML as DataFrame Storage
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
```

#### YAML as Structured Documents
```python
# Save structured configuration as YAML document
pipeline_config = {
    "project": {
        "name": "Data Analysis Pipeline",
        "version": "2.1.0",
        "description": "Automated data processing and analysis"
    },
    "data_sources": {
        "primary": {
            "type": "database",
            "connection": "postgresql://localhost:5432/analytics",
            "tables": ["users", "transactions", "products"]
        },
        "secondary": {
            "type": "api",
            "url": "https://api.external-service.com",
            "auth": {"type": "bearer", "token": "your-token"}
        }
    },
    "processing": {
        "batch_size": 1000,
        "parallel_workers": 4,
        "retry_attempts": 3,
        "timeout": 300
    },
    "output": {
        "formats": ["csv", "parquet"],
        "compression": "gzip",
        "include_metadata": True
    }
}

saved_path, _ = file_utils.save_document_to_storage(
    content=pipeline_config,
    output_filetype=OutputFileType.YAML,
    output_type="processed",
    file_name="pipeline_config"
)

# Load configuration
loaded_config = file_utils.load_yaml(
    file_path="pipeline_config.yaml",
    input_type="processed"
)

print(f"Project: {loaded_config['project']['name']}")
print(f"Batch size: {loaded_config['processing']['batch_size']}")
```

#### YAML with Automatic Type Conversion
```python
import pandas as pd
from datetime import datetime

# Create configuration with pandas types
config_with_types = {
    "metadata": {
        "created": pd.Timestamp.now(),
        "last_updated": datetime.now(),
        "version": "1.0"
    },
    "data_ranges": {
        "start_date": pd.Timestamp('2024-01-01'),
        "end_date": pd.Timestamp('2024-12-31'),
        "frequency": "daily"
    },
    "settings": {
        "debug": True,
        "log_level": "INFO"
    }
}

saved_path, _ = file_utils.save_document_to_storage(
    content=config_with_types,
    output_filetype=OutputFileType.YAML,
    output_type="processed",
    file_name="config_with_dates"
)

# Load the configuration
loaded_config = file_utils.load_yaml(
    file_path="config_with_dates.yaml",
    input_type="processed"
)

print(f"Created: {loaded_config['metadata']['created']}")  # Properly formatted
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

### PPTX Files
```python
# Save PPTX from bytes
with open("slides.pptx", "rb") as f:
    pptx_bytes = f.read()

saved_path, _ = file_utils.save_document_to_storage(
    content=pptx_bytes,
    output_filetype=OutputFileType.PPTX,
    output_type="processed",
    file_name="quarterly_review",
    sub_path="presentations/2024/Q1"
)

# Or save PPTX from a local file path
saved_path, _ = file_utils.save_document_to_storage(
    content="/absolute/path/to/slides.pptx",
    output_filetype=OutputFileType.PPTX,
    output_type="processed",
    file_name="quarterly_review",
    sub_path="presentations/2024/Q1"
)

# Load PPTX (returns bytes)
pptx_bytes = file_utils.load_document_from_storage(
    file_path="quarterly_review.pptx",
    input_type="processed",
    sub_path="presentations/2024/Q1"
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
PPTX support operates on raw files and does not require additional dependencies.

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

## Troubleshooting

### Common Issues and Solutions

#### JSON Serialization Errors

**Problem**: `TypeError: Object of type Timestamp is not JSON serializable`

**Solution**: Use `save_document_to_storage()` instead of manual JSON serialization:

```python
# ❌ This will fail
import json
data = {'date': pd.Timestamp.now()}
json.dumps(data)  # TypeError

# ✅ This works automatically
saved_path, _ = file_utils.save_document_to_storage(
    content=data,
    output_filetype=OutputFileType.JSON,
    output_type="processed",
    file_name="data"
)
```

#### Missing Document Dependencies

**Problem**: `ModuleNotFoundError: No module named 'docx'` or `ModuleNotFoundError: No module named 'fitz'`

**Solution**: Install document dependencies:

```bash
# Install all document support
pip install 'FileUtils[documents]'

# Or install specific dependencies
pip install python-docx markdown PyMuPDF
```

#### File Not Found with Timestamps

**Problem**: `FileNotFoundError` when loading files saved with timestamps

**Solution**: Use base filename - FileUtils automatically finds timestamped files:

```python
# Save with timestamp (creates: report_20241018_143022.json)
saved_path, _ = file_utils.save_document_to_storage(
    content=content,
    output_filetype=OutputFileType.JSON,
    file_name="report"
)

# Load by base name (automatically finds the timestamped file)
loaded_data = file_utils.load_json(
    file_path="report.json",  # Not "report_20241018_143022.json"
    input_type="processed"
)
```

#### MultiIndex DataFrame Issues

**Problem**: `NotImplementedError: Writing to Excel with MultiIndex columns and no index`

**Solution**: FileUtils automatically handles MultiIndex columns by flattening them:

```python
# FileUtils automatically flattens MultiIndex columns
df_with_multiindex = pd.DataFrame({
    ('A', 'x'): [1, 2, 3],
    ('A', 'y'): [4, 5, 6],
    ('B', 'z'): [7, 8, 9]
})

# This works automatically
saved_files, metadata = file_utils.save_data_to_storage(
    data={'data': df_with_multiindex},
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multiindex_data"
)
```

#### Azure Storage Connection Issues

**Problem**: `StorageConnectionError` when using Azure storage

**Solution**: Check your connection string and credentials:

```python
from FileUtils.core.base import StorageConnectionError

try:
    azure_utils = FileUtils(
        storage_type="azure",
        connection_string="your_connection_string"
    )
except StorageConnectionError as e:
    print(f"Azure connection failed: {e}")
    # Fall back to local storage
    file_utils = FileUtils(storage_type="local")
```

#### Configuration Issues

**Problem**: Configuration not loading or validation errors

**Solution**: Check your configuration file format:

```python
# Validate configuration
try:
    file_utils = FileUtils(config_file="config.yaml")
except Exception as e:
    print(f"Configuration error: {e}")
    # Use default configuration
    file_utils = FileUtils()
```

### Performance Tips

#### Large File Handling

For large files, consider these optimizations:

```python
# Use Parquet for large datasets
file_utils.save_data_to_storage(
    data=large_df,
    output_filetype=OutputFileType.PARQUET,
    compression="snappy"  # Fast compression
)

# Use chunked processing for very large files
chunk_size = 10000
for i, chunk in enumerate(pd.read_csv("large_file.csv", chunksize=chunk_size)):
    file_utils.save_data_to_storage(
        data={'chunk': chunk},
        output_filetype=OutputFileType.PARQUET,
        file_name=f"chunk_{i:04d}"
    )
```

#### Memory Optimization

```python
# For large DataFrames, use appropriate data types
df = df.astype({
    'category': 'category',  # Reduces memory usage
    'id': 'int32',           # Instead of int64
    'price': 'float32'       # Instead of float64
})
```