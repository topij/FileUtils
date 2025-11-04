"""Tests for new document file types (DOCX, Markdown, PDF)."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import os
import warnings

# Suppress PyMuPDF deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*SwigPy.*")
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*swigvarlink.*"
)
warnings.filterwarnings("ignore", category=DeprecationWarning, module="fitz")

from FileUtils import FileUtils
from FileUtils.core.enums import OutputFileType, StorageType
from FileUtils.core.base import StorageError


# Helper to check if PyMuPDF is available
def _pymupdf_available():
    """Check if PyMuPDF (fitz) is available."""
    try:
        import fitz  # noqa: F401

        return True
    except ImportError:
        return False


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
            include_timestamp=False,
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
                "date": "2024-01-01",
            },
            "body": "# Test Document\n\nThis is a test markdown document.",
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_md_frontmatter",
            include_timestamp=False,
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
            include_timestamp=False,
        )

        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name, input_type="processed"
        )

        assert loaded_content == content

    def test_load_markdown_with_frontmatter(self, file_utils):
        """Test loading Markdown with frontmatter."""
        content = {
            "frontmatter": {"title": "Test Document", "author": "Test Author"},
            "body": "# Test Document\n\nThis is a test markdown document.",
        }

        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="test_load_md_frontmatter",
            include_timestamp=False,
        )

        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name, input_type="processed"
        )

        assert isinstance(loaded_content, dict)
        assert loaded_content["frontmatter"]["title"] == "Test Document"
        assert (
            loaded_content["body"]
            == "# Test Document\n\nThis is a test markdown document."
        )

    def test_save_docx_simple_text(self, file_utils):
        """Test saving simple text to DOCX."""
        content = "This is a test document for DOCX format."

        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="test_docx",
            include_timestamp=False,
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
                    "text": "This is the introduction section.",
                },
                {
                    "heading": "Data Table",
                    "level": 2,
                    "table": [
                        ["Name", "Age", "City"],
                        ["Alice", "25", "New York"],
                        ["Bob", "30", "London"],
                    ],
                },
            ],
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.DOCX,
            output_type="processed",
            file_name="test_docx_structured",
            include_timestamp=False,
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
            include_timestamp=False,
        )

        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name, input_type="processed"
        )

        assert isinstance(loaded_content, str)
        assert "test document" in loaded_content.lower()

    @pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
    def test_save_pdf_simple_text(self, file_utils):
        """Test saving simple text to PDF."""
        content = "This is a test document for PDF format."

        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_pdf",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()
        assert saved_path.endswith(".pdf")

    @pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
    def test_save_pdf_structured(self, file_utils):
        """Test saving structured content to PDF."""
        content = {
            "title": "Test PDF Document",
            "sections": [
                {
                    "heading": "Introduction",
                    "text": "This is the introduction section.",
                },
                {"heading": "Conclusion", "text": "This is the conclusion section."},
            ],
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_pdf_structured",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()
        assert saved_path.endswith(".pdf")

    @pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
    def test_load_pdf(self, file_utils):
        """Test loading PDF file."""
        content = "This is a test document for PDF format."

        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.PDF,
            output_type="processed",
            file_name="test_load_pdf",
            include_timestamp=False,
        )

        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name, input_type="processed"
        )

        assert isinstance(loaded_content, str)
        assert "test document" in loaded_content.lower()

    def test_save_pptx_from_bytes(self, file_utils, temp_dir):
        """Test saving PPTX file from bytes."""
        # Create a minimal PPTX file in memory (PPTX is a ZIP archive with XML)
        import zipfile
        import io

        pptx_buffer = io.BytesIO()
        with zipfile.ZipFile(pptx_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
            )
            zip_file.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>',
            )

        pptx_bytes = pptx_buffer.getvalue()

        saved_path, _ = file_utils.save_document_to_storage(
            content=pptx_bytes,
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="test_pptx_from_bytes",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()
        assert saved_path.endswith(".pptx")
        # Verify it's a valid ZIP file
        assert zipfile.is_zipfile(saved_path)

    def test_save_pptx_from_file_path(self, file_utils, temp_dir):
        """Test saving PPTX file from source file path."""
        import zipfile
        import io

        # Create a source PPTX file
        source_pptx = temp_dir / "source.pptx"
        pptx_buffer = io.BytesIO()
        with zipfile.ZipFile(pptx_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
            )
            zip_file.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>',
            )

        with open(source_pptx, "wb") as f:
            f.write(pptx_buffer.getvalue())

        saved_path, _ = file_utils.save_document_to_storage(
            content=str(source_pptx),
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="test_pptx_from_path",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()
        assert saved_path.endswith(".pptx")
        assert zipfile.is_zipfile(saved_path)
        # Files should have same size (they're copies)
        assert Path(saved_path).stat().st_size == source_pptx.stat().st_size

    def test_load_pptx(self, file_utils, temp_dir):
        """Test loading PPTX file."""
        import zipfile
        import io

        # Create a PPTX file
        pptx_buffer = io.BytesIO()
        with zipfile.ZipFile(pptx_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
            )
            zip_file.writestr(
                "_rels/.rels",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>',
            )

        pptx_bytes = pptx_buffer.getvalue()

        # Save first
        saved_path, _ = file_utils.save_document_to_storage(
            content=pptx_bytes,
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="test_load_pptx",
            include_timestamp=False,
        )

        # Load using the new method
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name, input_type="processed"
        )

        assert isinstance(loaded_content, bytes)
        assert len(loaded_content) > 0
        # Verify loaded content is valid PPTX (ZIP file)
        pptx_buffer_check = io.BytesIO(loaded_content)
        assert zipfile.is_zipfile(pptx_buffer_check)

    def test_save_pptx_with_subpath(self, file_utils, temp_dir):
        """Test saving PPTX with sub_path."""
        import zipfile
        import io

        pptx_buffer = io.BytesIO()
        with zipfile.ZipFile(pptx_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(
                "[Content_Types].xml",
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>',
            )

        pptx_bytes = pptx_buffer.getvalue()

        saved_path, _ = file_utils.save_document_to_storage(
            content=pptx_bytes,
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="test_pptx_subpath",
            sub_path="presentations/2024",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()
        assert "presentations/2024" in str(saved_path)
        assert saved_path.endswith(".pptx")

    def test_save_pptx_invalid_content_type(self, file_utils):
        """Test that invalid content types for PPTX raise appropriate errors."""
        from FileUtils.core.base import StorageError

        # PPTX requires bytes or Path, not arbitrary string content
        with pytest.raises(StorageError) as exc_info:
            file_utils.save_document_to_storage(
                content="invalid string content",
                output_filetype=OutputFileType.PPTX,
                output_type="processed",
                file_name="test_invalid_pptx",
                include_timestamp=False,
            )
        error_msg = str(exc_info.value)
        # Should indicate invalid content type (wrapped in StorageError at top level)
        # The full error message contains: "Failed to save document: ... Failed to save PPTX file: Invalid content type for PPTX..."
        assert "Invalid content type for PPTX" in error_msg

    def test_invalid_document_format(self, file_utils):
        """Test that invalid document formats raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            file_utils.save_document_to_storage(
                content="test",
                output_filetype=OutputFileType.CSV,  # Not a document format
                output_type="processed",
                file_name="test_invalid",
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
            include_timestamp=False,
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
            include_timestamp=False,
        )

        # Load with subpath
        loaded_content = file_utils.load_document_from_storage(
            file_path=Path(saved_path).name,
            input_type="processed",
            sub_path="documents/load_test",
        )

        assert loaded_content == content

    def test_missing_dependencies_error(self, file_utils):
        """Test that missing dependencies raise appropriate errors."""
        # This test would require mocking the import failures
        # For now, we'll just test that the methods exist and can be called
        # In a real scenario, you'd mock the imports to test error handling

        # Test that methods exist
        assert hasattr(file_utils, "save_document_to_storage")
        assert hasattr(file_utils, "load_document_from_storage")

        # Test that storage backends have the required methods
        assert hasattr(file_utils.storage, "save_document")
        assert hasattr(file_utils.storage, "load_document")


@pytest.mark.skipif(
    not os.path.exists("/usr/bin/python3")
    and not os.path.exists("/usr/local/bin/python3"),
    reason="Skipping dependency tests in CI environment",
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


class TestDocumentFormatIntegration:
    """Test integration between document formats and existing functionality."""

    def test_json_yaml_as_documents(self, file_utils):
        """Test JSON and YAML as document formats."""
        # Test JSON as document
        json_data = {
            "project": "Test Project",
            "version": "1.0.0",
            "config": {"debug": True, "timeout": 30},
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=json_data,
            output_filetype=OutputFileType.JSON,
            output_type="processed",
            file_name="test_json_doc",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()

        # Load as document
        loaded_data = file_utils.load_document_from_storage(
            file_path="test_json_doc.json", input_type="processed"
        )

        assert loaded_data["project"] == "Test Project"
        assert loaded_data["config"]["debug"] is True

        # Test YAML as document
        yaml_data = {
            "database": {"host": "localhost", "port": 5432},
            "cache": {"enabled": True, "ttl": 3600},
        }

        saved_path, _ = file_utils.save_document_to_storage(
            content=yaml_data,
            output_filetype=OutputFileType.YAML,
            output_type="processed",
            file_name="test_yaml_doc",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()

        # Load as document
        loaded_data = file_utils.load_document_from_storage(
            file_path="test_yaml_doc.yaml", input_type="processed"
        )

        assert loaded_data["database"]["host"] == "localhost"
        assert loaded_data["cache"]["enabled"] is True

    def test_document_with_pandas_types(self, file_utils):
        """Test document saving with pandas types."""
        import pandas as pd
        import numpy as np

        # Create data with pandas types
        df = pd.DataFrame(
            {"date": pd.date_range("2024-01-01", periods=3), "value": [1, 2, 3]}
        )

        document_data = {
            "metadata": {"created": pd.Timestamp.now(), "total_records": len(df)},
            "data": df.to_dict("records"),
            "summary": {
                "mean_value": float(df["value"].mean()),
                "date_range": {
                    "start": str(df["date"].min()),
                    "end": str(df["date"].max()),
                },
            },
        }

        # Save as JSON document (should handle pandas types automatically)
        saved_path, _ = file_utils.save_document_to_storage(
            content=document_data,
            output_filetype=OutputFileType.JSON,
            output_type="processed",
            file_name="pandas_document",
            include_timestamp=False,
        )

        assert Path(saved_path).exists()

        # Load and verify
        loaded_data = file_utils.load_document_from_storage(
            file_path="pandas_document.json", input_type="processed"
        )

        assert isinstance(loaded_data["metadata"]["created"], str)
        assert loaded_data["summary"]["mean_value"] == 2.0
        assert len(loaded_data["data"]) == 3

    def test_document_timestamp_handling(self, file_utils):
        """Test timestamp handling for documents."""
        content = "Test document for timestamp handling"

        # Save with timestamp
        saved_path, _ = file_utils.save_document_to_storage(
            content=content,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="timestamped_doc",
            include_timestamp=True,
        )

        assert Path(saved_path).exists()
        # File should have timestamp in name
        assert "_" in Path(saved_path).stem

        # Load using base name (should find timestamped version)
        loaded_content = file_utils.load_document_from_storage(
            file_path="timestamped_doc.md", input_type="processed"
        )

        assert loaded_content == content
