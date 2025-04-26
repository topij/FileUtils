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
    include_timestamp: Optional[bool] = None,
    **kwargs
) -> Tuple[Dict[str, str], Optional[str]]
```

**Parameters:**

- `data`: DataFrame or dictionary of DataFrames (for multi-sheet Excel).
- `output_filetype`: File format to save data in (e.g., CSV, XLSX, JSON).
- `output_type`: Directory name to save in (e.g., "raw", "processed") - not the file format.
- `file_name`: Base name for the file without extension.
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
    **kwargs
) -> pd.DataFrame
```

**Parameters:**

- `file_path`: Path to file, relative to data directory. File format is auto-detected from extension.
- `input_type`: Directory name to load from (e.g., "raw", "processed") - not the file format.
- `**kwargs`: Format-specific options for reading.

**Returns:**

- DataFrame containing file data.

##### `load_excel_sheets`

Load all sheets from an Excel file.

```python
load_excel_sheets(
    file_path: Union[str, Path],
    input_type: str = "raw",
    **kwargs
) -> Dict[str, pd.DataFrame]
```

**Parameters:**

- `file_path`: Path to Excel file. Format is auto-detected from extension (.xlsx, .xls).
- `input_type`: Directory name to load from - not the file format.
- `**kwargs`: Additional options for pd.read_excel.

**Returns:**

- Dictionary mapping sheet names to DataFrames.

##### `load_multiple_files`

Load multiple files into a dictionary of DataFrames. File formats are automatically detected from extensions.

```python
load_multiple_files(
    file_paths: List[Union[str, Path]],
    input_type: str = "raw",
    file_type: Optional[OutputFileType] = None
) -> Dict[str, pd.DataFrame]
```

**Parameters:**

- `file_paths`: List of file paths. Formats are auto-detected from extensions.
- `input_type`: Directory name to load from - not the file format.
- `file_type`: Optional file type override if auto-detection should be bypassed.

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
    **kwargs
) -> Any
```

**Parameters:**

- `file_path`: Path to YAML file. Format is auto-detected from extension.
- `input_type`: Directory name to load from - not the file format.
- `**kwargs`: Additional options.

**Returns:**

- Parsed YAML content.

##### `load_json`

Load JSON file content.

```python
load_json(
    file_path: Union[str, Path],
    input_type: str = "raw",
    **kwargs
) -> Any
```

**Parameters:**

- `file_path`: Path to JSON file. Format is auto-detected from extension.
- `input_type`: Directory name to load from - not the file format.
- `**kwargs`: Additional options.

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

## Enums

### `OutputFileType`

Enumeration of supported file types.

```python
class OutputFileType(Enum):
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    JSON = "json"
    PARQUET = "parquet"
    YAML = "yaml"
```

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