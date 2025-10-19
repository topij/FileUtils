# FileUtils Examples Documentation

This document provides comprehensive documentation for all FileUtils example scripts, including use cases, features, and running instructions.

## 📁 Example Scripts Overview

FileUtils includes a comprehensive collection of example scripts that demonstrate various use cases and best practices:

| **Script** | **Purpose** | **Complexity** | **Key Features** |
|------------|-------------|----------------|------------------|
| [`basic_usage.py`](#basic-usage) | Basic operations | Beginner | CSV, Excel, metadata |
| [`data_pipeline.py`](#data-pipeline) | Complete data pipeline | Intermediate | End-to-end processing |
| [`ai_workflow.py`](#ai-workflow) | AI/agentic workflows | Intermediate | AI integration, multi-format |
| [`enhanced_docx.py`](#enhanced-docx) | Enhanced DOCX template system | Intermediate | Template support, markdown conversion |
| [`multi_format_reports.py`](#multi-format-reports) | Multi-format reporting | Intermediate | Excel, PDF, Markdown, JSON |
| [`error_handling.py`](#error-handling) | Robust error handling | Advanced | Retry logic, fallbacks |
| [`performance_optimization.py`](#performance-optimization) | Large dataset optimization | Advanced | Memory management, chunking |
| [`document_types.py`](#document-types) | Document functionality | Beginner | DOCX, Markdown, PDF |
| [`configuration.py`](#configuration) | Configuration options | Beginner | Custom configs, settings |
| [`azure_storage.py`](#azure-storage) | Azure integration | Intermediate | Cloud storage, Azure Blob |
| [`FileUtils_tutorial.ipynb`](#tutorial-notebook) | Comprehensive tutorial | All levels | Interactive learning |

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install FileUtils with all features
pip install "FileUtils[all]"

# Or install specific features
pip install "FileUtils[documents]"  # For document support
pip install "FileUtils[azure]"      # For Azure support
```

### Running Examples

```bash
# Navigate to examples directory
cd examples/

# Run any example script
python data_pipeline.py
python ai_workflow.py
python multi_format_reports.py
python enhanced_docx.py
```

---

## 📋 Detailed Examples

### Basic Usage

**File**: `basic_usage.py`  
**Level**: Beginner  
**Duration**: ~30 seconds  

#### Purpose
Demonstrates fundamental FileUtils operations including saving DataFrames, working with Excel files, and metadata management.

#### Key Features
- ✅ Single DataFrame saving (CSV, Excel)
- ✅ Multi-sheet Excel files
- ✅ Metadata generation and loading
- ✅ Basic data operations

#### What It Does
1. Creates sample data with names, ages, and cities
2. Saves data as CSV and Excel formats
3. Creates multi-sheet Excel with summary statistics
4. Demonstrates metadata saving and loading

#### Sample Output
```
Saved CSV file: {'Sheet1': '/path/to/sample_data.csv'}
Saved Excel file: {'Sheet1': '/path/to/sample_data.xlsx'}
Saved multi-sheet Excel file with metadata: {'original': '/path/to/multi_sheet_data.xlsx', ...}
```

#### Use Cases
- Learning FileUtils basics
- Simple data export workflows
- Multi-sheet Excel generation
- Metadata tracking

---

### Data Pipeline

**File**: `data_pipeline.py`  
**Level**: Intermediate  
**Duration**: ~2-3 minutes  

#### Purpose
Demonstrates a complete data science pipeline from raw data generation through analysis to report generation.

#### Key Features
- ✅ Realistic sales data generation
- ✅ Data cleaning and feature engineering
- ✅ Multi-sheet analysis reports
- ✅ Automated insights generation
- ✅ Configuration management

#### What It Does
1. **Data Generation**: Creates 7,000+ sales records with seasonal patterns
2. **Data Processing**: Cleans outliers, adds features (revenue, quarters, etc.)
3. **Analysis**: Generates 4 analysis sheets (summary, trends, regional, top products)
4. **Insights**: Creates comprehensive Markdown report with key metrics
5. **Configuration**: Saves pipeline configuration as JSON

#### Sample Output
```
=== Data Pipeline with FileUtils ===
✓ Processed 7,266 records
✓ Generated 4 analysis sheets
✓ Created insights document
✓ Saved configuration summary
```

#### Use Cases
- Complete data science workflows
- Sales analysis pipelines
- Automated report generation
- Data processing automation

#### Generated Files
- `sales_data_2024_*.parquet` - Raw data
- `sales_data_cleaned_*.parquet` - Processed data
- `sales_analysis_report_*.xlsx` - Analysis results
- `sales_insights_*.md` - Insights document
- `pipeline_config_*.json` - Configuration

---

### Enhanced DOCX Template System

**File**: `enhanced_docx.py`  
**Level**: Intermediate  
**Duration**: ~1-2 minutes  

#### Purpose
Demonstrates the enhanced DOCX template system with markdown conversion, template support, and customizable styling.

#### Key Features
- ✅ Template support with custom styles
- ✅ Markdown to DOCX conversion
- ✅ Style mapping and fallbacks
- ✅ Reviewer workflow support
- ✅ Provenance tracking
- ✅ Template management utilities

#### What It Does
1. **Template Configuration**: Sets up template system with custom styles
2. **Markdown Conversion**: Converts markdown content to professionally formatted DOCX
3. **Structured Content**: Creates DOCX documents with headings, tables, and formatting
4. **Template Management**: Demonstrates template listing and validation
5. **Configuration Options**: Shows custom template and style configuration

#### Sample Output
```
=== Enhanced DOCX Template System Demo ===
✓ Markdown converted to DOCX: /path/to/project_report.docx
✓ Structured DOCX created: /path/to/technical_spec.docx
✓ Simple DOCX created: /path/to/simple_doc.docx
✓ Template management: Available templates listed
```

#### Use Cases
- Document generation with templates
- Markdown to DOCX conversion
- Professional document formatting
- Review workflow automation
- Template management and validation

#### Generated Files
- `project_report_*.docx` - Markdown converted with template
- `technical_spec_*.docx` - Structured content with template
- `simple_doc_*.docx` - Basic DOCX document

---

### AI Workflow

**File**: `ai_workflow.py`  
**Level**: Intermediate  
**Duration**: ~1-2 minutes  

#### Purpose
Demonstrates FileUtils integration in AI/agentic workflows with structured data processing and multi-format outputs.

#### Key Features
- ✅ AI analysis simulation (sentiment, recommendations)
- ✅ Structured document generation
- ✅ API response formatting
- ✅ Model configuration management
- ✅ Multi-format outputs

#### What It Does
1. **AI Analysis**: Simulates sentiment analysis and recommendation engine
2. **Document Generation**: Creates comprehensive AI insights report
3. **API Integration**: Generates JSON API response format
4. **Model Management**: Saves AI model configurations
5. **Summary Reporting**: Creates workflow summary

#### Sample Output
```
=== AI/Agentic Workflow with FileUtils ===
✓ Processed 100 sentiment records
✓ Generated 292 recommendations
✓ Created 4 output files
✓ Generated insights document
✓ Saved API response format
```

#### Use Cases
- AI/ML pipeline integration
- Sentiment analysis workflows
- Recommendation systems
- API response generation
- Model configuration management

#### Generated Files
- `ai_analysis_results_*.xlsx` - Analysis results
- `ai_insights_report_*.md` - Insights document
- `ai_api_response_*.json` - API response
- `ai_model_config_*.yaml` - Model configuration
- `workflow_summary_*.json` - Summary report

---

### Multi-Format Reports

**File**: `multi_format_reports.py`  
**Level**: Intermediate  
**Duration**: ~1-2 minutes  

#### Purpose
Demonstrates generating comprehensive reports in multiple formats from the same dataset.

#### Key Features
- ✅ Same data → Multiple formats
- ✅ Excel multi-sheet reports
- ✅ PDF executive summaries
- ✅ Markdown comprehensive reports
- ✅ JSON API responses

#### What It Does
1. **Data Generation**: Creates quarterly sales data
2. **Multi-Format Generation**: 
   - Excel with 4 analysis sheets
   - PDF executive summary
   - Markdown comprehensive report
   - JSON API response
3. **Configuration**: Saves report generation settings

#### Sample Output
```
=== Multi-Format Report Generation ===
✓ Generated Excel report with 4 sheets
✓ Created comprehensive Markdown report
✓ Generated JSON API response
✓ Created PDF executive summary
✓ Saved report configuration
```

#### Use Cases
- Multi-stakeholder reporting
- Format-specific deliverables
- API integration
- Executive summaries
- Comprehensive documentation

#### Generated Files
- `quarterly_report_*.xlsx` - Excel analysis
- `quarterly_report_*.md` - Markdown report
- `quarterly_report_api_*.json` - JSON API
- `quarterly_report_*.pdf` - PDF summary
- `report_config_*.yaml` - Configuration

---

### Error Handling

**File**: `error_handling.py`  
**Level**: Advanced  
**Duration**: ~1-2 minutes  

#### Purpose
Demonstrates robust error handling and recovery strategies for production environments.

#### Key Features
- ✅ Retry logic with exponential backoff
- ✅ Data validation and cleaning
- ✅ Format fallback strategies
- ✅ Comprehensive error reporting
- ✅ Recovery configuration

#### What It Does
1. **Simulated Failures**: Tests various failure scenarios
2. **Retry Logic**: Implements robust retry mechanisms
3. **Data Validation**: Cleans corrupted/incomplete data
4. **Fallback Strategies**: Uses alternative formats when needed
5. **Error Reporting**: Generates comprehensive error reports

#### Sample Output
```
=== Error Handling and Recovery Demo ===
✓ Processed 100 records
✓ Encountered 2 errors/warnings
✓ Used parquet format
✓ Error handling: Successful
✓ Recovery mechanisms: Activated
```

#### Use Cases
- Production deployment
- Robust data processing
- Error monitoring
- Recovery strategies
- Quality assurance

#### Generated Files
- `robust_data_*.parquet` - Processed data
- `error_report_*.md` - Error documentation
- `recovery_config_*.yaml` - Recovery settings

---

### Performance Optimization

**File**: `performance_optimization.py`  
**Level**: Advanced  
**Duration**: ~3-5 minutes  

#### Purpose
Demonstrates performance optimization techniques for large datasets.

#### Key Features
- ✅ Large dataset generation (50MB+)
- ✅ Memory optimization techniques
- ✅ Chunked processing
- ✅ Performance monitoring
- ✅ Memory cleanup

#### What It Does
1. **Large Dataset**: Generates 50MB dataset (500K+ records)
2. **Memory Optimization**: Converts data types for efficiency
3. **Chunked Processing**: Processes data in manageable chunks
4. **Performance Monitoring**: Tracks memory and time usage
5. **Cleanup**: Demonstrates proper memory management

#### Sample Output
```
=== Performance Optimization Demo ===
✓ Processed 500,000 records
✓ Saved 25.3MB memory (45.2%)
✓ Total processing time: 12.45 seconds
✓ Memory cleanup: 150.2MB freed
✓ Performance report generated
```

#### Use Cases
- Large dataset processing
- Memory optimization
- Performance tuning
- Scalability planning
- Resource management

#### Generated Files
- `large_dataset_optimized_*.parquet` - Optimized data
- `performance_report_*.md` - Performance analysis
- `performance_config_*.yaml` - Optimization settings

---

### Document Types

**File**: `document_types.py`  
**Level**: Beginner  
**Duration**: ~1 minute  

#### Purpose
Demonstrates FileUtils' document functionality including DOCX, Markdown, and PDF generation.

#### Key Features
- ✅ Markdown with YAML frontmatter
- ✅ DOCX document generation
- ✅ PDF document creation
- ✅ Structured content handling

#### What It Does
1. **Markdown**: Creates simple and structured Markdown documents
2. **DOCX**: Generates Word documents with formatting
3. **PDF**: Creates PDF documents from text content
4. **Structured Content**: Demonstrates rich content handling

#### Use Cases
- Document generation
- Report creation
- Content management
- Multi-format documentation

---

### Configuration

**File**: `configuration.py`  
**Level**: Beginner  
**Duration**: ~30 seconds  

#### Purpose
Demonstrates FileUtils configuration options and customization.

#### Key Features
- ✅ Custom configuration files
- ✅ Directory structure customization
- ✅ Storage settings
- ✅ Azure configuration

#### What It Does
1. **Custom Config**: Creates YAML configuration file
2. **Directory Structure**: Defines custom directory layout
3. **Storage Settings**: Configures storage options
4. **Azure Setup**: Demonstrates Azure configuration

#### Use Cases
- Custom project setup
- Configuration management
- Environment-specific settings
- Azure integration setup

---

### Azure Storage

**File**: `azure_storage.py`  
**Level**: Intermediate  
**Duration**: ~1-2 minutes (requires Azure setup)  

#### Purpose
Demonstrates FileUtils integration with Azure Blob Storage.

#### Key Features
- ✅ Azure Blob Storage integration
- ✅ Cloud file operations
- ✅ Azure authentication
- ✅ Container management

#### Prerequisites
```bash
# Set Azure connection string
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

#### What It Does
1. **Azure Setup**: Configures Azure storage connection
2. **File Operations**: Demonstrates cloud file operations
3. **Container Management**: Shows container creation/management
4. **Error Handling**: Handles Azure-specific errors

#### Use Cases
- Cloud storage integration
- Azure-based workflows
- Distributed data processing
- Cloud-native applications

---

### Tutorial Notebook

**File**: `FileUtils_tutorial.ipynb`  
**Level**: All levels  
**Duration**: ~30-60 minutes  

#### Purpose
Comprehensive interactive tutorial covering all FileUtils features.

#### Key Features
- ✅ Interactive learning
- ✅ Step-by-step examples
- ✅ All features covered
- ✅ Best practices
- ✅ Troubleshooting

#### What It Covers
1. **Installation and Setup**
2. **Basic File Operations**
3. **Working with Different File Formats**
4. **Document Handling**
5. **Metadata Management**
6. **Azure Storage Integration**
7. **Advanced Configuration**

#### Use Cases
- Learning FileUtils
- Comprehensive feature overview
- Interactive experimentation
- Best practice learning

---

## 🛠️ Running Examples

### Individual Scripts

```bash
# Basic usage
python basic_usage.py

# Data pipeline
python data_pipeline.py

# AI workflow
python ai_workflow.py

# Multi-format reports
python multi_format_reports.py

# Enhanced DOCX template system
python enhanced_docx.py

# Error handling
python error_handling.py

# Performance optimization
python performance_optimization.py

# Document types
python document_types.py

# Configuration
python configuration.py

# Azure storage (requires setup)
python azure_storage.py
```

### Batch Running

```bash
# Run all examples
for script in *.py; do
    echo "Running $script..."
    python "$script"
    echo "Completed $script"
    echo "---"
done
```

### Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook FileUtils_tutorial.ipynb
```

---

## 📊 Example Comparison

| **Feature** | **Basic** | **Pipeline** | **AI** | **Enhanced DOCX** | **Multi-Format** | **Error Handling** | **Performance** |
|-------------|-----------|---------------|--------|-------------------|------------------|-------------------|-----------------|
| **Data Generation** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multiple Formats** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Template Support** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Markdown Conversion** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Error Handling** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Performance Focus** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **AI Integration** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Large Datasets** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Production Ready** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 Choosing the Right Example

### For Document Generation
- **Start with**: `enhanced_docx.py`
- **Then try**: `document_types.py`
- **Learn**: Template support, markdown conversion, document formatting

### For Data Scientists
- **Start with**: `data_pipeline.py`
- **Then try**: `multi_format_reports.py`
- **Learn**: End-to-end workflows, reporting

### For AI/ML Engineers
- **Start with**: `ai_workflow.py`
- **Then try**: `data_pipeline.py`
- **Learn**: AI integration, structured outputs

### For Production Deployment
- **Start with**: `error_handling.py`
- **Then try**: `performance_optimization.py`
- **Learn**: Robust error handling, optimization

### For Cloud Integration
- **Start with**: `azure_storage.py`
- **Then try**: `configuration.py`
- **Learn**: Cloud storage, configuration

---

## 🔧 Customization

### Modifying Examples

All examples are designed to be easily customizable:

```python
# Change data size
large_data = generate_large_dataset(size_mb=100)  # 100MB instead of 50MB

# Modify output formats
saved_files, _ = file_utils.save_data_to_storage(
    data=data,
    output_filetype=OutputFileType.PARQUET,  # Change format
    output_type="processed",
    file_name="custom_name",  # Change filename
    include_timestamp=False  # Disable timestamps
)

# Custom subdirectories
saved_path, _ = file_utils.save_document_to_storage(
    content=content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="report",
    sub_path="custom/reports"  # Custom subdirectory
)
```

### Environment Variables

```bash
# Azure configuration
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"

# Custom project root
export FILEUTILS_PROJECT_ROOT="/path/to/your/project"

# Logging level
export FILEUTILS_LOG_LEVEL="DEBUG"
```

---

## 🐛 Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get "ModuleNotFoundError: No module named 'FileUtils'"
# Make sure you're in the examples directory and FileUtils is installed
pip install "FileUtils[all]"
```

#### Azure Errors
```bash
# If Azure examples fail
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
# Or skip Azure examples if not needed
```

#### Memory Issues
```bash
# If performance optimization example fails
# Reduce dataset size in the script
large_data = generate_large_dataset(size_mb=10)  # 10MB instead of 50MB
```

#### Permission Errors
```bash
# If you get permission errors
chmod +x *.py
# Or run with appropriate permissions
```

### Getting Help

1. **Check the logs**: All examples include detailed logging
2. **Review error messages**: Examples include comprehensive error handling
3. **Check dependencies**: Ensure all required packages are installed
4. **Verify configuration**: Check Azure credentials and file permissions

---

## 📚 Additional Resources

- **Main Documentation**: See `docs/` directory
- **API Reference**: `docs/API_REFERENCE.md`
- **Installation Guide**: `docs/INSTALLATION.md`
- **Usage Guide**: `docs/USAGE.md`
- **Document Types**: `docs/DOCUMENT_TYPES.md`

---

## 🤝 Contributing

Want to add your own example? Here's how:

1. **Create a new script** in the `examples/` directory
2. **Follow the naming convention**: `descriptive_name.py`
3. **Include comprehensive documentation** in the script
4. **Add error handling** and logging
5. **Test thoroughly** before submitting
6. **Update this documentation** with your example

### Example Template

```python
"""Example: Your Example Name

Brief description of what this example demonstrates.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from FileUtils import FileUtils, OutputFileType

def your_example_function():
    """Your example function."""
    print("=== Your Example Name ===")
    
    # Initialize FileUtils
    file_utils = FileUtils()
    
    # Your example code here
    
    print("=== Example Complete ===")

if __name__ == "__main__":
    your_example_function()
```

---

*This documentation covers all FileUtils examples. For questions or contributions, please refer to the main project documentation.*
