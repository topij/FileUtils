# src/FileUtils/storage/azure.py

from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
from typing import Any, Dict, Union, Any
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
