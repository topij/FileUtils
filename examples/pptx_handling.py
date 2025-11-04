"""Example demonstrating PPTX file handling with FileUtils."""

import zipfile
import io
from pathlib import Path
from FileUtils import FileUtils, OutputFileType


def create_minimal_pptx():
    """Create a minimal valid PPTX file in memory for testing."""
    pptx_buffer = io.BytesIO()
    with zipfile.ZipFile(pptx_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Minimal PPTX structure (PPTX is a ZIP archive)
        zip_file.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
</Types>""",
        )
        zip_file.writestr(
            "_rels/.rels",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>""",
        )
        zip_file.writestr(
            "ppt/presentation.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
    <p:sldIdLst>
        <p:sldId id="256" r:id="rId1"/>
    </p:sldIdLst>
</p:presentation>""",
        )

    return pptx_buffer.getvalue()


def demonstrate_pptx_handling():
    """Demonstrate PPTX file handling with FileUtils."""
    # Initialize FileUtils
    file_utils = FileUtils()

    print("=== FileUtils PPTX Handling Demo ===\n")
    print("Note: PPTX support handles raw files only.")
    print("For creating/editing slides, use python-pptx library.\n")

    # 1. Save PPTX from bytes
    print("1. Saving PPTX from bytes")
    print("-" * 40)

    # Create a minimal PPTX file in memory
    pptx_bytes = create_minimal_pptx()
    print(f"✓ Created PPTX in memory ({len(pptx_bytes)} bytes)")

    # Save using FileUtils
    saved_path, _ = file_utils.save_document_to_storage(
        content=pptx_bytes,
        output_filetype=OutputFileType.PPTX,
        output_type="processed",
        file_name="demo_presentation",
        sub_path="presentations/demo",
        include_timestamp=False,
    )
    print(f"✓ Saved PPTX: {saved_path}")

    # Verify the file exists and is valid
    if Path(saved_path).exists():
        print(f"✓ File verified: {Path(saved_path).stat().st_size} bytes")
        # Verify it's a valid ZIP file (PPTX is a ZIP archive)
        if zipfile.is_zipfile(saved_path):
            print("✓ Valid PPTX file (ZIP archive verified)")

    # 2. Save PPTX from file path
    print("\n2. Saving PPTX from file path")
    print("-" * 40)

    # Use the previously saved file as source
    source_path = saved_path
    if Path(source_path).exists():
        saved_from_path, _ = file_utils.save_document_to_storage(
            content=source_path,
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="copied_presentation",
            sub_path="presentations/copies",
            include_timestamp=False,
        )
        print(f"✓ Copied PPTX from: {source_path}")
        print(f"✓ Saved to: {saved_from_path}")

        # Verify files are identical
        if Path(saved_from_path).exists():
            original_size = Path(source_path).stat().st_size
            copied_size = Path(saved_from_path).stat().st_size
            if original_size == copied_size:
                print(f"✓ Files match: {original_size} bytes each")

    # 3. Load PPTX as bytes
    print("\n3. Loading PPTX as bytes")
    print("-" * 40)

    loaded_bytes = file_utils.load_document_from_storage(
        file_path="demo_presentation.pptx",
        input_type="processed",
        sub_path="presentations/demo",
    )

    print(f"✓ Loaded PPTX: {len(loaded_bytes)} bytes")
    print(f"✓ Type: {type(loaded_bytes).__name__}")

    # Verify loaded content is valid
    pptx_buffer_check = io.BytesIO(loaded_bytes)
    if zipfile.is_zipfile(pptx_buffer_check):
        print("✓ Loaded content is valid PPTX (ZIP archive verified)")

    # 4. Demonstrate round-trip
    print("\n4. Round-trip test (save → load → save)")
    print("-" * 40)

    # Save the loaded bytes again
    roundtrip_path, _ = file_utils.save_document_to_storage(
        content=loaded_bytes,
        output_filetype=OutputFileType.PPTX,
        output_type="processed",
        file_name="roundtrip_presentation",
        sub_path="presentations/roundtrip",
        include_timestamp=False,
    )
    print(f"✓ Round-trip saved: {roundtrip_path}")

    # Verify round-trip
    if Path(roundtrip_path).exists():
        original_size = len(pptx_bytes)
        roundtrip_size = Path(roundtrip_path).stat().st_size
        if original_size == roundtrip_size:
            print(f"✓ Round-trip verified: {original_size} bytes preserved")

    # 5. Error handling demonstration
    print("\n5. Error handling")
    print("-" * 40)

    from FileUtils.core.base import StorageError

    # Try to save invalid content type
    try:
        file_utils.save_document_to_storage(
            content="This is not valid PPTX content",
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="invalid_test",
            include_timestamp=False,
        )
        print("✗ Should have raised an error")
    except StorageError as e:
        print(f"✓ Correctly caught error: {str(e)[:60]}...")

    # Try to save from non-existent file path
    try:
        file_utils.save_document_to_storage(
            content="/nonexistent/path/file.pptx",
            output_filetype=OutputFileType.PPTX,
            output_type="processed",
            file_name="missing_file_test",
            include_timestamp=False,
        )
        print("✗ Should have raised an error")
    except StorageError as e:
        print(f"✓ Correctly caught error: {str(e)[:60]}...")

    print("\n=== Demo Complete ===")
    print("\nKey Takeaways:")
    print("• PPTX support works with bytes or file paths")
    print("• Loaded PPTX files are returned as bytes")
    print("• Use sub_path for organized file storage")
    print("• For creating/editing slides, use python-pptx library")
    print("• FileUtils handles the storage, not the slide content")


if __name__ == "__main__":
    demonstrate_pptx_handling()
