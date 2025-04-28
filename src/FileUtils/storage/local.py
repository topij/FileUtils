"""Local filesystem storage implementation."""

import csv
from pathlib import Path
import yaml
import json
import tempfile
from typing import Dict, Optional, Union, Any

import pandas as pd

from ..core.base import BaseStorage, StorageOperationError
from ..utils.common import ensure_path


class LocalStorage(BaseStorage):
    """Local filesystem storage implementation."""

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs
    ) -> str:
        """Save DataFrame to local filesystem.
        
        Args:
            df: DataFrame to save
            file_path: Path to save to
            **kwargs: Additional arguments for saving:
                - sheet_name: Sheet name for Excel files
                - orient: Orientation for JSON files ("records", "index", etc.)
                - yaml_options: Dict of options for yaml.safe_dump
                - compression: Compression options for parquet files
            
        Returns:
            String path where the file was saved
        """
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            if suffix == ".csv":
                df.to_csv(
                    path,
                    index=False,
                    encoding=self.config["encoding"],
                    sep=self.config["csv_delimiter"],
                )
            elif suffix == ".parquet":
                compression = kwargs.get("compression", "snappy")
                df.to_parquet(path, index=False, compression=compression)
            elif suffix in (".xlsx", ".xls"):
                sheet_name = kwargs.get("sheet_name", "Sheet1")
                with pd.ExcelWriter(path, engine="openpyxl") as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            elif suffix == ".json":
                orient = kwargs.get("orient", "records")
                df.to_json(path, orient=orient, indent=2)
            elif suffix == ".yaml" or suffix == ".yml":
                yaml_options = kwargs.get("yaml_options", {})
                default_flow_style = yaml_options.pop("default_flow_style", False)
                sort_keys = yaml_options.pop("sort_keys", False)
                
                # Convert DataFrame to dict based on orient
                orient = kwargs.get("orient", "records")
                if orient == "records":
                    data = df.to_dict(orient="records")
                elif orient == "index":
                    data = df.to_dict(orient="index")
                else:
                    raise ValueError(f"Unsupported YAML orientation: {orient}")
                
                with open(path, "w", encoding=self.config["encoding"]) as f:
                    yaml.safe_dump(
                        data,
                        f,
                        default_flow_style=default_flow_style,
                        sort_keys=sort_keys,
                        encoding=self.config["encoding"],
                        **yaml_options
                    )
            else:
                raise ValueError(f"Unsupported file format: {suffix}")

            return str(path)
        except yaml.YAMLError as e:
            raise StorageOperationError(f"Failed to save YAML file - YAML error: {e}") from e
        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrame: {e}") from e

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from local filesystem."""
        try:
            path = ensure_path(file_path)
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

    def _load_csv_with_inference(self, path: Path) -> pd.DataFrame:
        """Load CSV with delimiter inference."""
        with open(path, "r", encoding=self.config["encoding"]) as f:
            content = f.read(1024)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(content)
                return pd.read_csv(
                    f,
                    dialect=dialect,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
            except:
                f.seek(0)
                return pd.read_csv(
                    f,
                    sep=self.config["csv_delimiter"],
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )

    def _load_json_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load JSON file as DataFrame.
        
        Supports both list of records and dictionary formats.
        """
        try:
            with open(path, "r", encoding=self.config["encoding"]) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    raise StorageOperationError(f"Invalid JSON format: {e}")

                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    return df.reindex(sorted(df.columns), axis=1)
                elif isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data, orient="index")
                    return df.reindex(sorted(df.columns), axis=1)
                else:
                    raise ValueError("JSON must contain list of records or dictionary")
        except Exception as e:
            if isinstance(e, StorageOperationError):
                raise
            raise StorageOperationError(f"Failed to load JSON file: {e}") from e

    def _load_yaml_as_dataframe(self, path: Path) -> pd.DataFrame:
        """Load YAML file as DataFrame.
        
        Supports both list of records and dictionary formats.
        Handles YAML-specific errors separately for better error messages.
        """
        try:
            with open(path, "r", encoding=self.config["encoding"]) as f:
                try:
                    data = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    raise StorageOperationError(f"Invalid YAML format: {e}")

                if isinstance(data, list):
                    df = pd.DataFrame(data)
                    return df.reindex(sorted(df.columns), axis=1)
                elif isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data, orient="index")
                    return df.reindex(sorted(df.columns), axis=1)
                else:
                    raise ValueError("YAML must contain list of records or dictionary")
        except Exception as e:
            if isinstance(e, StorageOperationError):
                raise
            raise StorageOperationError(f"Failed to load YAML file: {e}") from e

    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from local filesystem."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            raise StorageOperationError(
                f"Failed to delete file from local filesystem: {e}"
            ) from e

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

    def save_dataframes(
        self, data: Dict[str, pd.DataFrame], file_path: Union[str, Path], **kwargs
    ) -> Dict[str, str]:
        """Save multiple DataFrames to local filesystem.
        
        Args:
            data: Dictionary of DataFrames to save
            file_path: Path to save to
            **kwargs: Additional arguments for saving (e.g., engine for Excel)
            
        Returns:
            Dictionary mapping sheet names to saved file paths. For Excel files,
            all sheets will map to the same file path.
        """
        try:
            path = ensure_path(file_path)
            suffix = path.suffix.lower()

            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            if suffix in (".xlsx", ".xls"):
                # Save all DataFrames to a single Excel file
                with pd.ExcelWriter(path, engine=kwargs.get("engine", "openpyxl")) as writer:
                    for sheet_name, df in data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                # For Excel files, return a single file path
                return {"Sheet1": str(path)}
            else:
                # Save each DataFrame to a separate file
                saved_files = {}
                for sheet_name, df in data.items():
                    # Create unique file name for each sheet
                    sheet_path = path.parent / f"{path.stem}_{sheet_name}{path.suffix}"
                    saved_path = self.save_dataframe(df, sheet_path, **kwargs)
                    saved_files[sheet_name] = saved_path
                return saved_files

        except Exception as e:
            raise StorageOperationError(f"Failed to save DataFrames: {e}") from e
