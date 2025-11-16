# API Reference

## New and Updated APIs (v0.8)

- Storage interfaces
  - `BaseStorage.save_dataframe(df, file_path, **kwargs)` infers format from `file_path` suffix.
  - `BaseStorage.save_dataframes(dataframes, file_path, file_format: Optional[str] = None, **kwargs)` infers format from suffix; `file_format` is deprecated.

- Convenience
  - `FileUtils.save_bytes(content: bytes, file_stem: str, *, sub_path: str | Path | None = None, output_type: str | OutputArea = 'processed', file_ext: str = 'png', include_timestamp: bool | None = None, root_level: bool = False) -> str`
  - `FileUtils.open_run(sub_path_prefix: str, customer: str, *, fmt: str = '%Y%m%d-%H%M%S') -> tuple[str, str]`

- Structured results
  - `SaveResult`: dataclass with fields `path`, `url`, `checksum`, `mimetype`.
  - `FileUtils.save_data_to_storage(..., structured_result=True)` returns `dict[str, SaveResult]`.
  - `FileUtils.save_document_to_storage(..., structured_result=True)` returns `SaveResult`.

- Typed enums for directories
  - `InputType` and `OutputArea` can be passed anywhere a directory type is accepted; strings still work.

- File system operations (v0.8.3+)
  - `FileUtils.file_exists(file_path, input_type=None, sub_path=None, root_level=False) -> bool`: Check if a file exists. Never raises exceptions.
  - `FileUtils.list_directory(directory_path=None, input_type=None, sub_path=None, pattern=None, root_level=False, files_only=False, directories_only=False) -> List[str]`: List files and directories. Never raises exceptions.
  - `FileUtils.create_directory(directory_path, input_type=None, sub_path=None, exist_ok=True, root_level=False, parent_dir=None) -> str`: Enhanced directory creation with new signature while maintaining backward compatibility.

## Deprecations

- Passing `file_format=` to `BaseStorage.save_dataframes` is deprecated and ignored if it disagrees with the path suffix.
- `utils.common.get_logger` is deprecated, use `utils.logging.setup_logger`.
- `FileUtils._get_default_config()` is deprecated; configuration defaults come from `config/default_config.yaml`.

## Python Version

- Official support: Python 3.11+.

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

##### `convert_excel_to_csv_with_structure`

Convert Excel file with multiple worksheets to CSV files while maintaining workbook structure.

```python
convert_excel_to_csv_with_structure(
    excel_file_path: Union[str, Path],
    input_type: str = "raw",
    output_type: str = "processed",
    file_name: Optional[str] = None,
    preserve_structure: bool = True,
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Tuple[Dict[str, str], str]
```

**Parameters:**

- `excel_file_path`: Path to Excel file. If `sub_path` is provided, this should be the filename only. If `sub_path` is None, this is the path relative to the `input_type` directory.
- `input_type`: Directory name to load from - not the file format.
- `output_type`: Directory name to save to - not the file format.
- `file_name`: Base name for output files (defaults to Excel filename without extension).
- `preserve_structure`: Whether to create a structure JSON file with workbook metadata.
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional arguments for CSV saving (encoding, delimiter, etc.).

**Returns:**

- Tuple of (csv_files_dict, structure_json_path):
  - `csv_files_dict`: Dictionary mapping sheet names to CSV file paths
  - `structure_json_path`: Path to the structure JSON file (empty string if preserve_structure=False)

**Example:**

```python
# Convert Excel workbook to CSV files with structure preservation
csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
    excel_file_path="workbook.xlsx",
    file_name="converted_workbook",
    preserve_structure=True
)

# Result:
# csv_files = {
#     "Sheet1": "data/processed/converted_workbook_Sheet1.csv",
#     "Sheet2": "data/processed/converted_workbook_Sheet2.csv"
# }
# structure_file = "data/processed/converted_workbook_structure.json"
```

**Structure JSON Format:**

The structure JSON file contains comprehensive metadata about the workbook:

```json
{
  "workbook_info": {
    "source_file": "workbook.xlsx",
    "conversion_timestamp": "2024-01-15T10:30:00",
    "total_sheets": 2,
    "sheet_names": ["Sheet1", "Sheet2"]
  },
  "sheets": {
    "Sheet1": {
      "csv_file": "data/processed/converted_workbook_Sheet1.csv",
      "csv_filename": "converted_workbook_Sheet1.csv",
      "dimensions": {
        "rows": 100,
        "columns": 5
      },
      "columns": {
        "names": ["id", "name", "value", "category", "date"],
        "dtypes": {"id": "int64", "name": "object", "value": "float64"},
        "count": 5
      },
      "data_info": {
        "has_index": false,
        "index_name": null,
        "memory_usage": 8192,
        "null_counts": {"name": 2, "value": 0}
      }
    }
  }
}
```

##### `convert_csv_to_excel_workbook`

Convert CSV files back to Excel workbook using structure JSON.

```python
convert_csv_to_excel_workbook(
    structure_json_path: Union[str, Path],
    input_type: str = "processed",
    output_type: str = "processed",
    file_name: Optional[str] = None,
    sub_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> str
```

**Parameters:**

- `structure_json_path`: Path to the structure JSON file created during CSV conversion.
- `input_type`: Directory name where CSV files are located.
- `output_type`: Directory name for the Excel workbook.
- `file_name`: Base name for output Excel file (defaults to structure file name).
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional arguments for Excel saving (engine, etc.).

**Returns:**

- Path to the created Excel workbook file.

**Example:**

```python
# First convert Excel to CSV
csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
    "workbook.xlsx", file_name="converted_workbook"
)

# ... make changes to CSV files ...

# Then convert back to Excel
excel_path = file_utils.convert_csv_to_excel_workbook(
    structure_json_path=structure_file,
    file_name="reconstructed_workbook"
)
```

**Reconstruction Metadata:**

The method creates a reconstruction metadata JSON file with information about:
- Source structure file and reconstruction timestamp
- Original workbook information
- Sheets successfully reconstructed vs. missing files
- Current dimensions and column information for each sheet

##### `_get_directory_config`

Get directory configuration with fallback to defaults.

```python
_get_directory_config() -> Dict[str, str]
```

**Returns:**

- Dictionary with directory configuration including:
  - `data_directory`: Main directory name (e.g., "data", "documents")
  - `raw`: Raw data subdirectory name
  - `processed`: Processed data subdirectory name
  - `templates`: Templates subdirectory name

**Example:**

```python
dir_config = file_utils._get_directory_config()
# Returns: {
#     "data_directory": "documents",
#     "raw": "product_docs",
#     "processed": "cs_documents",
#     "templates": "templates"
# }
```

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

##### `file_exists`

Check if a file exists in storage. This method never raises exceptions - it returns `False` on any error.

```python
file_exists(
    file_path: str,
    input_type: str = None,
    sub_path: str = None,
    root_level: bool = False
) -> bool
```

**Parameters:**

- `file_path`: Path to file (relative to input_type/sub_path or absolute).
- `input_type`: Type of input directory (e.g., "raw", "config", "processed", "templates").
- `sub_path`: Optional subdirectory path relative to input_type directory.
- `root_level`: If True, input_type is a directory at project root level. If False (default), input_type is under the data directory.

**Returns:**

- `bool`: True if file exists, False otherwise. Never raises exceptions.

**Examples:**

```python
# Check config file
exists = file_utils.file_exists("ACME.config-defaults.yml", input_type="config", sub_path="ACME")

# Check template file (root level)
exists = file_utils.file_exists("ADP-template_ADM.pptx", input_type="templates", sub_path="ADM", root_level=True)

# Check absolute path
exists = file_utils.file_exists("/absolute/path/to/file.yml")
```

##### `list_directory`

List files and directories in a storage path. This method never raises exceptions - it returns an empty list on any error.

```python
list_directory(
    directory_path: str = None,
    input_type: str = None,
    sub_path: str = None,
    pattern: str = None,
    root_level: bool = False,
    files_only: bool = False,
    directories_only: bool = False
) -> List[str]
```

**Parameters:**

- `directory_path`: Path to directory (relative to input_type/sub_path or absolute). If None and input_type provided, lists input_type directory.
- `input_type`: Type of input directory (e.g., "raw", "config", "processed", "templates").
- `sub_path`: Optional subdirectory path relative to input_type directory.
- `pattern`: Optional glob pattern to filter results (e.g., "*.yml", "*.pptx", "ACME.*").
- `root_level`: If True, input_type is a directory at project root level. If False (default), input_type is under the data directory.
- `files_only`: If True, return only files (exclude directories).
- `directories_only`: If True, return only directories (exclude files).

**Returns:**

- `List[str]`: List of file/directory names in the directory (not full paths). Returns empty list if directory doesn't exist or on error.

**Examples:**

```python
# List all config files for a customer
config_files = file_utils.list_directory(
    input_type="config", 
    sub_path="ACME", 
    pattern="*.yml"
)

# List templates in customer directory (root level)
templates = file_utils.list_directory(
    input_type="templates", 
    sub_path="ADM", 
    root_level=True, 
    pattern="*.pptx"
)

# List all files in a directory
files = file_utils.list_directory("/absolute/path/to/dir", files_only=True)

# List only directories
dirs = file_utils.list_directory(input_type="raw", directories_only=True)
```

##### `create_directory`

Create a directory in storage. Supports both new signature and legacy signature for backward compatibility.

```python
create_directory(
    directory_path: str = None,
    input_type: str = None,
    sub_path: str = None,
    exist_ok: bool = True,
    root_level: bool = False,
    parent_dir: str = None  # Legacy parameter
) -> str
```

**Parameters:**

- `directory_path`: Path to directory (relative to input_type/sub_path or absolute). For backward compatibility, can also be called as positional first argument.
- `input_type`: Type of directory (e.g., "processed", "logs", "charts").
- `sub_path`: Optional subdirectory path.
- `exist_ok`: If True, don't raise error if directory exists (default: True).
- `root_level`: If True, input_type is a directory at project root level. If False (default), input_type is under the data directory.
- `parent_dir`: Legacy parameter - parent directory (use input_type/sub_path instead).

**Returns:**

- `str`: Path to created directory.

**Raises:**

- `StorageError`: If directory creation fails (and exist_ok=False if exists).
- `ValueError`: If invalid parent directory (legacy mode).

**Examples:**

```python
# New signature: Create chart directory in run folder
dir_path = file_utils.create_directory(
    "charts", 
    input_type="processed", 
    sub_path="presentations/ACME/run123"
)

# Create directory at root level
dir_path = file_utils.create_directory(
    "output", 
    input_type="reports", 
    root_level=True
)

# Legacy usage (still supported)
dir_path = file_utils.create_directory("features", parent_dir="data")
```

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

Save document content using configured storage backend. Supports rich document formats including DOCX, Markdown, PDF, PPTX, JSON, and YAML.

```python
save_document_to_storage(
    content: Union[str, Dict[str, Any], bytes, Path],
    output_filetype: Union[OutputFileType, str],
    output_type: str = "processed",
    file_name: Optional[str] = None,
    sub_path: Optional[Union[str, Path]] = None,
    include_timestamp: Optional[bool] = None,
    **kwargs
) -> Tuple[str, Optional[str]]
```

**Parameters:**

- `content`: Document content.
  - DOCX: string or structured dict (title/sections)
  - MARKDOWN: string or dict with `frontmatter` and `body`
  - PDF: string or structured dict (title/sections)
  - PPTX: bytes of a `.pptx` or a local Path/str pointing to a `.pptx` file
- `output_filetype`: Type of output file (DOCX, MARKDOWN, PDF, PPTX, JSON, YAML).
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
) -> Union[str, Dict[str, Any], bytes]
```

**Parameters:**

- `file_path`: Path to file. If `sub_path` is provided, this should be the filename only.
- `input_type`: Directory name to load from (e.g., "raw", "processed").
- `sub_path`: Optional subdirectory path relative to `input_type` directory.
- `**kwargs`: Additional arguments passed to storage backend.

**Returns:**

- Document content (string, dict, or bytes depending on file type).
  - MARKDOWN: str or dict (if YAML frontmatter present)
  - DOCX: extracted text (str)
  - PDF: extracted text (str)
  - PPTX: bytes of the `.pptx` file

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
    PARQUET = "parquet"
    
    # Multi-purpose formats (both tabular and document)
    JSON = "json"      # Can be used for DataFrames or structured documents
    YAML = "yaml"      # Can be used for DataFrames or structured documents
    
    # Document formats
    DOCX = "docx"
    MARKDOWN = "md"
    PDF = "pdf"
    PPTX = "pptx"
```

**Format Usage Guidelines:**

- **Tabular Data**: Use `save_data_to_storage()` for CSV, XLSX, PARQUET
- **Document Data**: Use `save_document_to_storage()` for DOCX, MARKDOWN, PDF, PPTX
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