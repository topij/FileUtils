import csv

DEFAULT_CONFIG = {
    "csv_delimiter": ";",
    "encoding": "utf-8",
    "quoting": csv.QUOTE_MINIMAL,
    "include_timestamp": True,
    "logging_level": "INFO",
    "disable_logging": False,
    "directory_structure": {
        "data": ["raw", "interim", "processed", "configurations"],
        "reports": ["figures", "outputs"],
        "models": [],
        "src": [],
    },
}
