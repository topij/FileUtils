# src/FileUtils/storage/azure.py

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from typing import Any, Dict, Union, Any, Tuple
import io
import json
import csv
from datetime import datetime

from pathlib import Path
import pandas as pd

from ..core.base import BaseStorage, StorageConnectionError, StorageOperationError


class AzureStorage(BaseStorage):
    """Azure Blob Storage implementation."""

    def __init__(self, connection_string: str, config: Dict[str, Any]):
        self.config = config
        try:
            self.client = BlobServiceClient.from_connection_string(connection_string)
        except Exception as e:
            raise StorageConnectionError(
                f"Failed to connect to Azure Storage: {e}"
            ) from e

    def _get_container_client(self, file_path: Union[str, Path]) -> Any:
        """Get container client for path."""
        path = str(file_path)
        if path.startswith("azure://"):
            container_name = path.split("/")[2]
            return self.client.get_container_client(container_name)
        return self.client.get_container_client(
            self.config["azure"]["default_container"]
        )

    def save_dataframe(
        self, df: pd.DataFrame, file_path: Union[str, Path], file_format: str, **kwargs
    ) -> str:
        """Save DataFrame to Azure Storage."""
        try:
            buffer = io.BytesIO()
            if file_format == "csv":
                df.to_csv(buffer, index=False, encoding=self.config["encoding"])
            elif file_format == "parquet":
                df.to_parquet(buffer, index=False)
            elif file_format == "xlsx":
                df.to_excel(buffer, index=False, engine="openpyxl")
            else:
                raise ValueError(f"Unsupported format: {file_format}")

            buffer.seek(0)
            container_client = self._get_container_client(file_path)
            blob_name = str(Path(file_path).name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(buffer, overwrite=True)

            return f"azure://{container_client.container_name}/{blob_name}"
        except Exception as e:
            raise StorageOperationError(
                f"Failed to save DataFrame to Azure: {e}"
            ) from e

    def _load_csv_with_inference(self, blob_client) -> pd.DataFrame:
        """Load CSV from Azure with delimiter inference."""
        buffer = io.BytesIO()
        blob_client.download_blob().readinto(buffer)
        buffer.seek(0)

        content = buffer.read().decode(self.config["encoding"])
        buffer.seek(0)

        # Try CSV Sniffer first
        try:
            dialect = csv.Sniffer().sniff(content[:1024])
            return pd.read_csv(
                buffer,
                dialect=dialect,
                encoding=self.config["encoding"],
                quoting=self.config["quoting"],
            )
        except:
            buffer.seek(0)

        # Try known delimiters
        for delimiter in [",", ";", "\t", "|"]:
            try:
                buffer.seek(0)
                df = pd.read_csv(
                    buffer,
                    delimiter=delimiter,
                    encoding=self.config["encoding"],
                    quoting=self.config["quoting"],
                )
                if len(df.columns) > 1:
                    return df
            except:
                continue

        raise ValueError("Could not infer CSV delimiter")

    def save_with_metadata(
        self, data: Dict[str, pd.DataFrame], base_path: Path, file_format: str, **kwargs
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
