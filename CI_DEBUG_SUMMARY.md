# CI Test Failure Debugging Guide

## Problem Summary

The CI workflow was failing because PDF tests were running even when PyMuPDF (the required dependency) wasn't installed. This happened when the CI matrix ran tests without the `[documents]` extra dependency.

## Root Cause

The PDF tests (`test_save_pdf_simple_text`, `test_save_pdf_structured`, `test_load_pdf`) in `tests/unit/test_document_types.py` didn't have skip markers to check if PyMuPDF was available. When CI ran tests without installing `[documents]`, these tests would fail with `ModuleNotFoundError: No module named 'fitz'`.

## Solution Applied

Added `@pytest.mark.skipif` decorators to all three PDF tests to skip them when PyMuPDF is not installed:

```python
# Helper function added
def _pymupdf_available():
    """Check if PyMuPDF (fitz) is available."""
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        return False

# Applied to all PDF tests
@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
def test_save_pdf_simple_text(self, file_utils):
    ...

@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
def test_save_pdf_structured(self, file_utils):
    ...

@pytest.mark.skipif(not _pymupdf_available(), reason="PyMuPDF not installed")
def test_load_pdf(self, file_utils):
    ...
```

## How to Access GitHub CI Workflow Logs

### Method 1: Through GitHub Web Interface

1. Go to your repository on GitHub
2. Click on the **Actions** tab
3. Select the workflow run you want to investigate
4. Click on the failed job (e.g., "test (ubuntu-latest, 3.11, '')")
5. Expand the failed step to see the error output
6. Click on any step to see detailed logs

### Method 2: Using GitHub CLI

```bash
# List recent workflow runs
gh run list

# View logs for a specific run
gh run view <run-id> --log

# Watch a workflow run in real-time
gh run watch
```

### Method 3: Download Logs Programmatically

```bash
# Get the latest failed run
gh run list --limit 1 --json databaseId --jq '.[0].databaseId' | xargs gh run view --log
```

## Testing Locally (Mirrors CI)

To replicate CI conditions locally:

```bash
# Test without documents dependency (mirrors CI matrix entry)
pip install -e .
pytest tests/unit/ -v

# Test with documents dependency
pip install -e .[documents]
pytest tests/unit/ -v

# Test with all dependencies
pip install -e .[all]
pytest tests/unit/ -v
```

## CI Workflow Matrix

The CI workflow runs tests across multiple configurations:

- **OS**: Ubuntu, macOS, Windows
- **Python**: 3.11, 3.12
- **Extras**: `""`, `[excel]`, `[parquet]`, `[documents]`, `[all]`

When extras is empty (`""`), PDF tests will now correctly skip instead of failing.

## Verification

After the fix:
- ✅ All 87 unit tests pass
- ✅ PDF tests skip gracefully when PyMuPDF is not installed
- ✅ PDF tests run when PyMuPDF is installed (with `[documents]` extra)

## Next Steps

1. **Push the changes** to trigger CI
2. **Monitor the workflow** in GitHub Actions
3. **Verify** that tests pass across all matrix combinations
4. **Check** that PDF tests skip when `[documents]` is not installed
5. **Confirm** that PDF tests run when `[documents]` is installed

## Future Improvements

Consider adding similar skip markers for other optional dependencies:
- Excel tests when `openpyxl` is not installed
- Parquet tests when `pyarrow` is not installed
- DOCX tests when `python-docx` is not installed

This ensures tests are robust across all CI matrix combinations.

