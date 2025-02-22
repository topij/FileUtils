"""Azure Blob Storage implementation."""

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from typing import Dict, Union, Any, Optional, Tuple
import io
import json
import yaml
import tempfile
from datetime import datetime
from pathlib import Path
import pandas as pd
import csv

from ..core.base import BaseStorage, StorageConnectionError, StorageOperationError


class AzureStorage(BaseStorage):
    """Azure Blob Storage implementation."""

    def __init__(self, connection_string: str, config: Dict[str, Any]):
        """Initialize Azure storage.

        Args:
            connection_string: Azure storage connection string
            config: Configuration dictionary
        """
        super().__init__(config)
        try:
            self.client = BlobServiceClient.from_connection_string(connection_string)
            self._ensure_containers()
        except Exception as e:
            raise StorageConnectionError(
                f"Failed to connect to Azure Storage: {e}"
            ) from e

    def _ensure_containers(self):
        """Ensure required containers exist."""
        containers = self.config.get("azure", {}).get("container_mapping", {})
        for container_name in containers.values():
            try:
                self.client.create_container(container_name)
                self.logger.debug(f"Created container: {container_name}")
            except ResourceExistsError:
                pass
            except Exception as e:
                self.logger.warning(f"Failed to create container {container_name}: {e}")

    def _get_container_client(self, file_path: Union[str, Path]) -> Any:
        """Get container client for path."""
        path = str(file_path)
        if path.startswith("azure://"):
            container_name = path.split("/")[2]
            return self.client.get_container_client(container_name)
        return self.client.get_container_client(
            self.config["azure"]["container_mapping"].get("default", "data")
        )

    def _parse_azure_url(self, file_path: str) -> Tuple[str, str]:
        """Parse azure:// URL into container and blob names."""
        if not file_path.startswith("azure://"):
            raise ValueError("Invalid Azure path format")
        
        parts = file_path.split("/")
        container_name = parts[2]
        blob_name = "/".join(parts[3:])
        return container_name, blob_name

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from Azure Blob Storage."""
        try:
            container_name, blob_name = self._parse_azure_url(str(file_path))
            blob_client = self.client.get_blob_client(
                container=container_name, blob=blob_name
            )

            suffix = Path(blob_name).suffix.lower()
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                blob_data = blob_client.download_blob()
                blob_data.readinto(temp_file)
                temp_path = Path(temp_file.name)

            try:
                if suffix == ".csv":
                    return self._load_csv_with_inference(temp_path)
                elif suffix == ".parquet":
                    return pd.read_parquet(temp_path)
                elif suffix in (".xlsx", ".xls"):
                    return pd.read_excel(temp_path, engine="openpyxl")
                elif suffix == ".json":
                    return self._load_json_as_dataframe(temp_path)
                elif suffix == ".yaml":
                    return self._load_yaml_as_dataframe(temp_path)
                else:
                    raise ValueError(f"Unsupported file format: {suffix}")
            finally:
                temp_path.unlink(missing_ok=True)

        except Exception as e:
            raise StorageOperationError(
                f"Failed to load DataFrame from Azure: {e}"
            ) from e

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

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs
    ) -> str:
        """Save DataFrame to Azure Blob Storage.
        
        Args:
            df: DataFrame to save
            file_path: Path to save to (azure:// URL)
            **kwargs: Additional arguments for saving:
                - sheet_name: Sheet name for Excel files
                - orient: Orientation for JSON files ("records", "index", etc.)
                - yaml_options: Dict of options for yaml.safe_dump
                - compression: Compression options for parquet files
            
        Returns:
            Azure URL where the file was saved
        """
        try:
            container_name, blob_name = self._parse_azure_url(str(file_path))
            blob_client = self.client.get_blob_client(
                container=container_name, blob=blob_name
            )

            suffix = Path(blob_name).suffix.lower()
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_path = Path(temp_file.name)

                try:
                    if suffix == ".csv":
                        df.to_csv(temp_path, index=False)
                    elif suffix == ".parquet":
                        compression = kwargs.get("compression", "snappy")
                        df.to_parquet(temp_path, index=False, compression=compression)
                    elif suffix in (".xlsx", ".xls"):
                        sheet_name = kwargs.get("sheet_name", "Sheet1")
                        df.to_excel(temp_path, sheet_name=sheet_name, index=False, engine="openpyxl")
                    elif suffix == ".json":
                        orient = kwargs.get("orient", "records")
                        df.to_json(temp_path, orient=orient, indent=2)
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
                        
                        with open(temp_path, "w", encoding=self.config["encoding"]) as f:
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

                    with open(temp_path, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)

                finally:
                    temp_path.unlink(missing_ok=True)

            return f"azure://{container_name}/{blob_name}"

        except yaml.YAMLError as e:
            raise StorageOperationError(f"Failed to save YAML file - YAML error: {e}") from e
        except Exception as e:
            raise StorageOperationError(
                f"Failed to save DataFrame to Azure: {e}"
            ) from e

    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists in Azure Storage."""
        try:
            if not str(file_path).startswith("azure://"):
                return False

            container_name, blob_name = self._parse_azure_url(str(file_path))
            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception:
            return False

    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from Azure Storage."""
        try:
            container_name, blob_name = self._parse_azure_url(str(file_path))
            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            if blob_client.exists():
                blob_client.delete_blob()
                return True
            return False
        except Exception as e:
            raise StorageOperationError(
                f"Failed to delete file from Azure Storage: {e}"
            ) from e

    def save_with_metadata(
        self,
        data: Dict[str, pd.DataFrame],
        base_path: Path,
        file_format: str,
        **kwargs,
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata to Azure."""
        saved_files = self.save_dataframes(data, base_path, file_format)

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "files": {
                k: {"path": v, "format": file_format} for k, v in saved_files.items()
            },
            "config": self.config,
            "storage": "azure",
        }

        container_client = self._get_container_client(base_path)
        metadata_blob = container_client.get_blob_client(
            f"{base_path.stem}_metadata.json"
        )

        metadata_json = json.dumps(metadata, indent=2)
        metadata_blob.upload_blob(metadata_json.encode("utf-8"), overwrite=True)

        return (
            saved_files,
            f"azure://{container_client.container_name}/{metadata_blob.blob_name}",
        )

    def load_from_metadata(
        self, metadata_path: Union[str, Path], **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using Azure metadata file."""
        container_client = self._get_container_client(metadata_path)
        blob_client = container_client.get_blob_client(Path(metadata_path).name)

        metadata_content = blob_client.download_blob().readall().decode("utf-8")
        metadata = json.loads(metadata_content)

        data = {}
        for key, file_info in metadata["files"].items():
            blob_path = file_info["path"].replace("azure://", "", 1)
            container_name = blob_path.split("/")[0]
            blob_name = "/".join(blob_path.split("/")[1:])

            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            if file_info["format"] == "csv":
                data[key] = self._load_csv_with_inference(blob_client)
            else:
                data[key] = self.load_dataframe(blob_path)

        return data

    def load_yaml(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load YAML file from Azure Storage."""
        try:
            if not str(file_path).startswith("azure://"):
                raise ValueError("Invalid Azure path format")

            parts = str(file_path).split("/")
            container_name = parts[2]
            blob_name = "/".join(parts[3:])

            if not blob_name.lower().endswith((".yaml", ".yml")):
                raise ValueError("File must have .yaml or .yml extension")

            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            content = (
                blob_client.download_blob().readall().decode(self.config["encoding"])
            )
            return yaml.safe_load(content)
        except Exception as e:
            raise StorageOperationError(f"Failed to load YAML from Azure: {e}") from e

    def load_json(self, file_path: Union[str, Path], **kwargs) -> Any:
        """Load JSON file from Azure Storage."""
        try:
            if not str(file_path).startswith("azure://"):
                raise ValueError("Invalid Azure path format")

            parts = str(file_path).split("/")
            container_name = parts[2]
            blob_name = "/".join(parts[3:])

            if not blob_name.lower().endswith(".json"):
                raise ValueError("File must have .json extension")

            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            content = (
                blob_client.download_blob().readall().decode(self.config["encoding"])
            )
            return json.loads(content, **kwargs)
        except Exception as e:
            raise StorageOperationError(f"Failed to load JSON from Azure: {e}") from e

    def save_dataframes(
        self, data: Dict[str, pd.DataFrame], file_path: Union[str, Path], **kwargs
    ) -> Dict[str, str]:
        """Save multiple DataFrames to Azure Blob Storage.
        
        Args:
            data: Dictionary of DataFrames to save
            file_path: Path to save to (azure:// URL)
            **kwargs: Additional arguments for saving (e.g., engine for Excel)
            
        Returns:
            Dictionary mapping sheet names to Azure URLs. For Excel files,
            all sheets will map to the same URL.
        """
        try:
            container_name, blob_name = self._parse_azure_url(str(file_path))
            suffix = Path(blob_name).suffix.lower()

            if suffix in (".xlsx", ".xls"):
                # Save all DataFrames to a single Excel file
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                    temp_path = Path(temp_file.name)
                    try:
                        with pd.ExcelWriter(temp_path, engine=kwargs.get("engine", "openpyxl")) as writer:
                            for sheet_name, df in data.items():
                                df.to_excel(writer, sheet_name=sheet_name, index=False)

                        # Upload the Excel file
                        blob_client = self.client.get_blob_client(
                            container=container_name, blob=blob_name
                        )
                        with open(temp_path, "rb") as data_file:
                            blob_client.upload_blob(data_file, overwrite=True)

                        # For Excel files, return a single URL
                        azure_url = f"azure://{container_name}/{blob_name}"
                        return {"Sheet1": azure_url}
                    finally:
                        temp_path.unlink(missing_ok=True)
            else:
                # Save each DataFrame to a separate file
                saved_files = {}
                for sheet_name, df in data.items():
                    # Create unique blob name for each sheet
                    sheet_blob_name = f"{Path(blob_name).stem}_{sheet_name}{Path(blob_name).suffix}"
                    sheet_path = f"azure://{container_name}/{sheet_blob_name}"
                    saved_path = self.save_dataframe(df, sheet_path, **kwargs)
                    saved_files[sheet_name] = saved_path
                return saved_files

        except Exception as e:
            raise StorageOperationError(
                f"Failed to save DataFrames to Azure: {e}"
            ) from e
