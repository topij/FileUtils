"""Local filesystem storage implementation."""

import csv
from pathlib import Path
import yaml
import json
from typing import Dict, Optional, Union, Any

import pandas as pd

from ..core.base import BaseStorage, StorageOperationError
from ..utils.common import ensure_path


class LocalStorage(BaseStorage):
    """Local filesystem storage implementation."""

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> str:
        """Save DataFrame to local filesystem."""
        try:
            path = ensure_path(file_path)

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
                # Handle Excel with sheet name
                sheet_name = kwargs.get(
                    "sheet_name", next(iter(kwargs)) if kwargs else "Sheet1"
                )
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            return str(path)
        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrame: {e}") from e

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

    def _load_csv_with_inference(self, file_path: Path) -> pd.DataFrame:
        """Load CSV with delimiter inference."""
        # Try CSV Sniffer first
        try:
            with open(file_path, "r", encoding=self.config["encoding"]) as f:
                sample = f.read(1024)
                dialect = csv.Sniffer().sniff(sample)
                return pd.read_csv(
                    file_path,
                    dialect=dialect,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
        except:
            pass

        # Try known delimiters
        delimiters = [",", ";", "\t", "|"]
        for delimiter in delimiters:
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=delimiter,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
                if len(df.columns) > 1:
                    return df
            except:
                continue

        raise ValueError("Could not infer CSV delimiter")

    def load_yaml(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load YAML file from local filesystem."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            if path.suffix.lower() not in (".yaml", ".yml"):
                raise ValueError("File must have .yaml or .yml extension")

            with open(path, "r", encoding=self.config["encoding"]) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise StorageOperationError(f"Failed to load YAML file: {e}") from e

    def load_json(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load JSON file from local filesystem."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            if path.suffix.lower() != ".json":
                raise ValueError("File must have .json extension")

            with open(path, "r", encoding=self.config["encoding"]) as f:
                return json.load(f, **kwargs)
        except Exception as e:
            raise StorageOperationError(f"Failed to load JSON file: {e}") from e

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from local filesystem."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")

            suffix = path.suffix.lower()
            if suffix == ".csv":
                return self._load_csv_with_inference(path)
            elif suffix == ".parquet":
                return pd.read_parquet(path)
            elif suffix in (".xlsx", ".xls"):
                return pd.read_excel(path, engine="openpyxl")
            elif suffix == ".json":
                return self._load_json_as_dataframe(path)
            elif suffix == ".yaml":
                return self._load_yaml_as_dataframe(path)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
        except Exception as e:
            raise StorageOperationError(f"Failed to load DataFrame: {e}") from e

    def _load_yaml_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load YAML file as DataFrame."""
        with open(path) as f:
            data = yaml.safe_load(f)
            # Handle both list of records and dictionary formats
            if isinstance(data, list):
                df = pd.DataFrame(data)
                # Sort columns alphabetically for consistent order
                return df.reindex(sorted(df.columns), axis=1)
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data, orient="index")
                return df.reindex(sorted(df.columns), axis=1)
            else:
                raise ValueError("YAML must contain list of records or dictionary")

    def _load_json_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load JSON file as DataFrame."""
        with open(path) as f:
            data = json.load(f)
            # Handle both list of records and dictionary formats
            if isinstance(data, list):
                df = pd.DataFrame(data)
                # Sort columns alphabetically for consistent order
                return df.reindex(sorted(df.columns), axis=1)
            elif isinstance(data, dict):
                df = pd.DataFrame.from_dict(data, orient="index")
                return df.reindex(sorted(df.columns), axis=1)
            else:
                raise ValueError("JSON must contain list of records or dictionary")
