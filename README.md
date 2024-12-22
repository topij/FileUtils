# FileUtils

A Python utility package for consistent file operations across local and Azure storage.

## Features

- Unified interface for both local and Azure Blob Storage operations
- Automatic directory structure management
- Support for multiple file formats:
  - CSV
  - Excel (.xlsx, .xls)
  - Parquet
  - JSON
  - YAML
- Configurable file operations with YAML configuration
- Type hints and comprehensive error handling
- Logging system with configurable levels
- Azure Blob Storage integration

## Background and Use Cases

While doing data analysis to support my main job in business and product development, I ended up copying and pasting a lot of code related to file and directory handling. I wanted to have a clean interface that I can re-use in all of my more complex data science projects. 

As an exmple, take a look my [semantic text analyzer](https://www.github.com/topij/text-analyzer). For that particular project, I also added support for Azure storage integration which allowed me to use the same code base regardless of the underlying storage (for ex., local Windows/bash or Azure blob).

## Installation

See [INSTALLATION.md](docs/INSTALLATION.md) for detailed installation instructions.

## Usage

See [USAGE.md](docs/USAGE.md) for usage examples and API documentation.

For Azure Blob Storage setup and configuration, see [AZURE_SETUP.md](docs/AZURE_SETUP.md).

## Quick Start

```python
from FileUtils import FileUtils, OutputFileType

# Initialize with local storage
file_utils = FileUtils()

# Load DataFrame from various formats
df_csv = file_utils.load_single_file("data.csv", input_type="raw")
df_excel = file_utils.load_single_file("data.xlsx", input_type="raw")
df_parquet = file_utils.load_single_file("data.parquet", input_type="raw")
df_json = file_utils.load_single_file("data.json", input_type="raw")
df_yaml = file_utils.load_single_file("data.yaml", input_type="raw")

# Save DataFrame
file_utils.save_data_to_storage(
    data={"Sheet1": df},
    file_name="output",
    output_type="processed",
    output_filetype=OutputFileType.XLSX
)
```

## Requirements

- Python 3.9+
- Dependencies listed in pyproject.toml/environment.yaml

## Notes from the Author
Please note that I am not a professional software developer, and, for example, the code has not been heavily optimized. My focus was on functionality rather than fine-tuning or optimization.
Active maintenance is not guaranteed, but I may occasionally revisit and update the code base when needed.
Let me know if you find this useful :-)


## License

MIT License