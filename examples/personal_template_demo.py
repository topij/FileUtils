#!/usr/bin/env python3
"""Example: Switching to Personal IP Template

This script demonstrates how to easily switch to your personal IP template
for personal use while keeping the generic template as default for sharing.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from FileUtils import FileUtils, OutputFileType


def demonstrate_personal_template():
    """Demonstrate using personal IP template."""
    print("=== Personal IP Template Demo ===\n")

    # Option 1: Override default template in code
    print("1. Using personal IP template via config override...")

    file_utils = FileUtils(
        config_override={
            "docx_templates": {
                "default_template": "IP-template-doc.docx",
                "templates": {
                    "default": "IP-template-doc.docx"  # Your personal template
                },
            }
        }
    )

    markdown_content = """# Personal Document

## Using IP Template

This document uses your personal IP template with custom branding.

## Key Features
- **Custom Styling**: Uses your IP-table styles
- **Personal Branding**: Your headers and footers
- **Professional Look**: Consistent with your brand

| Feature | Status | Notes |
|---------|--------|-------|
| Branding | ✅ | Personal IP template |
| Styling | ✅ | IP-table_light styles |
| Headers | ✅ | Custom headers preserved |
"""

    saved_path, _ = file_utils.save_document_to_storage(
        content=markdown_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="personal_document",
        add_provenance=True,
    )
    print(f"✓ Personal document created: {saved_path}")

    # Option 2: Use specific template name
    print("\n2. Using specific template name...")

    # Reset to default configuration
    file_utils = FileUtils()

    saved_path, _ = file_utils.save_document_to_storage(
        content=markdown_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="personal_document_specific",
        template="ip_template",  # Use IP template specifically
        add_provenance=True,
    )
    print(f"✓ Personal document (specific template): {saved_path}")

    # Show template information
    print("\n3. Template information...")
    try:
        from FileUtils.templates import DocxTemplateManager

        template_manager = DocxTemplateManager(file_utils.config)

        # Show available templates
        available_templates = template_manager.list_available_templates()
        print(f"Available templates: {list(available_templates.keys())}")

        # Show default template info
        default_info = template_manager.get_template_info("default")
        print(f"Default template: {default_info.get('path', 'Not found')}")

        # Show IP template info
        ip_info = template_manager.get_template_info("ip_template")
        print(f"IP template: {ip_info.get('path', 'Not found')}")

    except ImportError:
        print("Template management not available")

    print("\n=== Personal Template Demo Complete ===")
    print("✓ Personal IP template usage")
    print("✓ Config override method")
    print("✓ Specific template method")
    print("✓ Template information display")


if __name__ == "__main__":
    demonstrate_personal_template()
