# FileUtils Examples

This directory contains comprehensive example scripts demonstrating FileUtils capabilities across various use cases and complexity levels.

## 🚀 Quick Start

```bash
# Install FileUtils with all features
pip install "FileUtils[all]"

# Run any example
python data_pipeline.py
python ai_workflow.py
python multi_format_reports.py
```

## 📁 Example Scripts

| **Script** | **Purpose** | **Level** | **Duration** |
|------------|-------------|-----------|--------------|
| [`basic_usage.py`](basic_usage.py) | Basic operations | Beginner | ~30s |
| [`data_pipeline.py`](data_pipeline.py) | Complete data pipeline | Intermediate | ~2-3min |
| [`ai_workflow.py`](ai_workflow.py) | AI/agentic workflows | Intermediate | ~1-2min |
| [`multi_format_reports.py`](multi_format_reports.py) | Multi-format reporting | Intermediate | ~1-2min |
| [`error_handling.py`](error_handling.py) | Robust error handling | Advanced | ~1-2min |
| [`performance_optimization.py`](performance_optimization.py) | Large dataset optimization | Advanced | ~3-5min |
| [`document_types.py`](document_types.py) | Document functionality | Beginner | ~1min |
| [`configuration.py`](configuration.py) | Configuration options | Beginner | ~30s |
| [`azure_storage.py`](azure_storage.py) | Azure integration | Intermediate | ~1-2min |
| [`FileUtils_tutorial.ipynb`](FileUtils_tutorial.ipynb) | Comprehensive tutorial | All levels | ~30-60min |

## 🎯 Choose Your Example

### **Beginners**
Start with: `basic_usage.py` → `document_types.py` → `configuration.py`

### **Data Scientists**
Start with: `data_pipeline.py` → `multi_format_reports.py`

### **AI/ML Engineers**
Start with: `ai_workflow.py` → `data_pipeline.py`

### **Production Deployment**
Start with: `error_handling.py` → `performance_optimization.py`

### **Cloud Integration**
Start with: `azure_storage.py` → `configuration.py`

## 📚 Documentation

- **[Complete Examples Documentation](../docs/EXAMPLES.md)** - Detailed documentation for all examples
- **[API Reference](../docs/API_REFERENCE.md)** - Complete API documentation
- **[Usage Guide](../docs/USAGE.md)** - General usage patterns
- **[Installation Guide](../docs/INSTALLATION.md)** - Setup instructions

## 🔧 Prerequisites

### Basic Examples
```bash
pip install "FileUtils[documents]"
```

### Azure Examples
```bash
pip install "FileUtils[azure]"
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

### All Features
```bash
pip install "FileUtils[all]"
```

## 🏃‍♂️ Running Examples

### Individual Scripts
```bash
python basic_usage.py
python data_pipeline.py
python ai_workflow.py
```

### Batch Run All
```bash
for script in *.py; do
    echo "Running $script..."
    python "$script"
    echo "Completed $script"
    echo "---"
done
```

### Jupyter Notebook
```bash
jupyter notebook FileUtils_tutorial.ipynb
```

## 📊 What Each Example Demonstrates

### **Basic Usage** (`basic_usage.py`)
- CSV and Excel file operations
- Multi-sheet Excel generation
- Metadata management
- Simple data workflows

### **Data Pipeline** (`data_pipeline.py`)
- Complete data science pipeline
- Data generation and processing
- Analysis and reporting
- Configuration management
- **Output**: 7,000+ records processed, 4 analysis sheets, insights document

### **AI Workflow** (`ai_workflow.py`)
- AI analysis simulation
- Sentiment analysis and recommendations
- Multi-format AI outputs
- API response generation
- Model configuration
- **Output**: 100 sentiment records, 292 recommendations, 4 output files

### **Multi-Format Reports** (`multi_format_reports.py`)
- Same data → Multiple formats
- Excel, PDF, Markdown, JSON outputs
- Comprehensive reporting
- **Output**: 4 different format reports from same data

### **Error Handling** (`error_handling.py`)
- Robust retry logic
- Data validation and cleaning
- Fallback strategies
- Error reporting
- **Output**: Error reports, recovery configurations

### **Performance Optimization** (`performance_optimization.py`)
- Large dataset processing (50MB+)
- Memory optimization techniques
- Chunked processing
- Performance monitoring
- **Output**: 500,000+ records, 25MB memory savings, performance reports

### **Document Types** (`document_types.py`)
- DOCX document generation
- Markdown with YAML frontmatter
- PDF document creation
- Structured content handling

### **Configuration** (`configuration.py`)
- Custom configuration files
- Directory structure customization
- Storage settings
- Azure configuration

### **Azure Storage** (`azure_storage.py`)
- Azure Blob Storage integration
- Cloud file operations
- Container management
- Azure authentication

### **Tutorial Notebook** (`FileUtils_tutorial.ipynb`)
- Interactive learning
- All features covered
- Step-by-step examples
- Best practices

## 🎨 Customization

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

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# If you get "ModuleNotFoundError: No module named 'FileUtils'"
pip install "FileUtils[all]"
```

**Azure Errors**
```bash
# Set Azure connection string
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

**Memory Issues**
```bash
# Reduce dataset size in performance example
large_data = generate_large_dataset(size_mb=10)  # 10MB instead of 50MB
```

## 📈 Example Outputs

After running examples, you'll find generated files in:
- `data/raw/` - Raw data files
- `data/processed/` - Processed data and reports
- `data/processed/reports/` - Generated reports
- `data/processed/config/` - Configuration files

## 🤝 Contributing

Want to add your own example?

1. Create a new script following the naming convention
2. Include comprehensive documentation
3. Add error handling and logging
4. Test thoroughly
5. Update documentation

See the [main examples documentation](../docs/EXAMPLES.md) for detailed guidelines.

---

**Ready to get started?** Choose an example that matches your use case and run it! 🚀
