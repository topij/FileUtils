# Document Types Guide

This guide covers FileUtils' support for rich document formats, perfect for AI/agentic workflows and content management.

## Overview

FileUtils now supports three document formats alongside traditional tabular data:

- **Markdown (.md)**: Text-based documents with YAML frontmatter support
- **Microsoft Word (.docx)**: Structured documents with headings, text, and tables
- **PDF (.pdf)**: Text documents with basic formatting (read-only extraction)

## Document vs. Tabular Data

FileUtils maintains a clear separation between data types:

- **Tabular Data**: Use `save_data_to_storage()` and `load_single_file()` for DataFrames
- **Document Data**: Use `save_document_to_storage()` and `load_document_from_storage()` for rich content

## Markdown Files

### Simple Markdown

```python
from FileUtils import FileUtils, OutputFileType

file_utils = FileUtils()

# Save simple markdown
content = """# Analysis Report

## Executive Summary
This report analyzes the performance of our AI models.

## Key Findings
- Model accuracy: 95.2%
- Processing time: 2.3 seconds
- User satisfaction: 4.8/5

## Recommendations
1. Implement additional training data
2. Optimize inference pipeline
3. Add real-time monitoring
"""

saved_path, _ = file_utils.save_document_to_storage(
    content=content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="analysis_report"
)

# Load markdown
loaded_content = file_utils.load_document_from_storage(
    file_path="analysis_report.md",
    input_type="processed"
)
```

### Markdown with YAML Frontmatter

```python
# Save markdown with structured metadata
structured_content = {
    "frontmatter": {
        "title": "AI Model Performance Report",
        "author": "AI Team",
        "date": "2024-01-15",
        "version": "1.0",
        "tags": ["AI", "Performance", "Analysis"],
        "confidence": 0.95,
        "model": "GPT-4"
    },
    "body": """# AI Model Performance Report

## Model Metrics

| Model | Accuracy | Precision | Recall | F1-Score |
|-------|----------|-----------|--------|----------|
| Model A | 94.2% | 93.8% | 94.5% | 94.1% |
| Model B | 95.7% | 95.2% | 96.1% | 95.6% |
| Model C | 96.1% | 95.8% | 96.4% | 96.1% |

## Analysis
Model C shows the best overall performance across all metrics.

## Recommendations
1. Deploy Model C to production
2. Monitor performance metrics
3. Schedule retraining cycle
"""
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="model_performance_report",
    sub_path="reports/2024/january"
)

# Load structured markdown
loaded_content = file_utils.load_document_from_storage(
    file_path="model_performance_report.md",
    input_type="processed",
    sub_path="reports/2024/january"
)

# Access frontmatter and body separately
if isinstance(loaded_content, dict):
    metadata = loaded_content["frontmatter"]
    content = loaded_content["body"]
    print(f"Report by {metadata['author']} with {metadata['confidence']} confidence")
```

## DOCX Files

### Simple DOCX

```python
# Save simple DOCX document
docx_content = "This is a test document for DOCX format. It contains basic text content."

saved_path, _ = file_utils.save_document_to_storage(
    content=docx_content,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="simple_document"
)
```

### Structured DOCX

```python
# Save structured DOCX with headings, text, and tables
structured_docx = {
    "title": "Project Report",
    "sections": [
        {
            "heading": "Executive Summary",
            "level": 1,
            "text": "This project aims to improve our AI capabilities and has been completed successfully."
        },
        {
            "heading": "Project Overview",
            "level": 2,
            "text": "The project involved implementing new machine learning models and optimizing existing workflows."
        },
        {
            "heading": "Results",
            "level": 2,
            "text": "The results show significant improvement in accuracy and processing speed."
        },
        {
            "heading": "Performance Metrics",
            "level": 2,
            "table": [
                ["Metric", "Before", "After", "Improvement"],
                ["Accuracy", "87.3%", "95.2%", "+7.9%"],
                ["Speed", "4.2s", "2.3s", "+45%"],
                ["Memory Usage", "1.2GB", "512MB", "-58%"],
                ["User Satisfaction", "3.2/5", "4.8/5", "+50%"]
            ]
        },
        {
            "heading": "Next Steps",
            "level": 2,
            "text": "Based on these results, we recommend proceeding with the full deployment and scheduling regular performance reviews."
        }
    ]
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_docx,
    output_filetype=OutputFileType.DOCX,
    output_type="processed",
    file_name="project_report",
    sub_path="reports/2024"
)

# Load DOCX (extracts text content)
loaded_content = file_utils.load_document_from_storage(
    file_path="project_report.docx",
    input_type="processed",
    sub_path="reports/2024"
)
```

## PDF Files

### Simple PDF

```python
# Save simple PDF
pdf_content = "This is a test document for PDF format. It contains basic text content."

saved_path, _ = file_utils.save_document_to_storage(
    content=pdf_content,
    output_filetype=OutputFileType.PDF,
    output_type="processed",
    file_name="simple_pdf"
)
```

### Structured PDF

```python
# Save structured PDF
structured_pdf = {
    "title": "Technical Documentation",
    "sections": [
        {
            "heading": "Introduction",
            "text": "This document provides technical specifications for the new system architecture."
        },
        {
            "heading": "Architecture Overview",
            "text": "The system follows a microservices architecture with the following components:"
        },
        {
            "heading": "Components",
            "text": "1. API Gateway: Handles routing and authentication\n2. User Service: Manages user data\n3. Data Service: Handles data processing\n4. Notification Service: Sends alerts and updates"
        },
        {
            "heading": "Performance",
            "text": "System performance meets all requirements with 99.9% uptime and sub-second response times."
        },
        {
            "heading": "Security",
            "text": "All components implement OAuth 2.0 authentication and data encryption at rest and in transit."
        }
    ]
}

saved_path, _ = file_utils.save_document_to_storage(
    content=structured_pdf,
    output_filetype=OutputFileType.PDF,
    output_type="processed",
    file_name="technical_documentation",
    sub_path="docs/architecture"
)

# Load PDF (extracts text content)
loaded_content = file_utils.load_document_from_storage(
    file_path="technical_documentation.pdf",
    input_type="processed",
    sub_path="docs/architecture"
)
```

## AI/Agentic Workflow Examples

### AI Analysis Pipeline

```python
def create_ai_analysis_report(analysis_results):
    """Create a comprehensive AI analysis report."""
    
    # Structure the analysis results
    report_content = {
        "frontmatter": {
            "title": "AI Analysis Report",
            "model": analysis_results.get("model", "Unknown"),
            "timestamp": analysis_results.get("timestamp"),
            "confidence": analysis_results.get("confidence", 0.0),
            "processing_time": analysis_results.get("processing_time", "N/A"),
            "tags": analysis_results.get("tags", [])
        },
        "body": f"""# AI Analysis Report

## Executive Summary
This report presents the results of AI analysis conducted on {analysis_results.get('dataset_name', 'the dataset')}.

## Analysis Results

### Key Findings
{format_findings(analysis_results.get('findings', []))}

### Confidence Metrics
- Overall Confidence: {analysis_results.get('confidence', 0.0):.1%}
- Processing Time: {analysis_results.get('processing_time', 'N/A')}
- Model Used: {analysis_results.get('model', 'Unknown')}

### Recommendations
{format_recommendations(analysis_results.get('recommendations', []))}

## Next Steps
1. Review findings with stakeholders
2. Implement recommended changes
3. Schedule follow-up analysis
4. Update model training data
"""
    }
    
    # Save the report
    saved_path, _ = file_utils.save_document_to_storage(
        content=report_content,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name=f"ai_analysis_{analysis_results.get('timestamp', 'unknown')}",
        sub_path="ai_workflows/analysis"
    )
    
    return saved_path

def format_findings(findings):
    """Format findings as markdown list."""
    if not findings:
        return "- No specific findings identified"
    return "\n".join(f"- {finding}" for finding in findings)

def format_recommendations(recommendations):
    """Format recommendations as numbered list."""
    if not recommendations:
        return "1. No specific recommendations at this time"
    return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
```

### Multi-Format Report Generation

```python
def generate_comprehensive_report(data, analysis_results):
    """Generate reports in multiple formats."""
    
    # Create base content
    base_content = {
        "title": "Comprehensive Analysis Report",
        "sections": [
            {
                "heading": "Data Summary",
                "level": 1,
                "text": f"Analysis conducted on {len(data)} records"
            },
            {
                "heading": "Key Findings",
                "level": 2,
                "text": analysis_results.get("summary", "Analysis completed")
            },
            {
                "heading": "Metrics",
                "level": 2,
                "table": [
                    ["Metric", "Value"],
                    ["Records Processed", str(len(data))],
                    ["Confidence", f"{analysis_results.get('confidence', 0):.1%}"],
                    ["Processing Time", analysis_results.get('time', 'N/A')]
                ]
            }
        ]
    }
    
    # Save in multiple formats
    reports = {}
    
    # Markdown version
    markdown_content = {
        "frontmatter": {
            "title": base_content["title"],
            "generated_at": analysis_results.get("timestamp"),
            "confidence": analysis_results.get("confidence", 0)
        },
        "body": format_as_markdown(base_content)
    }
    
    reports["markdown"], _ = file_utils.save_document_to_storage(
        content=markdown_content,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="comprehensive_report",
        sub_path="reports/multi_format"
    )
    
    # DOCX version
    reports["docx"], _ = file_utils.save_document_to_storage(
        content=base_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="comprehensive_report",
        sub_path="reports/multi_format"
    )
    
    # PDF version
    reports["pdf"], _ = file_utils.save_document_to_storage(
        content=base_content,
        output_filetype=OutputFileType.PDF,
        output_type="processed",
        file_name="comprehensive_report",
        sub_path="reports/multi_format"
    )
    
    return reports

def format_as_markdown(content):
    """Convert structured content to markdown."""
    markdown = f"# {content['title']}\n\n"
    
    for section in content["sections"]:
        if "heading" in section:
            level = section.get("level", 1)
            markdown += f"{'#' * level} {section['heading']}\n\n"
        
        if "text" in section:
            markdown += f"{section['text']}\n\n"
        
        if "table" in section:
            markdown += format_table_as_markdown(section["table"]) + "\n\n"
    
    return markdown

def format_table_as_markdown(table):
    """Convert table to markdown format."""
    if not table:
        return ""
    
    markdown = "| " + " | ".join(table[0]) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(table[0])) + " |\n"
    
    for row in table[1:]:
        markdown += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return markdown
```

## Error Handling

Document operations can fail for various reasons. Handle errors gracefully:

```python
from FileUtils.core.base import StorageError

def safe_save_document(content, file_type, file_name):
    """Safely save document with error handling."""
    try:
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=file_type,
            output_type="processed",
            file_name=file_name
        )
        print(f"Document saved successfully: {saved_path}")
        return saved_path
    except StorageError as e:
        print(f"Failed to save document: {e}")
        return None
    except ValueError as e:
        print(f"Invalid document format: {e}")
        return None

def safe_load_document(file_path, input_type="processed"):
    """Safely load document with error handling."""
    try:
        content = file_utils.load_document_from_storage(
            file_path=file_path,
            input_type=input_type
        )
        print(f"Document loaded successfully: {len(str(content))} characters")
        return content
    except StorageError as e:
        print(f"Failed to load document: {e}")
        return None
    except FileNotFoundError as e:
        print(f"Document not found: {e}")
        return None
```

## Best Practices

### 1. Content Structure

- Use consistent structure for document content
- Include metadata in frontmatter for Markdown files
- Use appropriate heading levels for DOCX and PDF

### 2. File Organization

- Use subdirectories to organize documents by type, date, or project
- Include timestamps in filenames for version tracking
- Maintain consistent naming conventions

### 3. Error Handling

- Always handle missing dependencies gracefully
- Provide fallback options when document operations fail
- Log errors for debugging and monitoring

### 4. Performance

- Use Markdown for simple text documents (no dependencies)
- Use DOCX for complex documents with formatting
- Use PDF for final reports and documentation

### 5. Integration

- Combine document generation with data processing workflows
- Use structured content for programmatic document creation
- Leverage subdirectory support for organized file management

## Troubleshooting

### Missing Dependencies

If you encounter import errors:

```python
# Check if dependencies are installed
try:
    import docx
    print("DOCX support available")
except ImportError:
    print("Install DOCX support: pip install python-docx")

try:
    import fitz
    print("PDF support available")
except ImportError:
    print("Install PDF support: pip install PyMuPDF")
```

### Content Format Issues

Ensure content matches expected format:

```python
# For Markdown with frontmatter
content = {
    "frontmatter": {"key": "value"},
    "body": "markdown content"
}

# For structured DOCX/PDF
content = {
    "title": "Document Title",
    "sections": [
        {"heading": "Section", "level": 1, "text": "content"}
    ]
}
```

### File Path Issues

Use consistent path handling:

```python
# Correct usage with sub_path
saved_path, _ = file_utils.save_document_to_storage(
    content=content,
    output_filetype=OutputFileType.MARKDOWN,
    output_type="processed",
    file_name="report",  # Just filename
    sub_path="reports/2024"  # Subdirectory
)

# Load from same location
loaded_content = file_utils.load_document_from_storage(
    file_path="report.md",  # Just filename
    input_type="processed",
    sub_path="reports/2024"  # Same subdirectory
)
```
