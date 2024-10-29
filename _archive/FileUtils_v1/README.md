# FileUtils Module

A comprehensive utility class for handling file operations in data science projects. The `FileUtils` module provides methods for loading, saving, and managing data files, as well as setting up directory structures and handling configurations.

## Features

- **File Operations**: Load and save data in various formats like CSV, Excel, and JSON.
- **Directory Management**: Automatically set up and manage project directory structures.
- **Configuration Handling**: Load configurations from a YAML file with default fallbacks and schema validation.
- **Logging**: Configurable logging using Python's `logging` module.
- **Error Handling**: Improved error handling with specific exceptions and informative messages.
- **Documentation**: Detailed docstrings and examples for each method.
- **PEP 8 Compliance**: Code adheres to PEP 8 style guidelines for readability and maintainability.

## Installation

Ensure you have the required packages installed:

```bash
pip install pandas PyYAML openpyxl jsonschema
```

## Usage

### Initializing FileUtils

```python
from file_utils import FileUtils

# Initialize with default settings
file_utils = FileUtils()

# Initialize with a specific project root or configuration file
file_utils = FileUtils(project_root='/path/to/project', config_file='config.yaml')
```

### Setting Up Directory Structure

```python
# Set up the directory structure defined in the configuration
FileUtils.setup_directory_structure('/path/to/project')
```

### Loading Data

```python
# Load a single file
df = file_utils.load_single_file('data.csv', input_type='raw')

# Load multiple files
dataframes = file_utils.load_multiple_files(['data1.csv', 'data2.csv'], input_type='processed')

# Load data from a metadata file
dataframes = file_utils.load_data_from_metadata('metadata.json', input_type='raw')

# Load all sheets from an Excel file into a dictionary of DataFrames
sheets = file_utils.load_excel_sheets('data.xlsx', input_type='raw')

# Access individual DataFrames by sheet name
df_sheet1 = sheets['Sheet1']
df_sheet2 = sheets['Sheet2']

# Load multiple CSV files based on a metadata JSON file
dataframes = file_utils.load_csvs_from_metadata('metadata.json', input_type='raw')

# Access individual DataFrames by key
df1 = dataframes.get('file1')
df2 = dataframes.get('file2')
```

### Saving Data

```python
from file_utils import OutputFileType

# Save a single DataFrame
file_utils.save_data_to_disk(df, output_filetype=OutputFileType.CSV, output_type='processed', file_name='output')

# Save multiple DataFrames
data = {'sheet1': df1, 'sheet2': df2}
file_utils.save_data_to_disk(data, output_filetype=OutputFileType.XLSX, file_name='multi_sheet')

# Save data with additional parameters
parameters = {'param1': 'value1', 'param2': 'value2'}
file_utils.save_dataframes_to_excel(data, 'output', parameters_dict=parameters)
```

### Logging

```python
# Get a logger and log messages
logger = file_utils.get_logger(__name__)
logger.info('This is an info message.')
```

## Configuration

You can customize the behavior of `FileUtils` using a `config.yaml` file placed in the project root directory or specified during initialization.

### Example `config.yaml`

```yaml
# Configuration settings for FileUtils

csv_delimiter: ","
encoding: "utf-8"
quoting: 0  # csv.QUOTE_MINIMAL
include_timestamp: true
logging_level: "DEBUG"
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
  src:
    - scripts
    - notebooks
```

## Dependencies

- Python 3.6 or higher
- pandas
- PyYAML
- openpyxl
- jsonschema

Install the dependencies using:

```bash
pip install -r requirements.txt
```

### `requirements.txt`

```
pandas>=1.0
PyYAML>=5.0
openpyxl>=3.0
jsonschema>=3.0
```

## License

This project is licensed under the MIT License.

## Contact

If you have any questions or need further assistance, please open an issue or contact the maintainer.

---

**Note:** Replace `/path/to/project` and file names with the actual paths and names relevant to your project.