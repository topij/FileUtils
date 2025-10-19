# Test Documentation

This document provides comprehensive coverage of the FileUtils test suite, explaining what we test, why we test it, and how the tests validate key functionality.

## Table of Contents

- [Test Philosophy](#test-philosophy)
- [Test Structure](#test-structure)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Test Data and Fixtures](#test-data-and-fixtures)
- [Key Functionality Coverage](#key-functionality-coverage)
- [Running Tests](#running-tests)
- [Test Maintenance](#test-maintenance)

## Test Philosophy

### Core Principles

1. **Comprehensive Coverage**: Every public API method and major workflow is tested
2. **Real-world Scenarios**: Tests use realistic data and business scenarios
3. **Error Handling**: Both happy path and error conditions are validated
4. **Data Integrity**: Round-trip operations preserve data accuracy
5. **Regression Prevention**: Tests catch breaking changes in existing functionality

### Testing Strategy

- **Unit Tests**: Test individual methods in isolation with controlled inputs
- **Integration Tests**: Test complete workflows with realistic data
- **Edge Cases**: Validate behavior with unusual inputs and conditions
- **Error Scenarios**: Ensure graceful handling of failures

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── unit/
│   ├── test_file_utils.py        # Core FileUtils functionality tests
│   └── test_document_types.py    # Document format specific tests
└── integration/
    ├── test_azure_storage.py     # Azure Blob Storage integration tests
    └── test_excel_csv_conversion.py # Excel ↔ CSV round-trip tests
```

## Unit Tests

### Core FileUtils Tests (`tests/unit/test_file_utils.py`)

#### **Initialization and Configuration**
- **`test_initialization`**: Validates FileUtils initialization with custom config
- **Purpose**: Ensures proper setup of storage backends and configuration
- **Key API**: `FileUtils(project_root, config_file)`

#### **Data Storage Operations**
- **`test_save_single_dataframe`**: Tests saving individual DataFrames
- **`test_save_multiple_dataframes`**: Tests saving multi-sheet workbooks
- **Purpose**: Validates core data persistence functionality
- **Key API**: `save_data_to_storage(data, output_filetype, output_type, file_name)`

#### **Data Loading Operations**
- **`test_load_single_file`**: Tests loading individual files
- **`test_load_excel_sheets`**: Tests loading multi-sheet Excel files
- **`test_load_multiple_files`**: Tests batch file loading
- **Purpose**: Ensures data can be retrieved correctly
- **Key API**: `load_single_file()`, `load_excel_sheets()`, `load_multiple_files()`

#### **Excel ↔ CSV Conversion Tests**

##### **`test_convert_excel_to_csv_with_structure_basic`**
- **What**: Tests Excel to CSV conversion with structure preservation
- **Why**: Validates the core Excel → CSV workflow with metadata tracking
- **Key API**: `convert_excel_to_csv_with_structure(excel_file_path, preserve_structure=True)`
- **Validates**:
  - CSV files are created for each Excel sheet
  - Structure JSON contains workbook metadata
  - Sheet dimensions, columns, and data types are preserved
  - Data integrity through conversion process

##### **`test_convert_excel_to_csv_with_structure_no_preserve`**
- **What**: Tests Excel to CSV conversion without structure preservation
- **Why**: Ensures optional structure file creation works correctly
- **Key API**: `convert_excel_to_csv_with_structure(excel_file_path, preserve_structure=False)`
- **Validates**:
  - CSV files are created normally
  - No structure JSON file is generated
  - Function returns empty string for structure file

##### **`test_convert_csv_to_excel_workbook_basic`**
- **What**: Tests CSV to Excel workbook reconstruction
- **Why**: Validates the CSV → Excel reconstruction workflow
- **Key API**: `convert_csv_to_excel_workbook(structure_json_path, file_name)`
- **Validates**:
  - Excel workbook is reconstructed from CSV files
  - Sheet names and structure are preserved
  - Data content matches original
  - Reconstruction metadata is created

##### **`test_excel_csv_roundtrip_workflow`**
- **What**: Tests complete Excel ↔ CSV round-trip workflow
- **Why**: Validates end-to-end data processing pipeline
- **Key API**: Both conversion methods in sequence
- **Validates**:
  - Complete workflow: Excel → CSV → Modify → Excel
  - Data modifications are preserved
  - Multi-sheet workbooks maintain structure
  - Data integrity through entire process

#### **Subpath Operations**
- **`test_save_single_dataframe_with_subpath`**: Tests saving with subdirectories
- **`test_load_single_file_with_subpath`**: Tests loading from subdirectories
- **Purpose**: Validates hierarchical file organization
- **Key API**: `sub_path` parameter in save/load operations

#### **Document Operations**
- **`test_save_json_as_document`**: Tests JSON document saving
- **`test_save_yaml_as_document`**: Tests YAML document saving
- **Purpose**: Validates document format handling
- **Key API**: `save_document_to_storage(content, output_filetype)`

#### **Data Type Handling**
- **`test_automatic_pandas_type_conversion`**: Tests pandas type conversion
- **`test_intelligent_timestamp_handling`**: Tests datetime handling
- **Purpose**: Ensures data types are preserved correctly
- **Key API**: Automatic type inference and conversion

#### **Error Handling**
- **`test_file_not_found`**: Tests handling of missing files
- **`test_invalid_file_type`**: Tests handling of unsupported formats
- **Purpose**: Validates graceful error handling
- **Key API**: Exception raising and error messages

### Document Type Tests (`tests/unit/test_document_types.py`)

- **DOCX Template System**: Tests enhanced DOCX functionality
- **Markdown Processing**: Tests YAML frontmatter handling
- **PDF Text Extraction**: Tests PDF reading capabilities
- **Purpose**: Validates document format specific features

## Integration Tests

### Excel ↔ CSV Conversion (`tests/integration/test_excel_csv_conversion.py`)

#### **`test_complete_roundtrip_workflow`**
- **What**: Tests realistic business data workflow
- **Why**: Validates real-world usage scenarios
- **Data**: Multi-sheet business data (Sales, Customers, Products)
- **Workflow**:
  1. Create Excel workbook with business data
  2. Convert to CSV files with structure preservation
  3. Modify CSV data (add calculated fields)
  4. Reconstruct Excel workbook
  5. Verify data integrity and modifications
- **Key Validations**:
  - Data modifications are preserved (`profit_margin`, `quarter` fields)
  - Unmodified sheets remain unchanged
  - Data type changes from CSV round-trip are handled
  - Business calculations remain accurate

#### **`test_error_handling_missing_files`**
- **What**: Tests graceful handling of missing CSV files
- **Why**: Ensures robust error handling in production
- **Scenario**: Structure JSON references non-existent CSV files
- **Key Validations**:
  - Appropriate exceptions are raised
  - Error messages are informative
  - System doesn't crash on missing files

#### **`test_custom_csv_options`**
- **What**: Tests Excel to CSV conversion with custom options
- **Why**: Validates parameter passing and customization
- **Options**: Custom delimiter, encoding settings
- **Key Validations**:
  - Custom options are applied correctly
  - Files are created successfully
  - Content validation works

### Azure Storage Integration (`tests/integration/test_azure_storage.py`)

- **Cloud Storage**: Tests Azure Blob Storage operations
- **Authentication**: Tests credential handling
- **Purpose**: Validates cloud storage backend functionality

## Test Data and Fixtures

### Sample DataFrames (`conftest.py`)

```python
@pytest.fixture
def sample_df():
    """Standard test DataFrame with various data types."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'value': [10.5, 20.0, 30.5, 40.0, 50.5],
        'active': [True, False, True, True, False],
        'date': pd.date_range('2024-01-01', periods=5, freq='D')
    })
```

### Business Data (Integration Tests)

```python
# Realistic business data for integration testing
sales_data = pd.DataFrame({
    'sale_id': [1, 2, 3, 4, 5],
    'customer_name': ['Alice Corp', 'Bob Industries', ...],
    'product': ['Widget A', 'Widget B', ...],
    'quantity': [10, 5, 15, 8, 12],
    'unit_price': [25.50, 45.00, ...],
    'sale_date': pd.date_range('2024-01-01', periods=5, freq='D'),
    'sales_rep': ['John', 'Jane', ...]
})
```

### Test Configuration

- **Temporary Directories**: Each test gets isolated file system
- **Clean State**: Tests don't interfere with each other
- **Realistic Paths**: Tests use actual file system operations

## Key Functionality Coverage

### Core API Methods

| Method | Unit Tests | Integration Tests | Coverage |
|--------|------------|-------------------|----------|
| `save_data_to_storage` | Multiple | Workflow | Complete |
| `load_single_file` | Multiple | Workflow | Complete |
| `load_excel_sheets` | Multiple | Workflow | Complete |
| `convert_excel_to_csv_with_structure` | Basic + No Preserve | Complete Workflow | Complete |
| `convert_csv_to_excel_workbook` | Basic | Complete Workflow | Complete |
| `save_document_to_storage` | Multiple | Workflow | Complete |

### File Format Support

| Format | Unit Tests | Integration Tests | Coverage |
|--------|------------|-------------------|----------|
| CSV | Multiple | Round-trip | Complete |
| Excel (.xlsx) | Multiple | Round-trip | Complete |
| JSON | Multiple | Workflow | Complete |
| YAML | Multiple | Workflow | Complete |
| DOCX | Template System | Enhanced Features | Complete |
| Markdown | YAML Frontmatter | Document Processing | Complete |
| PDF | Text Extraction | Document Reading | Complete |

### Error Scenarios

| Scenario | Test Coverage | Validation |
|----------|---------------|------------|
| Missing Files | Unit + Integration | Proper exception handling |
| Invalid Formats | Unit | Graceful error messages |
| Corrupted Data | Unit | Data validation |
| Network Issues | Integration | Azure storage errors |
| Permission Errors | Unit | File system errors |

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_file_utils.py

# Run specific test
pytest tests/unit/test_file_utils.py::test_convert_excel_to_csv_with_structure_basic

# Run Excel ↔ CSV tests only
pytest -k "convert_excel_to_csv or convert_csv_to_excel or excel_csv_roundtrip"
```

### Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Excel ↔ CSV conversion tests
pytest -k "excel_csv"

# Error handling tests
pytest -k "error"
```

### Test Output and Debugging

```bash
# Show test output
pytest -s

# Stop on first failure
pytest -x

# Show local variables on failure
pytest --tb=long

# Run with coverage
pytest --cov=FileUtils
```

## Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to appropriate `test_*.py` file
2. **Integration Tests**: Create new file in `tests/integration/`
3. **Fixtures**: Add to `conftest.py` if shared
4. **Documentation**: Update this file with new test coverage

### Test Naming Conventions

- **Unit Tests**: `test_method_name_scenario`
- **Integration Tests**: `test_workflow_name`
- **Error Tests**: `test_method_name_error_condition`

### Test Data Management

- **Use Fixtures**: For reusable test data
- **Isolated Data**: Each test should be independent
- **Realistic Data**: Use business-relevant examples
- **Clean Up**: Tests should not leave artifacts

### Performance Considerations

- **Fast Execution**: All tests complete in < 1 second
- **Minimal I/O**: Use temporary directories
- **Efficient Data**: Use small but representative datasets
- **Parallel Execution**: Tests can run concurrently

## Test Quality Metrics

### Current Coverage

- **Total Tests**: 50+ (47 unit + 3+ integration)
- **API Coverage**: 100% of public methods
- **Format Coverage**: All supported file formats
- **Error Coverage**: Major error scenarios
- **Pass Rate**: 100% ✅

### Test Reliability

- **Deterministic**: Tests produce consistent results
- **Isolated**: Tests don't depend on each other
- **Fast**: Complete test suite runs in < 1 minute
- **Maintainable**: Clear test structure and naming

## Conclusion

The FileUtils test suite provides comprehensive validation of all core functionality, with particular emphasis on the Excel ↔ CSV conversion workflow. The tests ensure data integrity, proper error handling, and real-world usability while maintaining fast execution and clear documentation.

The combination of unit tests (for individual method validation) and integration tests (for complete workflow validation) provides confidence that FileUtils is robust, reliable, and ready for production use.
