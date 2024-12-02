# FileUtils

FileUtils is a Python utility class for handling file operations in data science projects. It provides robust methods for loading, saving, and managing data files in various formats, along with project directory structure management.

## Features

- Support for multiple file formats:
  - CSV (with delimiter inference)
  - Excel (single and multi-sheet)
  - Parquet
  - JSON
  - YAML

- Automated project structure management
- Configurable settings via YAML
- Comprehensive logging
- Timestamp-based file versioning
- Error handling and validation

## Installation

1. Ensure you have Python 3.6 or later installed.

2. Install required dependencies:
```bash
pip install pandas pyyaml xlsxwriter openpyxl pyarrow fastparquet jsonschema
```

3. Place the `file_utils.py` file in your project's source directory.

## Basic Usage

```python
from file_utils import FileUtils, OutputFileType

# Initialize FileUtils
file_utils = FileUtils()  # Automatically detects project root
# Or with specific paths:
# file_utils = FileUtils(project_root="path/to/project", config_file="path/to/config.yaml")

# Load data
df = file_utils.load_single_file("data.csv", input_type="raw")
yaml_data = file_utils.load_yaml("config.yaml", input_type="raw")
json_data = file_utils.load_json("data.json", input_type="raw")

# Save data
file_utils.save_data_to_disk(
    data=df,
    output_filetype=OutputFileType.CSV,
    output_type="processed",
    file_name="output_data"
)

# Save multiple DataFrames to Excel
dfs = {"sheet1": df1, "sheet2": df2}
file_utils.save_data_to_disk(
    data=dfs,
    output_filetype=OutputFileType.XLSX,
    output_type="processed",
    file_name="multi_sheet_output"
)
```

## Configuration

FileUtils uses a YAML configuration file. Default location is `config.yaml` in the project root.

Example configuration:
```yaml
csv_delimiter: ","
encoding: "utf-8"
quoting: 0  # csv.QUOTE_MINIMAL
include_timestamp: true
logging_level: "INFO"
disable_logging: false
directory_structure:
  data:
    - raw
    - interim
    - processed
  reports:
    - figures
    - outputs
  models: []
  src: []
parquet_compression: "snappy"
```

## Directory Structure

FileUtils manages the following directory structure by default:
```
project_root/
├── data/
│   ├── raw/         # Original data
│   ├── interim/     # Intermediate processing
│   └── processed/   # Final processed data
├── reports/
│   ├── figures/     # Generated graphics
│   └── outputs/     # Analysis outputs
├── models/          # Trained models
└── src/            # Source code
```

## API Reference

### Main Methods

#### Loading Data
- `load_single_file(file_path, input_type="raw")`: Load any supported file format
- `load_yaml(file_path, input_type="raw")`: Load YAML file
- `load_json(file_path, input_type="raw")`: Load JSON file
- `load_excel_sheets(file_path, input_type="raw")`: Load all Excel sheets
- `load_multiple_files(file_paths, input_type="raw")`: Load multiple files

#### Saving Data
- `save_data_to_disk(data, output_filetype, output_type="processed")`: Save data in any format
- `save_yaml(data, file_path, output_type="processed")`: Save YAML file
- `save_json(data, file_path, output_type="processed")`: Save JSON file
- `save_dataframes_to_excel(dataframes_dict, file_name, output_type="reports")`: Save multiple DataFrames to Excel

### Utility Methods
- `get_data_path(data_type="raw")`: Get path for specific data type
- `get_logger(name)`: Get configured logger instance
- `setup_directory_structure()`: Create project directory structure

## Error Handling

FileUtils includes comprehensive error handling:
- File existence validation
- Format validation
- Schema validation for configuration
- Proper exception handling with logging

## Command Line Interface

```bash
# Set up project structure
python -m file_utils setup --project-root /path/to/project

# Test logging
python -m file_utils test-logging
```

[Previous README content remains the same until License section, then add:]

## Testing

FileUtils includes a comprehensive test suite to ensure reliability and correct functionality.

### Running Tests

Basic test execution:
```bash
python -m unittest test_file_utils.py
```

With verbose output:
```bash
python -m unittest -v test_file_utils.py
```

### Test Structure

The test suite (`test_file_utils.py`) includes tests for:
- File loading and saving in all supported formats
- Configuration handling
- Error scenarios
- Timestamp functionality
- Directory structure management

### Writing Tests

Tests use Python's unittest framework. Here's an example of adding a new test:

```python
class TestFileUtils(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test config
        config_data = {
            "csv_delimiter": ",",
            "encoding": "utf-8",
            "quoting": 0,
            "include_timestamp": True,
            "logging_level": "INFO",
            "disable_logging": False,
            "directory_structure": {
                "data": ["raw", "interim", "processed"],
                "reports": ["figures", "outputs"],
                "models": [],
                "src": []
            }
        }
        
        # Create config file
        self.config_path = self.temp_dir / "config.yaml"
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f)
        
        # Initialize FileUtils
        self.file_utils = FileUtils(
            project_root=self.temp_dir,
            config_file=self.config_path
        )

    def tearDown(self):
        """Clean up after test."""
        # Force garbage collection to release file handles
        import gc
        gc.collect()
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_csv(self):
        """Example test: Test CSV saving and loading."""
        test_df = pd.DataFrame({
            'name': ['Alice', 'Bob'],
            'age': [25, 30]
        })
        
        # Save data
        result, _ = self.file_utils.save_data_to_disk(
            data=test_df,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="test_data",
            include_timestamp=False
        )
        
        saved_path = Path(next(iter(result.values())))
        
        # Load and verify
        loaded_df = self.file_utils.load_single_file(
            file_path=saved_path.name,
            input_type="processed"
        )
        
        pd.testing.assert_frame_equal(loaded_df, test_df)
```

### Test Guidelines

1. **Isolation**: Each test should create and use its own temporary directory
2. **Cleanup**: Always clean up temporary files in tearDown
3. **Resource Management**: 
   - Use context managers for file operations
   - Explicitly close file handles
   - Force garbage collection when needed
4. **Assertions**:
   - Use appropriate assertions for data types
   - Use pandas testing utilities for DataFrame comparisons
   - Include error case testing
5. **Configuration**:
   - Create fresh configuration for each test
   - Use minimal required configuration
   - Test with different configuration settings

### Common Testing Patterns

1. Testing file operations:
```python
def test_file_operation(self):
    try:
        # Perform operation
        result = self.file_utils.some_operation()
        
        # Verify result
        self.assertEqual(expected, result)
    finally:
        # Clean up references
        if 'result' in locals():
            del result
        gc.collect()
```

2. Testing error conditions:
```python
def test_error_condition(self):
    with self.assertRaises(ExpectedException):
        self.file_utils.operation_that_should_fail()
```

3. Testing with DataFrames:
```python
def test_dataframe_operation(self):
    df = pd.DataFrame(...)
    try:
        result = self.file_utils.process_dataframe(df)
        pd.testing.assert_frame_equal(result, expected)
    finally:
        del df
        if 'result' in locals():
            del result
        gc.collect()
```

### Test Coverage

Future improvements will include test coverage reporting using the `coverage` package:

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest test_file_utils.py

# Generate coverage report
coverage report
coverage html  # For detailed HTML report
```

[Rest of README content remains the same]

## License

This project is open-source and available under the MIT License.