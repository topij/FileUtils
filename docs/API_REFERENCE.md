# FileUtils API Reference

This document provides detailed information about the classes, methods, and options available in the FileUtils package.

## Important Concepts

### Automatic File Type Detection

FileUtils automatically detects file formats based on file extensions. When loading files, you don't need to specify the format - it's determined from the file extension (e.g., `.csv`, `.xlsx`, `.json`).

### Directory Types vs File Formats

- **Directory Types** (`input_type` and `output_type` parameters): These refer to the **directory names** where files are stored (like "raw", "processed", "interim"). They represent the purpose or stage of the data in your workflow, not the technical format of files.

- **File Formats** (`output_filetype` parameter): When saving data, you specify the desired file format using the `OutputFileType` enum (e.g., `CSV`, `XLSX`, `JSON`).

## Core Classes

### `FileUtils`

The main class providing unified file operations across different storage backends.

#### Constructor

```python
FileUtils(
    project_root: Optional[Union[str, Path]] = None,
    config_file: Optional[Union[str, Path]] = None,
    storage_type: Union[str, StorageType] = StorageType.LOCAL,
    log_level: Optional[str] = None,
    directory_structure: Optional[Dict[str, Any]] = None,
    config_override: Optional[Dict[str, Any]] = None,
    **kwargs
)
```

**Parameters:**

- `project_root`: Root directory for the project. Defaults to current directory if not specified.
- `config_file`: Path to YAML configuration file.
- `storage_type`: Type of storage backend (`"local"` or `"azure"`).
- `log_level`: Logging level (e.g., `"INFO"`, `"DEBUG"`).
- `directory_structure`: Dictionary defining directory structure.
- `config_override`: Dictionary to override any configuration values.
- `**kwargs`: Additional arguments for storage backend.
  - For Azure storage: `connection_string`, `container_name`
  - Common options: `create_directories` (bool)

#### Methods

##### `save_data_to_storage`

Save DataFrame(s) to storage in various formats.

```python
save_data_to_storage(
    data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    output_filetype: Union[OutputFileType, str] = OutputFileType.CSV,
    output_type: str = "processed",
    file_name: Optional[str] = None,
    sub_path: Optional[Union[str, Path]] = None,
    include_timestamp: Optional[bool] = None,
    **kwargs
) -> Tuple[Dict[str, str], Optional[str]]
```

**Parameters:**

- `data`: DataFrame or dictionary of DataFrames (for multi-sheet Excel).
- `output_filetype`: File format to save data in (e.g., CSV, XLSX, JSON).
- `output_type`: Directory name to save in (e.g., "raw", "processed") - not the file format.
- `file_name`: Base name for the file without extension.
- `sub_path`: Optional relative path for subdirectory within `output_type` directory.
- `include_timestamp`: Whether to include timestamp in filename.
- `**kwargs`: Format-specific options:
  - CSV: `sep`, `encoding`, `index`, `quoting`
  - Excel: `index`, `engine`
  - JSON: `orient`, `indent`, `force_ascii`
  - Parquet: `compression`, `engine`, `index`
  - YAML: `yaml_options`, `orient`

**Returns:**

- Tuple with dictionary mapping names to file paths and optional metadata path.

##### `load_single_file`

Load a single file as a DataFrame. The file format is automatically detected from the file extension.

```python
load_single_file(
    file_path: Union[str, Path],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> pd.DataFrame
```

**Parameters:**

- `file_path`: Path to file. If `sub_path` is provided, this should be the filename only. If `sub_path` is None, this is the path relative to the `input_type` directory.
- `input_type`: Directory name to load from (e.g., "raw", "processed") - not the file format.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Format-specific options for reading.

**Returns:**

- DataFrame containing file data.

##### `load_excel_sheets`

Load all sheets from an Excel file.

```python
load_excel_sheets(
    file_path: Union[str, Path],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Dict[str, pd.DataFrame]
```

**Parameters:**

- `file_path`: Path to Excel file. If `sub_path` is provided, this should be the filename only. If `sub_path` is None, this is the path relative to the `input_type` directory.
- `input_type`: Directory name to load from - not the file format.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional options for pd.read_excel.

**Returns:**

- Dictionary mapping sheet names to DataFrames.

##### `load_multiple_files`

Load multiple files into a dictionary of DataFrames. File formats are automatically detected from extensions.

```python
load_multiple_files(
    file_paths: List[Union[str, Path]],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    file_type: Optional[OutputFileType] = None,
    **kwargs
) -> Dict[str, pd.DataFrame]
```

**Parameters:**

- `file_paths`: List of file paths. If `sub_path` is provided, these should be filenames only. If `sub_path` is None, these are paths relative to the `input_type` directory.
- `input_type`: Directory name to load from - not the file format.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `file_type`: Optional file type override if auto-detection should be bypassed.
- `**kwargs`: Additional options passed to the underlying `load_single_file` calls.

**Returns:**

- Dictionary mapping file names to DataFrames.

##### `save_with_metadata`

Save DataFrames with a metadata file for tracking.

```python
save_with_metadata(
    data: Dict[str, pd.DataFrame],
    output_filetype: OutputFileType = OutputFileType.CSV,
    output_type: str = "processed",
    file_name: Optional[str] = None,
    include_timestamp: Optional[bool] = None,
    **kwargs
) -> Tuple[Dict[str, str], str]
```

**Parameters:**

- Same as `save_data_to_storage`, with `output_type` referring to the directory name.

**Returns:**

- Tuple with saved file paths and path to metadata file.

##### `load_from_metadata`

Load data using a previously created metadata file.

```python
load_from_metadata(
    metadata_path: Union[str, Path],
    input_type: str = "raw",
    **kwargs
) -> Dict[str, pd.DataFrame]
```

**Parameters:**

- `metadata_path`: Path to metadata JSON file.
- `input_type`: Directory name to load from - not the file format.
- `**kwargs`: Format-specific options.

**Returns:**

- Dictionary of DataFrames loaded according to metadata.

##### `load_yaml`

Load YAML file content.

```python
load_yaml(
    file_path: Union[str, Path],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Any
```

**Parameters:**

- `file_path`: Path to YAML file. If `sub_path` is provided, this should be the filename only. If `sub_path` is None, this is the path relative to the `input_type` directory.
- `input_type`: Directory name to load from - not the file format.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional options passed to `yaml.safe_load` or the storage backend.

**Returns:**

- Parsed YAML content.

##### `load_json`

Load JSON file content.

```python
load_json(
    file_path: Union[str, Path],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Any
```

**Parameters:**

- `file_path`: Path to JSON file. If `sub_path` is provided, this should be the filename only. If `sub_path` is None, this is the path relative to the `input_type` directory.
- `input_type`: Directory name to load from - not the file format.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional options passed to `json.load` or the storage backend.

**Returns:**

- Parsed JSON content.

##### `get_data_path`

Get path to a specific data directory.

```python
get_data_path(data_type: str = "raw") -> Path
```

**Parameters:**

- `data_type`: Directory name to access (e.g., "raw", "processed").

**Returns:**

- Path object for the specified directory.

##### `create_directory`

Create a new directory within the configured structure.

```python
create_directory(
    directory_name: str,
    parent_dir: str = "data"
) -> Path
```

**Parameters:**

- `directory_name`: Name of the directory to create.
- `parent_dir`: Parent directory name.

**Returns:**

- Path to the created directory.

##### `get_config`

Get current configuration.

```python
get_config() -> Dict[str, Any]
```

**Returns:**

- Copy of current configuration dictionary.

##### `set_logging_level`

Set logging level for the FileUtils instance.

```python
set_logging_level(level: str) -> None
```

**Parameters:**

- `level`: Logging level (e.g., "DEBUG", "INFO", "WARNING").

##### `save_document_to_storage`

Save document content using configured storage backend. Supports rich document formats including DOCX, Markdown, PDF, JSON, and YAML.

```python
save_document_to_storage(
    content: Union[str, Dict[str, Any]],
    output_filetype: Union[OutputFileType, str],
    output_type: str = "processed",
    file_name: Optional[str] = None,
    sub_path: Optional[Union[str, Path]] = None,
    include_timestamp: Optional[bool] = None,
    **kwargs
) -> Tuple[str, Optional[str]]
```

**Parameters:**

- `content`: Document content (string, dict, or structured content).
- `output_filetype`: Type of output file (DOCX, MARKDOWN, PDF, JSON, YAML).
- `output_type`: Directory name to save in (e.g., "raw", "processed").
- `file_name`: Base name for the file without extension.
- `sub_path`: Optional relative path for subdirectory within `output_type` directory.
- `include_timestamp`: Whether to include timestamp in filename.
- `**kwargs`: Additional arguments for storage backend.

**Returns:**

- Tuple with saved file path and optional metadata path.

**Raises:**

- `ValueError`: If output_filetype is not a document format.
- `StorageError`: If saving fails.

**Enhanced Features:**

- **Automatic Type Conversion**: For JSON files, pandas Timestamps, NumPy types, and datetime objects are automatically converted to JSON-serializable formats.
- **Structured Content Support**: Supports both simple strings and complex structured content for DOCX and PDF files.
- **YAML Frontmatter**: Markdown files support structured metadata in YAML frontmatter format.

##### `load_document_from_storage`

Load document content from storage with intelligent timestamp handling.

```python
load_document_from_storage(
    file_path: Union[str, Path],
    input_type: str = "raw",
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Union[str, Dict[str, Any]]
```

**Parameters:**

- `file_path`: Path to file. If `sub_path` is provided, this should be the filename only.
- `input_type`: Directory name to load from (e.g., "raw", "processed").
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional arguments passed to storage backend.

**Returns:**

- Document content (string or dict depending on file type).

**Raises:**

- `StorageError`: If loading fails.
- `ValueError`: If sub_path is provided and file_path also contains path separators.

**Enhanced Features:**

- **Intelligent Timestamp Handling**: If the exact file doesn't exist, automatically searches for files with timestamps matching the base name pattern.
- **Format-Specific Parsing**: Returns appropriate data types based on file format (string for Markdown/PDF, dict for structured content).
- **YAML Frontmatter Parsing**: Markdown files with frontmatter return structured dictionaries with separate `frontmatter` and `body` keys.

## Enums

### `OutputFileType`

Enumeration of supported file types.

```python
class OutputFileType(Enum):
    # Tabular data formats
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    PARQUET = "parquet"
    
    # Multi-purpose formats (both tabular and document)
    JSON = "json"      # Can be used for DataFrames or structured documents
    YAML = "yaml"      # Can be used for DataFrames or structured documents
    
    # Document formats
    DOCX = "docx"
    MARKDOWN = "md"
    PDF = "pdf"
```

**Format Usage Guidelines:**

- **Tabular Data**: Use `save_data_to_storage()` for CSV, XLSX, XLS, PARQUET
- **Document Data**: Use `save_document_to_storage()` for DOCX, MARKDOWN, PDF
- **Flexible Formats**: JSON and YAML can be used with either method:
  - Use `save_data_to_storage()` for DataFrame content
  - Use `save_document_to_storage()` for structured documents/configurations

### `StorageType`

Enumeration of supported storage backends.

```python
class StorageType(Enum):
    LOCAL = "local"
    AZURE = "azure"
```

## Storage Classes

### `BaseStorage`

Abstract base class for storage implementations.

### `LocalStorage`

Implementation for local file system operations.

### `AzureStorage`

Implementation for Azure Blob Storage operations.

## Configuration Options

### Default Configuration

```python
{
    "directory_structure": {"data": ["raw", "processed"]},
    "csv_delimiter": ";",
    "encoding": "utf-8",
    "quoting": 0,  # csv.QUOTE_MINIMAL
    "include_timestamp": True
}
```

### Format-Specific Options

#### CSV Options

- `sep` / `delimiter`: Column separator (default: ";")
- `encoding`: File encoding (default: "utf-8")
- `index`: Whether to include DataFrame index (default: False)
- `quoting`: CSV quoting style (default: csv.QUOTE_MINIMAL)

#### Excel Options

- `index`: Whether to include DataFrame index (default: False)
- `engine`: Excel engine ("openpyxl" or "xlsxwriter")

#### JSON Options

- `orient`: Orientation of the data ("records", "index", "columns", etc.)
- `indent`: Indentation level for pretty printing
- `force_ascii`: Whether to ensure ASCII output

#### Parquet Options

- `compression`: Compression algorithm ("snappy", "gzip", "brotli", etc.)
- `engine`: Parquet engine ("auto", "pyarrow", "fastparquet")
- `index`: Whether to include DataFrame index

#### YAML Options

- `yaml_options`: Dictionary of options for yaml.dump
- `orient`: Orientation of the data ("records", "index", etc.)

## Enhanced Features

### Automatic Type Conversion

FileUtils includes an enhanced JSON encoder (`PandasJSONEncoder`) that automatically handles common data science data types:

#### Supported Conversions

- **Pandas Timestamps**: Converted to ISO format strings (`2024-01-01T00:00:00`)
- **NumPy Types**: Converted using `.item()` method
- **NumPy Arrays**: Converted using `.tolist()` method  
- **Datetime Objects**: Converted using `.isoformat()` method

#### Usage

The automatic conversion is applied when using `save_document_to_storage()` with JSON format:

```python
import pandas as pd
import numpy as np

# Create data with pandas types
df = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=5),
    'value': np.random.randn(5),
    'category': ['A', 'B', 'C', 'D', 'E']
})

# This works without manual conversion!
json_data = {
    'metadata': {'created': pd.Timestamp.now()},
    'data': df.to_dict('records')
}

saved_path, _ = file_utils.save_document_to_storage(
    content=json_data,
    output_filetype=OutputFileType.JSON,
    output_type="processed",
    file_name="data_with_types"
)
```

#### Manual Override

If you need custom JSON serialization, you can still use the standard `json` module with custom encoders:

```python
import json
from datetime import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

# Use with standard json module
json_string = json.dumps(data, cls=CustomEncoder)
```

### Intelligent Timestamp Handling

FileUtils automatically handles timestamped files when loading:

#### Automatic File Discovery

When loading files, if the exact filename doesn't exist, FileUtils searches for files matching the pattern `{base_name}_*{extension}` and loads the most recent one:

```python
# Save with timestamp
saved_path, _ = file_utils.save_document_to_storage(
    content=content,
    output_filetype=OutputFileType.JSON,
    file_name="report"  # Creates: report_20241018_143022.json
)

# Load by base name (finds the timestamped file automatically)
loaded_data = file_utils.load_json(
    file_path="report.json",  # Loads: report_20241018_143022.json
    input_type="processed"
)
```

#### Supported Methods

Timestamp handling is available for:
- `load_document_from_storage()`
- `load_single_file()`
- `load_json()`
- `load_yaml()` 