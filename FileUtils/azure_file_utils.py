"""Azure Storage extension for FileUtils."""

import io
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd
from azure.storage.blob import BlobServiceClient, ContainerClient

from .file_utils import FileUtils, OutputFileType

logger = logging.getLogger(__name__)


class AzureFileUtils(FileUtils):
    """FileUtils extension with Azure Blob Storage support."""

    def __init__(
        self,
        connection_string: Optional[str] = None,
        project_root: Optional[Union[str, Path]] = None,
        container_mapping: Optional[Dict[str, str]] = None,
    ):
        """Initialize with optional Azure support.

        Args:
            connection_string: Azure Storage connection string
            project_root: Local project root directory
            container_mapping: Maps output types to container names
        """
        super().__init__(project_root)
        self.blob_service_client = None
        self.container_mapping = container_mapping or {
            "raw": "raw-data",
            "processed": "processed-data",
            "interim": "interim-data",
            "parameters": "parameters",
            "configurations": "configurations",
        }

        if connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    connection_string
                )
                self._ensure_containers()
                logger.info("Azure Blob Storage connection established")
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Azure Storage: {e}. Using local storage only."
                )

    def _ensure_containers(self) -> None:
        """Ensure required containers exist."""
        if not self.blob_service_client:
            return

        for container_name in self.container_mapping.values():
            try:
                self.blob_service_client.create_container(container_name, exist_ok=True)
                logger.debug(f"Container {container_name} verified")
            except Exception as e:
                logger.error(f"Error creating container {container_name}: {e}")

    def _get_container_client(self, output_type: str) -> Optional[ContainerClient]:
        """Get container client for output type."""
        if not self.blob_service_client:
            return None

        container_name = self.container_mapping.get(output_type)
        if not container_name:
            logger.warning(f"No container mapping for {output_type}")
            return None

        return self.blob_service_client.get_container_client(container_name)

    def save_data_to_disk(
        self,
        data: Union[Dict[str, Union[pd.DataFrame, List, Dict]], pd.DataFrame],
        output_filetype: OutputFileType = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], Optional[str]]:
        """Save data with Azure support."""
        if self.blob_service_client:
            try:
                container_client = self._get_container_client(output_type)
                if not container_client:
                    return super().save_data_to_disk(
                        data,
                        output_filetype,
                        output_type,
                        file_name,
                        include_timestamp,
                        **kwargs,
                    )

                saved_files = {}
                timestamp = self._get_timestamp() if include_timestamp else ""

                if isinstance(data, pd.DataFrame):
                    blob_name = (
                        f"{file_name or 'data'}{timestamp}.{output_filetype.value}"
                    )
                    saved_files.update(
                        self._save_dataframe_to_blob(
                            data, blob_name, container_client, output_filetype
                        )
                    )
                elif isinstance(data, dict):
                    saved_files.update(
                        self._save_dict_to_blob(
                            data,
                            container_client,
                            output_filetype,
                            timestamp,
                            file_name,
                        )
                    )

                return saved_files, None

            except Exception as e:
                logger.error(f"Azure save failed: {e}. Falling back to local storage.")

        return super().save_data_to_disk(
            data, output_filetype, output_type, file_name, include_timestamp, **kwargs
        )

    def _save_dataframe_to_blob(
        self,
        df: pd.DataFrame,
        blob_name: str,
        container_client: ContainerClient,
        output_filetype: OutputFileType,
    ) -> Dict[str, str]:
        """Save DataFrame to blob storage."""
        buffer = io.BytesIO()

        if output_filetype == OutputFileType.CSV:
            df.to_csv(buffer, index=False, encoding=self.config["encoding"])
        elif output_filetype == OutputFileType.PARQUET:
            df.to_parquet(buffer, index=False)
        elif output_filetype == OutputFileType.XLSX:
            df.to_excel(buffer, index=False, engine="openpyxl")

        buffer.seek(0)
        container_client.upload_blob(blob_name, buffer, overwrite=True)

        return {blob_name: f"azure://{container_client.container_name}/{blob_name}"}

    def _save_dict_to_blob(
        self,
        data: Dict,
        container_client: ContainerClient,
        output_filetype: OutputFileType,
        timestamp: str,
        file_name: Optional[str] = None,
    ) -> Dict[str, str]:
        """Save dictionary data to blob storage."""
        saved_files = {}

        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                blob_name = f"{key}{timestamp}.{output_filetype.value}"
                saved_files.update(
                    self._save_dataframe_to_blob(
                        value, blob_name, container_client, output_filetype
                    )
                )

        return saved_files

    def load_single_file(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> pd.DataFrame:
        """Load file with Azure support."""
        if self.blob_service_client and str(file_path).startswith("azure://"):
            try:
                container_name = str(file_path).split("/")[2]
                blob_name = "/".join(str(file_path).split("/")[3:])

                container_client = self.blob_service_client.get_container_client(
                    container_name
                )
                blob_client = container_client.get_blob_client(blob_name)

                stream = blob_client.download_blob()
                data = stream.readall()

                suffix = Path(blob_name).suffix.lower()
                if suffix == ".csv":
                    return pd.read_csv(
                        io.BytesIO(data), encoding=self.config["encoding"]
                    )
                elif suffix == ".parquet":
                    return pd.read_parquet(io.BytesIO(data))
                elif suffix in [".xlsx", ".xls"]:
                    return pd.read_excel(io.BytesIO(data))

                raise ValueError(f"Unsupported file type: {suffix}")

            except Exception as e:
                logger.error(f"Azure load failed: {e}. Falling back to local load.")

        return super().load_single_file(file_path, input_type)

    def load_excel_sheets(
        self, file_path: Union[str, Path], input_type: str = "raw"
    ) -> Dict[str, pd.DataFrame]:
        """Load Excel sheets with Azure support."""
        if self.blob_service_client and str(file_path).startswith("azure://"):
            try:
                container_name = str(file_path).split("/")[2]
                blob_name = "/".join(str(file_path).split("/")[3:])

                container_client = self.blob_service_client.get_container_client(
                    container_name
                )
                blob_client = container_client.get_blob_client(blob_name)

                stream = blob_client.download_blob()
                data = stream.readall()

                return pd.read_excel(io.BytesIO(data), sheet_name=None)

            except Exception as e:
                logger.error(
                    f"Azure Excel load failed: {e}. Falling back to local load."
                )

        return super().load_excel_sheets(file_path, input_type)
