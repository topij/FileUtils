"""Azure Blob Storage implementation."""

from azure.storage.blob import BlobServiceClient
import yaml
from azure.core.exceptions import ResourceExistsError
from typing import Dict, Union, Any, Tuple
import io
import json
from datetime import datetime
from pathlib import Path
import pandas as pd

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

    import json


import yaml
import tempfile
from pathlib import Path
from typing import Union, Optional

import pandas as pd
from azure.storage.blob import BlobServiceClient
from FileUtils.core.base import StorageOperationError


class AzureStorage:
    """Azure Blob Storage implementation."""

    def load_dataframe(self, file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load DataFrame from Azure Blob Storage."""
        try:
            # Handle azure:// URLs
            container_name, blob_name = self._parse_azure_url(str(file_path))

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )

            # Get file suffix from blob name
            suffix = Path(blob_name).suffix.lower()

            # Create temp file for download
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                # Download blob to temp file
                blob_data = blob_client.download_blob()
                blob_data.readinto(temp_file)
                temp_path = Path(temp_file.name)

            try:
                # Load based on file format
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
                # Clean up temp file
                temp_path.unlink(missing_ok=True)

        except Exception as e:
            raise StorageOperationError(
                f"Failed to load DataFrame from Azure: {e}"
            ) from e

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

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], **kwargs
    ) -> None:
        """Save DataFrame to Azure Blob Storage."""
        try:
            # Handle azure:// URLs
            container_name, blob_name = self._parse_azure_url(str(file_path))

            # Get blob client
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )

            # Get file suffix
            suffix = Path(blob_name).suffix.lower()

            # Create temp file for upload
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_path = Path(temp_file.name)

                try:
                    # Save based on file format
                    if suffix == ".csv":
                        df.to_csv(temp_path, index=False)
                    elif suffix == ".parquet":
                        df.to_parquet(temp_path)
                    elif suffix in (".xlsx", ".xls"):
                        df.to_excel(temp_path, index=False, engine="openpyxl")
                    elif suffix == ".json":
                        df.to_json(temp_path, orient="records")
                    elif suffix == ".yaml":
                        with open(temp_path, "w") as f:
                            yaml.safe_dump(df.to_dict(orient="records"), f)
                    else:
                        raise ValueError(f"Unsupported file format: {suffix}")

                    # Upload file
                    with open(temp_path, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)

                finally:
                    # Clean up temp file
                    temp_path.unlink(missing_ok=True)

        except Exception as e:
            raise StorageOperationError(
                f"Failed to save DataFrame to Azure: {e}"
            ) from e

    def _load_csv_from_buffer(self, buffer: io.BytesIO) -> pd.DataFrame:
        """Load CSV from buffer with inference."""
        content = buffer.read().decode(self.config["encoding"])
        buffer.seek(0)

        try:
            import csv

            dialect = csv.Sniffer().sniff(content[:1024])
            return pd.read_csv(
                buffer,
                dialect=dialect,
                encoding=self.config["encoding"],
                quoting=self.config["quoting"],
            )
        except:
            # Fallback to configured delimiter
            buffer.seek(0)
            return pd.read_csv(
                buffer,
                sep=self.config["csv_delimiter"],
                encoding=self.config["encoding"],
                quoting=self.config["quoting"],
            )

    def exists(self, file_path: Union[str, Path]) -> bool:
        """Check if file exists in Azure Storage."""
        try:
            if not str(file_path).startswith("azure://"):
                return False

            parts = str(file_path).split("/")
            container_name = parts[2]
            blob_name = "/".join(parts[3:])

            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            return blob_client.exists()
        except Exception:
            return False

    def delete(self, file_path: Union[str, Path]) -> bool:
        """Delete file from Azure Storage."""
        try:
            if not str(file_path).startswith("azure://"):
                raise ValueError("Invalid Azure path format")

            parts = str(file_path).split("/")
            container_name = parts[2]
            blob_name = "/".join(parts[3:])

            container_client = self.client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)

            if blob_client.exists():
                blob_client.delete_blob()
                return True
            return False
        except Exception as e:
            raise StorageOperationError(f"Failed to delete file from Azure: {e}") from e

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

    def _load_csv_with_inference(self, blob_client) -> pd.DataFrame:
        """Load CSV from Azure with delimiter inference."""
        buffer = io.BytesIO()
        blob_client.download_blob().readinto(buffer)
        buffer.seek(0)
        return self._load_csv_from_buffer(buffer)

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
