# src/FileUtils/storage/local.py

import io
from pathlib import Path
from typing import Dict, Optional, Union, Any, Tuple
from datetime import datetime
import json
import csv

import pandas as pd

from ..core.base import BaseStorage, StorageOperationError


class LocalStorage(BaseStorage):
    """Local filesystem storage implementation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> str:
        """Save DataFrame to local filesystem."""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if file_format == "csv":
                df.to_csv(
                    path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                )
            elif file_format == "parquet":
                df.to_parquet(path, index=False)
            elif file_format == "xlsx":
                df.to_excel(path, index=False, engine="openpyxl")
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            return str(path)
        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrame: {e}") from e

    def save_dataframes(
        self,
        dataframes: Dict[str, pd.DataFrame],
        file_path: Union[str, Path],
        file_format: str,
        **kwargs,
    ) -> Dict[str, str]:
        """Save multiple DataFrames."""
        path = Path(file_path)
        saved_files = {}

        try:
            if file_format == "xlsx":
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    for sheet_name, df in dataframes.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                saved_files[path.stem] = str(path)
            else:
                for name, df in dataframes.items():
                    file_path = path.parent / f"{path.stem}_{name}.{file_format}"
                    saved_path = self.save_dataframe(df, file_path, file_format)
                    saved_files[name] = saved_path

            return saved_files
        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrames: {e}") from e

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from local filesystem."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            suffix = path.suffix.lower()
            if suffix == ".csv":
                return pd.read_csv(
                    path,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                )
            elif suffix == ".parquet":
                return pd.read_parquet(path)
            elif suffix in (".xlsx", ".xls"):
                return pd.read_excel(path, engine="openpyxl")
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
        except Exception as e:
            raise StorageOperationError(f"Failed to load DataFrame: {e}") from e

    def load_dataframes(
        self, file_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple DataFrames."""
        try:
            path = Path(file_path)
            if path.suffix.lower() in (".xlsx", ".xls"):
                return pd.read_excel(path, sheet_name=None, engine="openpyxl")
            else:
                # For other formats, assume multiple files with pattern
                pattern = f"{path.stem}_*.{path.suffix}"
                dataframes = {}
                for file in path.parent.glob(pattern):
                    name = file.stem.replace(f"{path.stem}_", "")
                    dataframes[name] = self.load_dataframe(file)
                return dataframes
        except Exception as e:
            raise StorageOperationError(f"Failed to load DataFrames: {e}") from e

    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from storage."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            raise StorageOperationError(f"Failed to delete file: {e}") from e

    def load_from_metadata(
        self, metadata_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using local metadata file."""
        with open(metadata_path, "r", encoding=self.config["encoding"]) as f:
            metadata = json.load(f)

        data = {}
        for key, file_info in metadata["files"].items():
            file_path = Path(file_info["path"])
            if file_info["format"] == "csv":
                data[key] = self._load_csv_with_inference(file_path)
            else:
                data[key] = self.load_dataframe(file_path)

        return data

    CSV_DELIMITERS = [",", ";", "\t", "|"]

    def _load_csv_with_inference(self, file_path: Path) -> pd.DataFrame:
        """Load CSV with delimiter inference."""
        for delimiter in self.CSV_DELIMITERS:
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
                if len(df.columns) > 1:
                    return df
            except pd.errors.ParserError:
                continue

        # Try CSV Sniffer as fallback
        with open(file_path, "r", encoding=self.config["encoding"]) as f:
            sample = f.read(1024)
            dialect = csv.Sniffer().sniff(sample)
        return pd.read_csv(
            file_path,
            dialect=dialect,
            encoding=self.config["encoding"],
            quoting=self.config["quoting"],
        )

    def save_with_metadata(
        self, data: Dict[str, pd.DataFrame], base_path: Path, file_format: str, **kwargs
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata."""
        saved_files = self.save_dataframes(data, base_path, file_format)

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "files": {
                k: {"path": v, "format": file_format} for k, v in saved_files.items()
            },
            "config": self.config,
        }

        metadata_path = base_path.parent / f"{base_path.stem}_metadata.json"
        with open(metadata_path, "w", encoding=self.config["encoding"]) as f:
            json.dump(metadata, f, indent=2)

        return saved_files, str(metadata_path)
