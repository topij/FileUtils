"""Example demonstrating new document file types (DOCX, Markdown, PDF)."""

import pandas as pd

from FileUtils import FileUtils, OutputFileType


def demonstrate_document_types():
    """Demonstrate the new document file type functionality."""
    # Initialize FileUtils
    file_utils = FileUtils()

    print("=== FileUtils Document Types Demo ===\n")

    # 1. Markdown Examples
    print("1. Markdown File Examples")
    print("-" * 30)

    # Simple markdown
    simple_md = """# AI Analysis Report

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
        content=simple_md,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="ai_analysis_report",
        include_timestamp=False,
    )
    print(f"✓ Saved simple markdown: {saved_path}")

    # Markdown with YAML frontmatter
    structured_md = {
        "frontmatter": {
            "title": "AI Model Performance Report",
            "author": "AI Team",
            "date": "2024-01-15",
            "version": "1.0",
            "tags": ["AI", "Performance", "Analysis"],
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
""",
    }

    saved_path, _ = file_utils.save_document_to_storage(
        content=structured_md,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="structured_report",
        include_timestamp=False,
    )
    print(f"✓ Saved structured markdown: {saved_path}")

    # Load markdown
    loaded_content = file_utils.load_document_from_storage(
        file_path="ai_analysis_report.md", input_type="processed"
    )
    print(f"✓ Loaded markdown content (length: {len(loaded_content)} chars)")

    print()

    # 2. DOCX Examples (if python-docx is available)
    print("2. DOCX File Examples")
    print("-" * 30)

    try:
        # Simple DOCX
        simple_docx = (
            "This is a test document for DOCX format. It contains basic text content."
        )

        saved_path, _ = file_utils.save_document_to_storage(
            content=simple_docx,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="simple_document",
            include_timestamp=False,
        )
        print(f"✓ Saved simple DOCX: {saved_path}")

        # Structured DOCX
        structured_docx = {
            "title": "Project Report",
            "sections": [
                {
                    "heading": "Project Overview",
                    "level": 1,
                    "text": "This project aims to improve our AI capabilities.",
                },
                {
                    "heading": "Results",
                    "level": 2,
                    "text": "The results show significant improvement in accuracy.",
                },
                {
                    "heading": "Data Summary",
                    "level": 2,
                    "table": [
                        ["Metric", "Value", "Unit"],
                        ["Accuracy", "95.2", "%"],
                        ["Speed", "2.3", "seconds"],
                        ["Memory", "512", "MB"],
                    ],
                },
            ],
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=structured_docx,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="structured_document",
            include_timestamp=False,
        )
        print(f"✓ Saved structured DOCX: {saved_path}")

        # Load DOCX
        loaded_content = file_utils.load_document_from_storage(
            file_path="simple_document.docx", input_type="processed"
        )
        print(f"✓ Loaded DOCX content (length: {len(loaded_content)} chars)")

    except Exception as e:
        print(f"⚠ DOCX functionality requires python-docx: {e}")

    print()

    # 3. PDF Examples (if PyMuPDF is available)
    print("3. PDF File Examples")
    print("-" * 30)

    try:
        # Simple PDF
        simple_pdf = (
            "This is a test document for PDF format. It contains basic text content."
        )

        saved_path, _ = file_utils.save_document_to_storage(
            content=simple_pdf,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="simple_pdf",
            include_timestamp=False,
        )
        print(f"✓ Saved simple PDF: {saved_path}")

        # Structured PDF
        structured_pdf = {
            "title": "Technical Documentation",
            "sections": [
                {
                    "heading": "Introduction",
                    "text": "This document provides technical specifications.",
                },
                {
                    "heading": "Architecture",
                    "text": "The system follows a microservices architecture.",
                },
                {
                    "heading": "Performance",
                    "text": "System performance meets all requirements.",
                },
            ],
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=structured_pdf,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="structured_pdf",
            include_timestamp=False,
        )
        print(f"✓ Saved structured PDF: {saved_path}")

        # Load PDF
        loaded_content = file_utils.load_document_from_storage(
            file_path="simple_pdf.pdf", input_type="processed"
        )
        print(f"✓ Loaded PDF content (length: {len(loaded_content)} chars)")

    except Exception as e:
        print(f"⚠ PDF functionality requires PyMuPDF: {e}")

    print()

    # 4. Subdirectory Examples
    print("4. Subdirectory Examples")
    print("-" * 30)

    # Save to subdirectory
    content = "Document saved to subdirectory for organization."

    saved_path, _ = file_utils.save_document_to_storage(
        content=content,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="subdir_document",
        sub_path="reports/2024/january",
        include_timestamp=False,
    )
    print(f"✓ Saved to subdirectory: {saved_path}")

    # Load from subdirectory
    loaded_content = file_utils.load_document_from_storage(
        file_path="subdir_document.md",
        input_type="processed",
        sub_path="reports/2024/january",
    )
    print(f"✓ Loaded from subdirectory (length: {len(loaded_content)} chars)")

    print()

    # 5. Error Handling
    print("5. Error Handling Examples")
    print("-" * 30)

    try:
        # Try to save with invalid format
        file_utils.save_document_to_storage(
            content="test",
            output_filetype=OutputFileType.CSV,  # Not a document format
            output_type="processed",
            file_name="invalid_test",
        )
    except ValueError as e:
        print(f"✓ Caught invalid format error: {e}")

    print()

    print("=== Demo Complete ===")
    print("\nTo install document dependencies:")
    print("pip install 'FileUtils[documents]'")
    print("\nOr install specific dependencies:")
    print("pip install python-docx markdown PyMuPDF")


def demonstrate_ai_workflow():
    """Demonstrate how document types can be used in AI workflows."""
    print("\n=== AI Workflow Example ===")

    file_utils = FileUtils()

    # Simulate AI analysis results
    analysis_results = {
        "frontmatter": {
            "model": "GPT-4",
            "timestamp": "2024-01-15T10:30:00Z",
            "confidence": 0.95,
            "processing_time": "2.3s",
        },
        "body": """# AI Analysis Results

## Summary
The analysis identified 3 key insights from the provided data.

## Key Findings

### 1. Pattern Recognition
- Detected recurring patterns in user behavior
- Confidence level: 94.2%

### 2. Anomaly Detection
- Found 2 anomalies requiring attention
- Severity: Medium

### 3. Recommendations
1. Implement additional monitoring
2. Update training data
3. Schedule follow-up analysis

## Next Steps
- Review findings with stakeholders
- Implement recommended changes
- Schedule next analysis cycle
""",
    }

    # Save analysis results
    saved_path, _ = file_utils.save_document_to_storage(
        content=analysis_results,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="ai_analysis_results",
        sub_path="ai_workflows/analysis_2024_01_15",
        include_timestamp=False,
    )

    print(f"✓ AI analysis saved to: {saved_path}")
    print("✓ Document includes structured metadata and analysis results")
    print("✓ Ready for further processing or human review")


if __name__ == "__main__":
    demonstrate_document_types()
    demonstrate_ai_workflow()
