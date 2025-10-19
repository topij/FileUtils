# FileUtils

A Python utility package for consistent file operations across local and Azure storage, with enhanced support for various data formats and flexible configuration options.

## Features

- **Unified Storage Interface**
  - Seamless operations across local and Azure Blob Storage
  - Consistent API regardless of storage backend
  - Automatic directory structure management

- **Comprehensive File Format Support**
  - **Tabular Data**: CSV (with delimiter auto-detection), Excel (.xlsx, .xls) with multi-sheet support, Parquet (with compression options)
  - **Document Formats**: Microsoft Word (.docx) with template support, Markdown (.md) with YAML frontmatter, PDF (read-only text extraction)
  - **Multi-Purpose Formats**: JSON and YAML support both DataFrame storage and structured document handling with automatic pandas type conversion

- **Advanced Data Handling**
  - Single and multi-DataFrame operations
  - Automatic format detection
  - Flexible data orientation options
  - Customizable save/load options per format
  - `Dynamic Subdirectory Creation`: Specify nested subdirectories for saving files on the fly using the `sub_path` parameter.
  - `File Format Handling`: Loads data based on file extension; includes CSV delimiter auto-detection during load.

- **Robust Infrastructure**
  - YAML-based configuration system
  - Comprehensive error handling
  - Detailed logging with configurable levels
  - Type hints throughout the codebase

## Installation

<!-- Choose the installation option that best suits your needs:

```bash
# Basic installation (local storage only)
pip install FileUtils

# Install with Azure support
pip install 'FileUtils[azure]'

# Install with Parquet support
pip install 'FileUtils[parquet]'

# Install with Excel support
pip install 'FileUtils[excel]'

# Install with all optional dependencies
pip install 'FileUtils[all]'
```-->

You can install directly from GitHub and choose the installation option that best suits your needs:
```bash
# Basic installation
pip install git+https://github.com/topij/FileUtils.git

# With specific features
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[azure]'
pip install 'git+https://github.com/topij/FileUtils.git#egg=FileUtils[all]'
```

## Quick Start

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with local storage
file_utils = FileUtils()

# Load data (format is auto-detected)
df = file_utils.load_single_file("data.csv", input_type="raw")

# Save as JSON with custom options
file_utils.save_data_to_storage(
    data=df,
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.JSON,
    orient="records",  # Save as list of records
)

# Save multiple DataFrames to Excel
data_dict = {
    "Sheet1": df1,
    "Sheet2": df2
}
file_utils.save_data_to_storage(
    data=data_dict,
    file_name="multi_sheet",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)

# Save to a dynamic subdirectory
file_utils.save_data_to_storage(
    data=df,
    file_name="report_data",
    output_type="processed",
    output_filetype=OutputFileType.CSV,
    sub_path="analysis_run_1/summaries" # New subdirectory
)
# File saved to: data/processed/analysis_run_1/summaries/report_data_<timestamp>.csv

# Load data from the dynamic subdirectory
loaded_report = file_utils.load_single_file(
    file_path="report_data.csv", # Just the filename
    input_type="processed",
    sub_path="analysis_run_1/summaries" # Specify the sub_path
)
```

## Document Handling

FileUtils now supports rich document formats perfect for AI/agentic workflows:

```python
from FileUtils import FileUtils, OutputFileType

# Initialize FileUtils
file_utils = FileUtils()

# Save Markdown with YAML frontmatter
document_content = {
    "frontmatter": {
        "title": "AI Analysis Report",
        "author": "AI Agent",
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
    content=document_content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="ai_analysis",
    sub_path="reports/2024"
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

# Save structured DOCX document
docx_content = {
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
                ["Metric", "Value"],
                ["Accuracy", "95.2%"],
                ["Speed", "2.3s"]
            ]
        }
    ]
}

saved_path, _ = file_utils.save_document_to_storage(
    content=docx_content,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="project_report"
)

# Load document content
loaded_content = file_utils.load_document_from_storage(
    file_path="ai_analysis.md",
    input_type="processed",
    sub_path="reports/2024"
)

# Save structured JSON configuration
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
        "cache_ttl": 3600
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

# Automatic type conversion for pandas data
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=5),
    'value': np.random.randn(5),
    'category': ['A', 'B', 'C', 'D', 'E']
})

# This works without manual conversion!
json_data = {
    'metadata': {
        'created': pd.Timestamp.now(),
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
```

## Enhanced DOCX Template System

FileUtils includes a comprehensive DOCX template system with:

- **Template Support**: Use existing DOCX files with custom styles (not .dotx template files)
- **Markdown Conversion**: Convert markdown content to professionally formatted DOCX
- **Style Mapping**: Customize how elements are styled in the output
- **Reviewer Workflow**: Built-in support for document review processes
- **Provenance Tracking**: Automatic metadata and source tracking

**Important**: FileUtils uses regular `.docx` files as templates, not Microsoft Word `.dotx` template files. The system loads the DOCX file, clears its content, and preserves the styles for use in the generated documents.

```python
# Initialize with template configuration
file_utils = FileUtils(
    config_override={
        "docx_templates": {
            "template_dir": "templates",
            "templates": {
                "default": "style-template-doc.docx",  # Generic template
                "personal": "IP-template-doc.docx"      # Personal template
            }
        },
        "style_mapping": {
            "table": "IP-table_light",
            "heading_1": "Heading 1"
        }
    }
)

# Convert markdown to DOCX with template
file_utils.save_document_to_storage(
    content=markdown_content,
    output_filetype=OutputFileType.DOCX,
    template="review",
    add_provenance=True,
    add_reviewer_instructions=True
)
```

For detailed DOCX template documentation, see [Enhanced DOCX Guide](docs/ENHANCED_DOCX.md).

## Examples

FileUtils includes comprehensive example scripts demonstrating various use cases:

### Quick Examples
```bash
# Run example scripts
python examples/data_pipeline.py      # Complete data pipeline
python examples/ai_workflow.py         # AI/agentic workflows  
python examples/multi_format_reports.py # Multi-format reporting
python examples/enhanced_docx.py       # Enhanced DOCX template system
python examples/error_handling.py      # Robust error handling
python examples/performance_optimization.py # Large dataset optimization
```

### Example Scripts Overview
- **`basic_usage.py`** - Basic operations (CSV, Excel, metadata)
- **`data_pipeline.py`** - Complete data science pipeline (7,000+ records)
- **`ai_workflow.py`** - AI integration (sentiment analysis, recommendations)
- **`enhanced_docx.py`** - Enhanced DOCX template system (markdown conversion, templates)
- **`multi_format_reports.py`** - Same data → Excel, PDF, Markdown, JSON
- **`error_handling.py`** - Production-ready error handling and recovery
- **`performance_optimization.py`** - Large dataset optimization (50MB+)
- **`document_types.py`** - Document functionality (DOCX, Markdown, PDF)
- **`configuration.py`** - Configuration options and customization
- **`azure_storage.py`** - Azure Blob Storage integration
- **`FileUtils_tutorial.ipynb`** - Comprehensive interactive tutorial

📚 **[Complete Examples Documentation](docs/EXAMPLES.md)** - Detailed guide to all example scripts

## Key Benefits

- **Consistency**: Same interface for local and cloud storage operations
- **Flexibility**: Extensive options for each file format
- **Reliability**: Robust error handling and logging
- **Simplicity**: Intuitive API with sensible defaults
- **Smart Type Handling**: Automatic conversion of pandas types for JSON/YAML documents
- **Intelligent File Discovery**: Automatic handling of timestamped files when loading

## Background

This package was developed to streamline data operations across various projects, particularly in data science and analysis workflows. It eliminates the need to rewrite common file handling code and provides a consistent interface regardless of the storage backend.

For a practical example, check out my [semantic text analyzer](https://www.github.com/topij/text-analyzer) project, which uses FileUtils for seamless data handling across local and Azure environments.

## Documentation

- [Getting Started Guide](docs/GETTING_STARTED_GUIDE.md) - Quick introduction to key use cases
- [Installation Guide](docs/INSTALLATION.md) - Detailed installation instructions
- [Usage Guide](docs/USAGE.md) - Comprehensive examples and patterns
- [Document Types Guide](docs/DOCUMENT_TYPES.md) - Rich document formats (DOCX, Markdown, PDF)
- [Enhanced DOCX Guide](docs/ENHANCED_DOCX.md) - DOCX template system and markdown conversion
- [Examples Documentation](docs/EXAMPLES.md) - Complete guide to all example scripts
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Azure Setup Guide](docs/AZURE_SETUP.md) - Azure Blob Storage configuration
- [Development Guide](docs/DEVELOPMENT.md) - Setup, building, and contributing to the project
- [Future Features](docs/FUTURE_FEATURES.md) - Roadmap and planned enhancements

## Requirements

### Core Dependencies (automatically installed)
- Python 3.9+
- pandas
- pyyaml
- python-dotenv
- jsonschema

### Optional Dependencies
Choose the dependencies you need based on your use case:

- **Azure Storage** (`[azure]`):
  - azure-storage-blob
  - azure-identity
- **Parquet Support** (`[parquet]`):
  - pyarrow
- **Excel Support** (`[excel]`):
  - openpyxl
- **Document Formats** (`[documents]`):
  - python-docx (Microsoft Word documents)
  - markdown (Markdown processing)
  - PyMuPDF (PDF read/write, supports multiple formats)

Install optional dependencies using the corresponding extras tag (e.g., `pip install 'FileUtils[documents]'`).

## Notes from the Author

This package prioritizes functionality and ease of use over performance optimization. While I use it in all of my projects, it's maintained as a side project. 

## License

MIT License
