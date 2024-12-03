"""Azure setup utilities for FileUtils.

This module provides helper functions for setting up Azure Storage
containers and validating Azure configurations with python-dotenv support.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Union

import yaml
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv, find_dotenv, set_key

logger = logging.getLogger(__name__)


class AzureSetupUtils:
    """Utility class for Azure Storage setup and validation."""

    @staticmethod
    def load_env_file(env_path: Optional[Union[str, Path]] = None) -> str:
        """Load environment variables from .env file.

        Args:
            env_path: Optional path to .env file. If not provided,
                     will search for .env in parent directories

        Returns:
            str: Path to the loaded .env file

        Raises:
            FileNotFoundError: If no .env file is found
        """
        if env_path:
            env_path = Path(env_path)
            if not env_path.exists():
                raise FileNotFoundError(f"No .env file found at: {env_path}")
            load_dotenv(env_path)
            return str(env_path)

        # Search for .env file
        env_path = find_dotenv()
        if not env_path:
            raise FileNotFoundError(
                "No .env file found. Create one or provide path explicitly."
            )

        load_dotenv(env_path)
        return env_path

    @staticmethod
    def create_env_file(
        connection_string: str,
        env_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
    ) -> str:
        """Create or update .env file with Azure connection string.

        Args:
            connection_string: Azure Storage connection string
            env_path: Optional path for .env file. Defaults to project root
            overwrite: Whether to overwrite existing .env file

        Returns:
            str: Path to the created/updated .env file

        Raises:
            FileExistsError: If file exists and overwrite=False
        """
        if env_path:
            env_path = Path(env_path)
        else:
            env_path = Path.cwd() / ".env"

        if env_path.exists() and not overwrite:
            raise FileExistsError(
                f".env file already exists at {env_path}. Set overwrite=True to update."
            )

        # Create or update .env file
        env_path.parent.mkdir(parents=True, exist_ok=True)

        if not env_path.exists():
            env_path.touch()

        set_key(str(env_path), "AZURE_STORAGE_CONNECTION_STRING", connection_string)

        logger.info(f"Created/updated .env file at: {env_path}")
        return str(env_path)

    @staticmethod
    def validate_connection_string(
        connection_string: Optional[str] = None,
        env_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """Validate and retrieve Azure connection string.

        Args:
            connection_string: Optional explicit connection string
            env_path: Optional path to .env file

        Returns:
            str: Valid connection string

        Raises:
            ValueError: If no valid connection string is found
        """
        if connection_string:
            return connection_string

        # Try to load from .env file
        try:
            AzureSetupUtils.load_env_file(env_path)
        except FileNotFoundError:
            logger.debug("No .env file found")

        conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not conn_str:
            raise ValueError(
                "Azure connection string not found. Either:\n"
                "1. Set AZURE_STORAGE_CONNECTION_STRING environment variable\n"
                "2. Create .env file with AZURE_STORAGE_CONNECTION_STRING\n"
                "3. Provide connection_string parameter"
            )
        return conn_str

    @staticmethod
    def load_container_config(config_path: Optional[Path] = None) -> Dict[str, str]:
        """Load container configuration from config file.

        Args:
            config_path: Optional path to config file

        Returns:
            Dict[str, str]: Container mapping configuration
        """
        default_mapping = {
            "raw": "raw-data",
            "processed": "processed-data",
            "interim": "interim-data",
            "parameters": "parameters",
            "configurations": "configurations",
        }

        if not config_path:
            return default_mapping

        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            return config.get("azure", {}).get("container_mapping", default_mapping)
        except Exception as e:
            logger.warning(f"Error loading config file: {e}. Using default mapping.")
            return default_mapping

    @classmethod
    def setup_azure_storage(
        cls,
        connection_string: Optional[str] = None,
        config_path: Optional[Path] = None,
        container_names: Optional[List[str]] = None,
        env_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """Set up Azure Storage containers.

        Args:
            connection_string: Optional Azure Storage connection string
            config_path: Optional path to config file
            container_names: Optional list of container names to create
            env_path: Optional path to .env file

        Raises:
            ValueError: If connection string is invalid
        """
        # Validate connection string
        conn_str = cls.validate_connection_string(connection_string, env_path)

        # Get container names
        if container_names is None:
            container_mapping = cls.load_container_config(config_path)
            container_names = list(container_mapping.values())

        # Create service client
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)

        # Create containers
        for container in container_names:
            try:
                blob_service_client.create_container(container)
                logger.info(f"Created container: {container}")
            except ResourceExistsError:
                logger.info(f"Container already exists: {container}")
            except Exception as e:
                logger.error(f"Error creating container {container}: {e}")

    @classmethod
    def validate_azure_setup(
        cls,
        connection_string: Optional[str] = None,
        container_names: Optional[List[str]] = None,
        env_path: Optional[Union[str, Path]] = None,
    ) -> bool:
        """Validate Azure Storage setup.

        Args:
            connection_string: Optional Azure Storage connection string
            container_names: Optional list of container names to validate
            env_path: Optional path to .env file

        Returns:
            bool: True if setup is valid
        """
        try:
            conn_str = cls.validate_connection_string(connection_string, env_path)
            blob_service_client = BlobServiceClient.from_connection_string(conn_str)

            if container_names is None:
                container_mapping = cls.load_container_config()
                container_names = list(container_mapping.values())

            # Check each container
            for container in container_names:
                container_client = blob_service_client.get_container_client(container)
                if not container_client.exists():
                    logger.warning(f"Container does not exist: {container}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Azure setup validation failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create/update .env file with connection string
    try:
        AzureSetupUtils.create_env_file(
            "your_connection_string", env_path=".env", overwrite=True
        )
    except Exception as e:
        logger.error(f"Error creating .env file: {e}")

    # Setup containers using environment variable from .env
    AzureSetupUtils.setup_azure_storage()

    # Validate setup
    is_valid = AzureSetupUtils.validate_azure_setup()
    if is_valid:
        logger.info("Azure setup validation successful")
    else:
        logger.warning("Azure setup validation failed")
