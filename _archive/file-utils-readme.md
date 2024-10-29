# FileUtils

FileUtils is a Python utility class for handling file operations in data science projects. It provides methods for loading, saving, and managing data files, as well as organizing project directory structures.

## Project Structure

FileUtils assumes and manages the following project structure:

```
project_root/
│
├── input/
│   ├── raw/
│   ├── configurations/
│   └── external/
│
├── output/
│   ├── interim/
│   │   └── configurations/
│   ├── processed/
│   ├── reports/
│   ├── figures/
│   └── models/
│
├── notebooks/
│
├── src/
│   └── file_utils.py
│
└── config.py (or other root indicators)
```

## Installation

1. Ensure you have Python 3.6 or later installed on your system.

2. Install the required dependencies:

   ```
   pip install pandas tqdm xlsxwriter openpyxl
   ```

3. Save the `file_utils.py` file in your project's `src` directory.

## Usage

Here's a basic example of how to use the FileUtils class:

```python
from src.file_utils import FileUtils

# Initialize the FileUtils object
file_utils = FileUtils()

# Load data from the input directory
df = file_utils.load_data("my_data.csv", input_type="raw")

# Save processed data to the output directory
file_utils.save_data_to_disk({"processed_data": df}, output_type="processed")

# Save a figure as an Excel file
file_utils.save_dataframe_to_excel(df, "my_figure", output_type="figures")
```

## Main Features

1. **Project Structure Management**: Automatically creates and manages a standardized project directory structure.
2. **Data Loading**: Supports loading data from Excel and CSV files with progress bars for large files.
3. **Data Saving**: Saves DataFrames to CSV and Excel files, with options for multiple sheets and parameter information.
4. **Input/Output Organization**: Organizes input and output files into different categories (raw, external, configurations, interim, processed, reports, figures, models).

## API Reference

### `FileUtils(project_root=None)`

Initializes the FileUtils object.

- `project_root` (str, optional): The root directory of the project. If not provided, it will be determined automatically.

### `load_data(file_path, input_type="raw", csv_delimiter=",", encoding="utf-8", sheet_name=None)`

Loads data from Excel or CSV files with a progress bar.

- `file_path` (str or Path): Path to the file to be loaded, relative to the input type directory.
- `input_type` (str): The type of input being loaded ("raw" or "external").
- `csv_delimiter` (str, optional): Delimiter to use for CSV files. Defaults to ",".
- `encoding` (str, optional): File encoding. Defaults to 'utf-8'.
- `sheet_name` (str or list, optional): Name(s) of Excel sheets to load. If None, loads all sheets.

Returns a pandas DataFrame or dict of DataFrames for Excel files with multiple sheets.

### `save_dataframe_to_excel(df, file_name, output_type="reports", sheet_name="Sheet1", keep_index=False)`

Saves a single DataFrame to an Excel file.

- `df` (pd.DataFrame): DataFrame to save.
- `file_name` (str): Filename to save under, without extension.
- `output_type` (str): The type of output ("figures", "models", "processed", or "reports").
- `sheet_name` (str, optional): Sheet name to save the DataFrame in. Defaults to "Sheet1".
- `keep_index` (bool, optional): Whether to include the index in the saved file. Defaults to False.

### `save_dataframes_to_excel(dataframes_dict, file_name, output_type="reports", parameters_dict=None, keep_index=False)`

Saves given dataframes and optional parameters to individual sheets in an Excel file.

- `dataframes_dict` (dict): Dictionary where keys are sheet names and values are dataframes to save.
- `file_name` (str): The base name for the Excel file to save, without extension.
- `output_type` (str): The type of output ("figures", "models", "processed", or "reports").
- `parameters_dict` (dict, optional): Dictionary containing parameters to be saved on a separate sheet.
- `keep_index` (bool, optional): Whether to include the index in the saved file. Defaults to False.

### `save_data_to_disk(data_dict, output_type="processed", subtype=None, create_metadata=True, csv_delimiter=";", quoting=csv.QUOTE_MINIMAL, verbose=False, include_timestamp=True)`

Save each dataset in the dictionary to a separate CSV file.

- `data_dict` (dict): Dictionary of DataFrames
- `output_type` (str): The type of output being saved ("interim", "processed", "reports", "figures", or "models").
- `subtype` (str, optional): A subtype for more specific categorization, especially for interim files.
- `create_metadata` (bool): Whether to create a JSON metadata file. Defaults to True.
- `csv_delimiter` (str): The delimiter to use for CSV files. Defaults to ";".
- `quoting` (int): The quoting behavior for CSV output. Defaults to csv.QUOTE_MINIMAL.
- `verbose` (bool): Whether to print detailed saving information. Defaults to False.
- `include_timestamp` (bool): Whether to include a timestamp in the filename. Defaults to True.

Returns:
- dict: Dictionary with data types as keys and file paths as values
- str or None: Path to metadata file if created, else None

### `load_data_from_disk(metadata_file=None, file_path=None, csv_delimiter=";", verbose=False)`

Load datasets from disk based on the metadata file or a specific file path.

- `metadata_file` (Path or str, optional): Path to the metadata JSON file
- `file_path` (Path or str, optional): Path to a specific CSV file to load
- `csv_delimiter` (str): The delimiter used in the CSV file. Defaults to ";".
- `verbose` (bool): Whether to print detailed loading information. Defaults to False.

Returns a dictionary of loaded DataFrames or a single DataFrame if file_path is provided.

## Error Handling

The FileUtils class includes comprehensive error checking:

- Raises `FileNotFoundError` if a specified file is not found.
- Raises `ValueError` for unsupported file types, empty files, or errors in reading files.
- Raises `TypeError` for incorrect input types in various methods.

## Notes

- The class automatically detects the project root directory based on common project indicators.
- All saved files include timestamps in their filenames for version control.
- CSV files are saved with proper quoting and loaded with newlines restored.
- Excel files can include multiple sheets and an optional parameters sheet.
- The class provides verbose options for detailed information during saving and loading operations.

## Contributing

If you'd like to contribute to this project, please feel free to submit a pull request or open an issue on the project's repository.

## License

This project is licensed under the MIT License.