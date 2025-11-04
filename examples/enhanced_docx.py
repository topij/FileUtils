"""Example: Enhanced DOCX Template System

This script demonstrates the enhanced DOCX functionality with template support,
markdown conversion, and customizable styling.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)  # Insert at beginning to prioritize

from FileUtils import FileUtils, OutputFileType


def demonstrate_enhanced_docx():
    """Demonstrate enhanced DOCX functionality."""
    print("=== Enhanced DOCX Template System Demo ===\n")

    # Initialize FileUtils with template configuration
    file_utils = FileUtils(
        config_override={
            "docx_templates": {
                "template_dir": "data/templates",
                "default_template": "style-template-doc.docx",
                "templates": {
                    "default": "style-template-doc.docx",
                    "review": "style-template-doc.docx",
                    "report": "style-template-doc.docx",
                    "ip_template": "IP-template-doc.docx",  # Personal IP template
                },
            },
            "style_mapping": {
                "table": "IP-table_light",
                "table_fallback": "IP-table",
                "table_default": "Table Grid",
                "heading_1": "Heading 1",
                "list_bullet": "List Bullet",
                "list_number": "List Number",
            },
        }
    )

    # Example 1: Convert Markdown to DOCX with template
    print("1. Converting Markdown to DOCX with template...")

    markdown_content = """# Project Report

## Executive Summary

This is a comprehensive analysis of our project progress.

## Key Findings

- **Important**: We've achieved 95% completion
- **Critical**: Budget is on track
- **Action Required**: Need to review timeline

### TODO Items

- [ ] Complete final testing
- [x] Update documentation
- [ ] Schedule review meeting

## Data Analysis

| Metric | Value | Status |
|--------|-------|--------|
| Progress | 95% | ✅ On Track |
| Budget | $45,000 | ✅ Under Budget |
| Timeline | 2 weeks | ⚠️ Review Needed |

## Next Steps

1. Complete testing phase
2. Prepare final documentation
3. Schedule stakeholder review
4. Plan deployment strategy

## Technical Details

The project uses **modern technologies** and follows *best practices*.

Code example: `python main.py --config production`

---

*Generated on 2024-01-15*
"""

    saved_path, _ = file_utils.save_document_to_storage(
        content=markdown_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="project_report",
        template="review",  # Use review template
        add_provenance=True,
        add_reviewer_instructions=True,
        source_file="project_report.md",
    )
    print(f"✓ Markdown converted to DOCX: {saved_path}")

    # Example 2: Structured content with template
    print("\n2. Creating structured DOCX with template...")

    structured_content = {
        "title": "Technical Specification",
        "sections": [
            {
                "heading": "Overview",
                "level": 1,
                "text": "This document outlines the technical specifications for the new system.",
            },
            {
                "heading": "System Requirements",
                "level": 2,
                "text": "The system must meet the following requirements:",
            },
            {
                "heading": "Performance Metrics",
                "level": 2,
                "table": [
                    ["Metric", "Target", "Current"],
                    ["Response Time", "< 2s", "1.8s"],
                    ["Throughput", "> 1000 req/s", "1200 req/s"],
                    ["Uptime", "> 99.9%", "99.95%"],
                ],
            },
            {
                "heading": "Implementation Plan",
                "level": 2,
                "text": "The implementation will be completed in three phases.",
            },
        ],
    }

    saved_path, _ = file_utils.save_document_to_storage(
        content=structured_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="technical_spec",
        template="report",  # Use report template
    )
    print(f"✓ Structured DOCX created: {saved_path}")

    # Example 3: Simple text with default template
    print("\n3. Creating simple DOCX...")

    simple_content = """Simple Document

This is a basic document without complex formatting.

Key points:
- Point 1
- Point 2
- Point 3

End of document."""

    saved_path, _ = file_utils.save_document_to_storage(
        content=simple_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="simple_doc",
    )
    print(f"✓ Simple DOCX created: {saved_path}")

    # Example 4: Template management
    print("\n4. Template management...")

    try:
        from FileUtils.templates import DocxTemplateManager

        template_manager = DocxTemplateManager(file_utils.config)

        # List available templates
        available_templates = template_manager.list_available_templates()
        print(f"Available templates: {list(available_templates.keys())}")

        # Get template info including headers/footers
        template_info = template_manager.get_template_info("default")
        print(f"Default template info: {template_info}")

        # Check for headers and footers
        if "headers_footers" in template_info:
            hf_info = template_info["headers_footers"]
            print(f"Template has headers: {hf_info.get('has_headers', False)}")
            print(f"Template has footers: {hf_info.get('has_footers', False)}")
            if hf_info.get("has_headers"):
                print(f"Header count: {hf_info.get('header_count', 0)}")
            if hf_info.get("has_footers"):
                print(f"Footer count: {hf_info.get('footer_count', 0)}")

    except ImportError:
        print("Template management not available (templates module not found)")

    print("\n=== Enhanced DOCX Demo Complete ===")
    print("✓ Markdown conversion with template")
    print("✓ Structured content with template")
    print("✓ Simple document creation")
    print("✓ Template management")

    return {
        "markdown_docx": saved_path,
        "structured_docx": saved_path,
        "simple_docx": saved_path,
    }


def demonstrate_template_configuration():
    """Demonstrate template configuration options."""
    print("\n=== Template Configuration Demo ===\n")

    # Custom template configuration
    custom_config = {
        "docx_templates": {
            "template_dir": "custom_templates",
            "templates": {
                "corporate": "corporate-template.docx",
                "technical": "technical-template.docx",
                "simple": None,  # Use default
            },
        },
        "style_mapping": {
            "table": "Corporate-Table",
            "heading_1": "Corporate-Heading-1",
            "list_bullet": "Corporate-List",
        },
        "markdown_options": {
            "add_provenance": True,
            "add_reviewer_instructions": True,
            "checkbox_symbols": {"unchecked": "□", "checked": "■"},
        },
    }

    file_utils = FileUtils(config_override=custom_config)

    print("Custom configuration applied:")
    print(f"- Template directory: {custom_config['docx_templates']['template_dir']}")
    print(
        f"- Available templates: {list(custom_config['docx_templates']['templates'].keys())}"
    )
    print(f"- Custom table style: {custom_config['style_mapping']['table']}")

    return file_utils


if __name__ == "__main__":
    # Run the main demonstration
    results = demonstrate_enhanced_docx()

    # Demonstrate configuration
    demonstrate_template_configuration()

    print(f"\nDemo results: {results}")
