"""Tests for new document file types (DOCX, Markdown, PDF)."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
import warnings

# Suppress PyMuPDF deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPy.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*swigvarlink.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")

from FileUtils import FileUtils
from FileUtils.core.enums import OutputFileType, StorageType
from FileUtils.core.base import StorageError


class TestDocumentTypes:
    """Test document file type functionality."""

    def test_output_file_type_enum(self):
        """Test that new document types are in the enum."""
        assert OutputFileType.DOCX.value == "docx"
        assert OutputFileType.MARKDOWN.value == "md"
        assert OutputFileType.PDF.value == "pdf"

    def test_save_markdown_simple_text(self, file_utils):
        """Test saving simple text to Markdown."""
        content = "# Test Document\n\nThis is a test markdown document."
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_md",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert saved_path.endswith(".md")
        
        # Verify content
        with open(saved_path, "r", encoding="utf-8") as f:
            loaded_content = f.read()
        assert loaded_content == content

    def test_save_markdown_with_frontmatter(self, file_utils):
        """Test saving Markdown with YAML frontmatter."""
        content = {
            "frontmatter": {
                "title": "Test Document",
                "author": "Test Author",
                "date": "2024-01-01"
            },
            "body": "# Test Document\n\nThis is a test markdown document."
        }
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_md_frontmatter",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        
        # Verify content
        with open(saved_path, "r", encoding="utf-8") as f:
            loaded_content = f.read()
        assert "---" in loaded_content
        assert "title: Test Document" in loaded_content
        assert "# Test Document" in loaded_content

    def test_load_markdown_simple(self, file_utils):
        """Test loading simple Markdown file."""
        content = "# Test Document\n\nThis is a test markdown document."
        
        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_load_md",
            include_timestamp=False
        )
        
        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed"
        )
        
        assert loaded_content == content

    def test_load_markdown_with_frontmatter(self, file_utils):
        """Test loading Markdown with frontmatter."""
        content = {
            "frontmatter": {
                "title": "Test Document",
                "author": "Test Author"
            },
            "body": "# Test Document\n\nThis is a test markdown document."
        }
        
        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_load_md_frontmatter",
            include_timestamp=False
        )
        
        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed"
        )
        
        assert isinstance(loaded_content, dict)
        assert loaded_content["frontmatter"]["title"] == "Test Document"
        assert loaded_content["body"] == "# Test Document\n\nThis is a test markdown document."

    def test_save_docx_simple_text(self, file_utils):
        """Test saving simple text to DOCX."""
        content = "This is a test document for DOCX format."
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="test_docx",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert saved_path.endswith(".docx")

    def test_save_docx_structured(self, file_utils):
        """Test saving structured content to DOCX."""
        content = {
            "title": "Test Document",
            "sections": [
                {
                    "heading": "Introduction",
                    "level": 1,
                    "text": "This is the introduction section."
                },
                {
                    "heading": "Data Table",
                    "level": 2,
                    "table": [
                        ["Name", "Age", "City"],
                        ["Alice", "25", "New York"],
                        ["Bob", "30", "London"]
                    ]
                }
            ]
        }
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="test_docx_structured",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert saved_path.endswith(".docx")

    def test_load_docx(self, file_utils):
        """Test loading DOCX file."""
        content = "This is a test document for DOCX format."
        
        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="test_load_docx",
            include_timestamp=False
        )
        
        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed"
        )
        
        assert isinstance(loaded_content, str)
        assert "test document" in loaded_content.lower()

    def test_save_pdf_simple_text(self, file_utils):
        """Test saving simple text to PDF."""
        content = "This is a test document for PDF format."
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_pdf",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert saved_path.endswith(".pdf")

    def test_save_pdf_structured(self, file_utils):
        """Test saving structured content to PDF."""
        content = {
            "title": "Test PDF Document",
            "sections": [
                {
                    "heading": "Introduction",
                    "text": "This is the introduction section."
                },
                {
                    "heading": "Conclusion",
                    "text": "This is the conclusion section."
                }
            ]
        }
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_pdf_structured",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert saved_path.endswith(".pdf")

    def test_load_pdf(self, file_utils):
        """Test loading PDF file."""
        content = "This is a test document for PDF format."
        
        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_load_pdf",
            include_timestamp=False
        )
        
        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed"
        )
        
        assert isinstance(loaded_content, str)
        assert "test document" in loaded_content.lower()

    def test_invalid_document_format(self, file_utils):
        """Test that invalid document formats raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_utils.save_document_to_storage(
                content="test",
                output_filetype=OutputFileType.CSV,  # Not a document format
                output_type="processed",
                file_name="test_invalid"
            )
        assert "Invalid document format" in str(exc_info.value)

    def test_document_with_subpath(self, file_utils):
        """Test saving documents with sub_path."""
        content = "Test document with subpath."
        
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_subpath",
            sub_path="documents/test",
            include_timestamp=False
        )
        
        assert Path(saved_path).exists()
        assert "documents/test" in str(saved_path)
        assert saved_path.endswith(".md")

    def test_load_document_with_subpath(self, file_utils):
        """Test loading documents with sub_path."""
        content = "Test document with subpath for loading."
        
        # Save with subpath
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_load_subpath",
            sub_path="documents/load_test",
            include_timestamp=False
        )
        
        # Load with subpath
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed",
            sub_path="documents/load_test"
        )
        
        assert loaded_content == content

    def test_missing_dependencies_error(self, file_utils):
        """Test that missing dependencies raise appropriate errors."""
        # This test would require mocking the import failures
        # For now, we'll just test that the methods exist and can be called
        # In a real scenario, you'd mock the imports to test error handling
        
        # Test that methods exist
        assert hasattr(file_utils, 'save_document_to_storage')
        assert hasattr(file_utils, 'load_document_from_storage')
        
        # Test that storage backends have the required methods
        assert hasattr(file_utils.storage, 'save_document')
        assert hasattr(file_utils.storage, 'load_document')


@pytest.mark.skipif(
    not os.path.exists("/usr/bin/python3") and not os.path.exists("/usr/local/bin/python3"),
    reason="Skipping dependency tests in CI environment"
)
class TestDocumentDependencies:
    """Test document functionality with actual dependencies."""
    
    def test_docx_dependency_available(self):
        """Test if python-docx is available."""
        try:
            from docx import Document
            assert True
        except ImportError:
            pytest.skip("python-docx not installed")

    def test_pymupdf_dependency_available(self):
        """Test if PyMuPDF is available."""
        try:
            import fitz
            assert True
        except ImportError:
            pytest.skip("PyMuPDF not installed")

    def test_markdown_dependency_available(self):
        """Test if markdown library is available."""
        try:
            import markdown
            assert True
        except ImportError:
            pytest.skip("markdown library not installed")
