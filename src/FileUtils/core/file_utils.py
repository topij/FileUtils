"""Main FileUtils implementation."""

import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from ..config import get_default_config, load_config, validate_config
from ..core.base import StorageError
from ..core.enums import InputType, OutputArea, OutputFileType, StorageType
from ..core.types import SaveResult
from ..storage.local import LocalStorage
from ..utils.common import format_file_path
from ..utils.logging import setup_logger
from ..utils.pathing import find_project_root
from .base import BaseStorage


class FileUtils:
    """Main FileUtils class with storage abstraction."""

    def __init__(
        self,
        project_root: Optional[Union[str, Path]] = None,
        config_file: Optional[Union[str, Path]] = None,
        storage_type: Union[str, StorageType] = StorageType.LOCAL,
        quiet: bool = False,
        log_level: Optional[Union[str, int]] = None,
        directory_structure: Optional[Dict[str, Any]] = None,
        config_override: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialize FileUtils with enhanced configuration support.

        Args:
            project_root: Root directory for project
            config_file: Path to configuration file
            storage_type: Type of storage backend
            quiet: If True, suppress all logging except CRITICAL errors.
                   Shorthand for log_level=logging.CRITICAL. Useful for
                   automation scripts and structured output (JSON/XML).
            log_level: Logging level (string like "INFO" or logging constant
                      like logging.INFO). If provided, overrides 'quiet' parameter.
            directory_structure: Optional directory structure override
            config_override: Optional dictionary to override any config values
            **kwargs: Additional arguments for storage backend

        Examples:
            # Default behavior (INFO level logging)
            fu = FileUtils()

            # Quiet mode for automation/JSON output
            fu = FileUtils(quiet=True)

            # Custom log level (string)
            fu = FileUtils(log_level="WARNING")

            # Custom log level (logging constant)
            import logging
            fu = FileUtils(log_level=logging.DEBUG)

            # With storage type
            fu = FileUtils(storage_type="azure", quiet=True)

        Note:
            Parameter priority: log_level > quiet > default (INFO)
        """
        # Determine effective log level
        import logging

        if log_level is not None:
            effective_level = log_level  # Explicit log_level has highest priority
        elif quiet:
            effective_level = logging.CRITICAL  # quiet=True suppresses most logging
        else:
            effective_level = None  # Use setup_logger default (INFO)

        # Set up logging
        self.logger = setup_logger(__name__, effective_level)

        # Load base configuration
        self.config = self._load_configuration(
            config_file=config_file,
            directory_structure=directory_structure,
            config_override=config_override,
        )
        validate_config(self.config)

        # Set project root
        self.project_root = (
            Path(project_root) if project_root else self._get_project_root()
        )
        self.logger.info(f"Project root: {self.project_root}")

        # Set up directory structure (only if explicitly requested)
        if kwargs.get("create_directories", False):
            self._setup_directory_structure()

        # Initialize storage backend
        if isinstance(storage_type, str):
            storage_type = StorageType(storage_type.lower())
        self.storage = self._create_storage(storage_type, **kwargs)
        self.logger.info(f"FileUtils initialized with {storage_type.value} storage")

    def _load_configuration(
        self,
        config_file: Optional[Union[str, Path]] = None,
        directory_structure: Optional[Dict[str, Any]] = None,
        config_override: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Load configuration with override support.

        Args:
            config_file: Optional path to configuration file
            directory_structure: Optional directory structure override
            config_override: Optional dictionary to override any config values

        Returns:
            Dict containing merged configuration
        """
        # Start with empty config
        config = {}

        # Load from file if provided
        if config_file:
            config = load_config(config_file)
        else:
            # Load default config if no file provided
            config = get_default_config()

        # Override directory structure if provided
        if directory_structure:
            config["directory_structure"] = directory_structure

        # Apply any additional overrides
        if config_override:
            self._deep_merge(config, config_override)

        return config

    def _get_default_config(self) -> Dict[str, Any]:
        """Deprecated: use config.get_default_config().

        Kept for backward compatibility and emits a deprecation warning.
        """
        warnings.warn(
            "FileUtils._get_default_config is deprecated; using config.get_default_config()",
            DeprecationWarning,
            stacklevel=2,
        )
        return get_default_config()

    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> None:
        """Recursively merge two dictionaries."""
        for key, value in dict2.items():
            if (
                key in dict1
                and isinstance(dict1[key], dict)
                and isinstance(value, dict)
            ):
                self._deep_merge(dict1[key], value)
            else:
                dict1[key] = value

    def get_directory_structure(self) -> Dict[str, Any]:
        """Get current directory structure configuration."""
        return self.config.get("directory_structure", {})

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()

    def _get_project_root(self) -> Path:
        """Determine project root directory using shared helper."""
        root = find_project_root()
        return root or Path.cwd()

    def _setup_directory_structure(self) -> None:
        """Create project directory structure."""
        structure = self.config["directory_structure"]
        for main_dir, sub_dirs in structure.items():
            main_path = self.project_root / main_dir
            main_path.mkdir(parents=True, exist_ok=True)
            for sub_dir in sub_dirs:
                (main_path / sub_dir).mkdir(parents=True, exist_ok=True)

    def _create_storage(self, storage_type: StorageType, **kwargs) -> BaseStorage:
        """Create storage backend instance."""
        if storage_type == StorageType.AZURE:
            try:
                from ..storage.azure import AzureStorage
            except ImportError:
                self.logger.warning(
                    "Azure storage dependencies not installed. "
                    "To use Azure storage, install the package with Azure dependencies: "
                    "pip install 'FileUtils[azure]'"
                )
                if kwargs.get("connection_string"):
                    self.logger.warning(
                        "Falling back to local storage despite connection string being provided."
                    )
                return LocalStorage(self.config)

            try:
                connection_string = kwargs.get("connection_string")
                if not connection_string:
                    self.logger.warning(
                        "Azure connection string not provided. Falling back to local storage."
                    )
                    return LocalStorage(self.config)
                return AzureStorage(connection_string, self.config)
            except Exception as e:
                self.logger.error(f"Failed to initialize Azure storage: {e}")
                self.logger.warning("Falling back to local storage.")

        return LocalStorage(self.config)

    def _get_directory_config(self) -> Dict[str, str]:
        """Get directory configuration with fallback to defaults.

        Returns:
            Dictionary with directory configuration
        """
        directories_config = self.config.get("directories", {})

        # Get data directory name with fallback
        data_directory = directories_config.get("data_directory", "data")

        # Get subdirectory names with fallbacks
        subdirectories = directories_config.get("subdirectories", {})
        raw_dir = subdirectories.get("raw", "raw")
        processed_dir = subdirectories.get("processed", "processed")
        templates_dir = subdirectories.get("templates", "templates")

        return {
            "data_directory": data_directory,
            "raw": raw_dir,
            "processed": processed_dir,
            "templates": templates_dir,
        }

    def get_data_path(
        self, data_type: Union[str, InputType, OutputArea] = "raw"
    ) -> Path:
        """Get the path for a specific data directory.

        Args:
            data_type: Type of data directory (e.g., "raw", "processed")

        Returns:
            Path to the specified data directory
        """
        dir_config = self._get_directory_config()
        data_directory = dir_config["data_directory"]

        # Map data_type to configured subdirectory name
        # Coerce enums to string values
        data_type_str = (
            data_type.value if hasattr(data_type, "value") else str(data_type)
        )

        subdirectory_mapping = {
            "raw": dir_config["raw"],
            "processed": dir_config["processed"],
            "templates": dir_config["templates"],
        }

        # Use configured subdirectory name or fallback to data_type
        subdirectory = subdirectory_mapping.get(data_type_str, data_type_str)

        path = self.project_root / data_directory / subdirectory
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_base_path(
        self,
        directory_type: Optional[Union[str, InputType, OutputArea]] = None,
        root_level: bool = False,
    ) -> Path:
        """Get base path for file operations, supporting both data directory and root-level directories.

        Args:
            directory_type: Directory name/type (e.g., "raw", "processed", "config", "logs")
            root_level: If True, directory is at project root level. If False, it's under data directory.

        Returns:
            Path to the specified directory
        """
        if root_level:
            # Root-level directory (e.g., config, logs at project root)
            if directory_type is None:
                # Default to project root itself
                path = self.project_root
            else:
                # Directory at project root level
                dir_name = (
                    directory_type.value
                    if hasattr(directory_type, "value")
                    else str(directory_type)
                )
                path = self.project_root / dir_name
        else:
            # Data directory (current behavior)
            if directory_type is None:
                directory_type = "raw"  # Default fallback
            path = self.get_data_path(directory_type)

        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_directory(
        self,
        directory_path: Optional[str] = None,
        input_type: Optional[str] = None,
        sub_path: Optional[str] = None,
        exist_ok: bool = True,
        root_level: bool = False,
        parent_dir: Optional[str] = None,  # Legacy parameter for backward compatibility
    ) -> str:
        """Create a directory in storage.

        Args:
            directory_path: Path to directory (relative to input_type/sub_path or absolute).
                           For backward compatibility, can also be called as positional first argument.
            input_type: Type of directory (e.g., "processed", "logs", "charts")
            sub_path: Optional subdirectory path
            exist_ok: If True, don't raise error if directory exists (default: True)
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            parent_dir: Legacy parameter - parent directory (use input_type/sub_path instead)

        Returns:
            str: Path to created directory

        Raises:
            StorageError: If directory creation fails (and exist_ok=False if exists)

        Examples:
            # Create chart directory in run folder
            fu.create_directory("charts", input_type="processed", sub_path="presentations/ACME/run123")

            # Create directory at root level
            fu.create_directory("output", input_type="reports", root_level=True)

            # Legacy usage (still supported)
            fu.create_directory("features", parent_dir="data")
        """
        try:
            if directory_path is None:
                raise ValueError("directory_path must be provided")

            if parent_dir is not None:
                # Legacy mode: parent_dir is at project root level
                # Map parent_dir to input_type with root_level=True
                if input_type is None:
                    input_type = parent_dir
                    root_level = True  # Legacy parent_dir is at root level
                # Check if parent_dir is in configured structure (legacy validation)
                if (
                    "directory_structure" in self.config
                    and parent_dir not in self.config["directory_structure"]
                ):
                    valid_parents = list(self.config["directory_structure"].keys())
                    raise ValueError(
                        f"Invalid parent directory: {parent_dir}. "
                        f"Must be one of: {', '.join(valid_parents)}"
                    )

            # Determine the directory path
            if Path(directory_path).is_absolute():
                # Absolute path
                target_dir = Path(directory_path)
            else:
                # Relative path - construct using input_type/sub_path
                if input_type is None:
                    # Legacy behavior: if parent_dir was None, use data directory
                    # Otherwise, assume relative to project root
                    if parent_dir is None:
                        # Legacy: default to data directory
                        dir_config = self._get_directory_config()
                        target_dir = (
                            self.project_root
                            / dir_config["data_directory"]
                            / directory_path
                        )
                    else:
                        # New behavior: relative to project root
                        target_dir = self.project_root / directory_path
                else:
                    base_dir = self._get_base_path(input_type, root_level=root_level)
                    if sub_path:
                        safe_sub_path = (
                            Path(sub_path).relative_to(Path(sub_path).anchor)
                            if Path(sub_path).is_absolute()
                            else Path(sub_path)
                        )
                        target_dir = base_dir / safe_sub_path / directory_path
                    else:
                        target_dir = base_dir / directory_path

            # Create directory
            target_dir.mkdir(parents=True, exist_ok=exist_ok)

            # Legacy: Add to config structure if not exists (for backward compatibility)
            # This handles both explicit parent_dir and implicit data directory
            if directory_path:
                dir_name_to_add = Path(directory_path).name
                # Determine which parent directory to use for config update
                config_parent_dir = parent_dir
                if config_parent_dir is None and input_type is None:
                    # Legacy: default to data directory
                    dir_config = self._get_directory_config()
                    config_parent_dir = dir_config["data_directory"]

                if config_parent_dir is not None:
                    if (
                        "directory_structure" in self.config
                        and dir_name_to_add
                        not in self.config["directory_structure"].get(
                            config_parent_dir, []
                        )
                    ):
                        if config_parent_dir not in self.config["directory_structure"]:
                            self.config["directory_structure"][config_parent_dir] = []
                        self.config["directory_structure"][config_parent_dir].append(
                            dir_name_to_add
                        )

            self.logger.info(f"Created directory: {target_dir}")
            return str(target_dir)

        except Exception as e:
            # Preserve ValueError and FileExistsError (when exist_ok=False)
            if isinstance(e, ValueError):
                raise
            if isinstance(e, FileExistsError) and not exist_ok:
                raise
            self.logger.error(f"Failed to create directory {directory_path}: {e}")
            raise StorageError(f"Failed to create directory: {e}") from e

    def save_data_to_storage(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        output_filetype: Union[OutputFileType, str] = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        sub_path: Optional[Union[str, Path]] = None,
        include_timestamp: Optional[bool] = None,
        root_level: bool = False,
        structured_result: bool = False,
        **kwargs,
    ) -> Tuple[Union[Dict[str, str], Dict[str, SaveResult]], Optional[str]]:
        """Save data using configured storage backend.

        Args:
            data: DataFrame or dict of DataFrames to save
            output_filetype: Type of output file
            output_type: Type of output (e.g., "processed", "raw", "config", "logs")
            file_name: Base name for output file
            sub_path: Optional subdirectory path relative to output_type directory
            include_timestamp: Whether to include timestamp in filename
            root_level: If True, output_type is a directory at project root level.
                       If False (default), output_type is under the data directory.
            **kwargs: Additional arguments for storage backend

        Returns:
            Tuple of (saved files dict, optional metadata path)
        """
        if isinstance(output_filetype, str):
            output_filetype = OutputFileType(output_filetype.lower())

        # Convert single DataFrame to dict format
        if isinstance(data, pd.DataFrame):
            # Preserve sheet name if provided in kwargs, otherwise use default
            sheet_name = kwargs.get("sheet_name", "Sheet1")
            data = {sheet_name: data}

        # For Excel files, ensure openpyxl engine
        if output_filetype == OutputFileType.XLSX and "engine" not in kwargs:
            kwargs["engine"] = "openpyxl"

        # Generate output path
        base_dir = self._get_base_path(output_type, root_level=root_level)
        full_file_path_str = format_file_path(
            base_dir,
            file_name or "data",
            output_filetype.value,
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
        )

        # Insert sub_path if provided
        full_file_path = Path(full_file_path_str)
        if sub_path:
            # Ensure sub_path is relative
            safe_sub_path = (
                Path(sub_path).relative_to(Path(sub_path).anchor)
                if Path(sub_path).is_absolute()
                else Path(sub_path)
            )
            # Construct the full path: base_dir / sub_path / filename
            full_file_path = base_dir / safe_sub_path / full_file_path.name

        try:
            if len(data) == 1 and output_filetype != OutputFileType.XLSX:
                # For non-Excel single DataFrame
                sheet_name = next(iter(data.keys()))
                # Pass format info through kwargs instead of positional args
                kwargs["sheet_name"] = sheet_name
                saved_path = self.storage.save_dataframe(
                    next(iter(data.values())),
                    full_file_path,
                    **kwargs,
                )
                saved_files = {sheet_name: saved_path}
            else:
                # For Excel or multiple DataFrames
                saved_files = self.storage.save_dataframes(
                    data, full_file_path, output_filetype.value, **kwargs
                )

            self.logger.info(f"Data saved successfully: {saved_files}")
            if structured_result:
                # Map paths to SaveResult with optional url for azure
                def to_res(p: str) -> SaveResult:
                    url = p if str(p).startswith("azure://") else None
                    return SaveResult(path=str(p), url=url)

                saved_struct = {k: to_res(v) for k, v in saved_files.items()}
                return saved_struct, None
            return saved_files, None

        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise StorageError(f"Failed to save data: {e}") from e

    def save_data_to_disk(self, *args, **kwargs):
        """Deprecated: Use save_data_to_storage instead."""
        warnings.warn(
            "save_data_to_disk is deprecated, use save_data_to_storage instead",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.save_data_to_storage(*args, **kwargs)

    def load_single_file(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> pd.DataFrame:
        """Load a single file from storage.

        Args:
            file_path: Path to file, relative to input_type/sub_path directory
                       OR relative to input_type directory if sub_path is None.
            input_type: Type of input directory (e.g., "raw", "processed", "config", "logs")
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to storage backend

        Returns:
            pd.DataFrame: Loaded data

        Raises:
            StorageError: If loading fails
            ValueError: If sub_path is provided and file_path also contains path separators
        """
        try:
            # Handle potential Azure paths (which should not be combined with input_type/sub_path)
            if str(file_path).startswith("azure://"):
                if sub_path:
                    raise ValueError(
                        "Cannot use sub_path with an absolute Azure path in file_path."
                    )
                # Azure path is handled directly by storage backend
                full_path = file_path
            else:
                # Construct local path
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )

                    # Check if file_path also contains directory structure
                    if file_path_obj.parent != Path("."):
                        raise ValueError(
                            f"Cannot provide sub_path ('{sub_path}') when file_path "
                            f"('{file_path}') already contains directory separators."
                        )
                    search_dir = base_dir / safe_sub_path
                    full_path = search_dir / file_path_obj
                else:
                    # No sub_path, use file_path relative to base_dir (allows subdir in file_path)
                    search_dir = base_dir
                    full_path = search_dir / file_path_obj

                # If the exact file doesn't exist, try to find a file with timestamp
                if not full_path.exists():
                    # Look for files matching the pattern (with timestamp)
                    pattern = f"{file_path_obj.stem}_*{file_path_obj.suffix}"
                    matching_files = list(search_dir.glob(pattern))

                    if matching_files:
                        # Use the most recent file (by modification time)
                        full_path = max(matching_files, key=lambda f: f.stat().st_mtime)
                    else:
                        # If no timestamped file found, try the original path
                        pass

            return self.storage.load_dataframe(full_path, **kwargs)
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to load file {file_path}: {e}")
            raise StorageError(f"Failed to load file {file_path}: {e}") from e

    def load_excel_sheets(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Dict[str, pd.DataFrame]:
        """Load all sheets from an Excel file.

        Args:
            file_path: Path to Excel file, relative to input_type/sub_path directory
                       OR relative to input_type directory if sub_path is None.
            input_type: Type of input directory (e.g., "raw", "processed", "config", "logs")
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to storage backend

        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping sheet names to DataFrames

        Raises:
            StorageError: If loading fails
            ValueError: If sub_path is provided and file_path also contains path separators
        """
        try:
            # Handle potential Azure paths
            if str(file_path).startswith("azure://"):
                if sub_path:
                    raise ValueError(
                        "Cannot use sub_path with an absolute Azure path in file_path."
                    )
                full_path = file_path
            else:
                # Construct local path
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )

                    # Check if file_path also contains directory structure
                    if file_path_obj.parent != Path("."):
                        raise ValueError(
                            f"Cannot provide sub_path ('{sub_path}') when file_path "
                            f"('{file_path}') already contains directory separators."
                        )
                    full_path = base_dir / safe_sub_path / file_path_obj
                else:
                    # No sub_path, use file_path relative to base_dir
                    full_path = base_dir / file_path_obj

            return self.storage.load_dataframes(full_path, **kwargs)
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to load Excel sheets from {file_path}: {e}")
            raise StorageError(f"Failed to load Excel sheets: {e}") from e

    def load_multiple_files(
        self,
        file_paths: List[Union[str, Path]],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        file_type: Optional[OutputFileType] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Dict[str, pd.DataFrame]:
        """Load multiple files of the same type from storage.

        Args:
            file_paths: List of file paths, relative to input_type/sub_path directory
                        OR relative to input_type directory if sub_path is None.
                        If sub_path is used, these should be filenames only.
            input_type: Type of input directory (e.g., "raw", "processed", "config", "logs")
            sub_path: Optional subdirectory path relative to input_type directory
            file_type: Optional OutputFileType to enforce specific type checking
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to load_single_file

        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping file stems to loaded DataFrames

        Raises:
            StorageError: If loading fails for any file
            ValueError: If sub_path is provided and any file_path in the list
                        also contains path separators.
        """
        loaded_data = {}
        base_dir = self._get_base_path(
            input_type, root_level=root_level
        )  # Base path for the input type

        # Prepare safe_sub_path once if provided
        safe_sub_path = None
        if sub_path:
            safe_sub_path = (
                Path(sub_path).relative_to(Path(sub_path).anchor)
                if Path(sub_path).is_absolute()
                else Path(sub_path)
            )
            # --- Pre-validation loop ---
            for file_path_item in file_paths:
                file_path_obj = Path(file_path_item)
                if file_path_obj.parent != Path("."):
                    raise ValueError(
                        f"Cannot provide sub_path ('{sub_path}') when a file_path in the list "
                        f"('{file_path_item}') already contains directory separators."
                    )
            # --- End Pre-validation loop ---

        for file_path_item in file_paths:
            file_path_obj = Path(file_path_item)

            if safe_sub_path:
                # If sub_path is used, file_path_item should be a filename only
                # Validation is now done above, so we just construct the path here
                load_path_arg = safe_sub_path / file_path_obj
            else:
                # No sub_path, file_path_item is relative to base_dir
                load_path_arg = file_path_obj  # Pass the relative path as is

            # Validate file type suffix if needed (using the constructed or original relative path)
            current_full_path_for_check = base_dir / load_path_arg
            if (
                file_type
                and current_full_path_for_check.suffix.lstrip(".") != file_type.value
            ):
                raise ValueError(
                    f"File {current_full_path_for_check} does not match type: {file_type.value}"
                )

            # Call load_single_file - it will handle combining base_dir and load_path_arg correctly now
            # Pass down any extra kwargs including root_level
            loaded_data[file_path_obj.stem] = self.load_single_file(
                file_path=load_path_arg,  # Pass the path relative to input_type
                input_type=input_type,
                sub_path=None,  # sub_path logic is handled above for the list context
                root_level=root_level,
                **kwargs,
            )

        return loaded_data

    def save_with_metadata(
        self,
        data: Dict[str, pd.DataFrame],
        output_filetype: OutputFileType = OutputFileType.CSV,
        output_type: str = "processed",
        file_name: Optional[str] = None,
        include_timestamp: Optional[bool] = None,
        **kwargs,
    ) -> Tuple[Dict[str, str], str]:
        """Save data with metadata using configured storage."""
        base_path = format_file_path(
            self.get_data_path(output_type),
            file_name or "data",
            output_filetype.value,
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
        )

        return self.storage.save_with_metadata(
            data, base_path, output_filetype.value, **kwargs
        )

    def load_from_metadata(
        self, metadata_path: Union[str, Path], input_type: str = "raw", **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """Load data using metadata file."""
        if not str(metadata_path).startswith("azure://"):
            metadata_path = self.get_data_path(input_type) / metadata_path

        return self.storage.load_from_metadata(metadata_path, **kwargs)

    def load_yaml(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Any:
        """Load a YAML file as a Python object.

        Args:
            file_path: Path to YAML file, relative to input_type/sub_path directory
                       OR relative to input_type directory if sub_path is None.
            input_type: Type of input directory ("raw", "processed", "config", "logs", etc.)
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to yaml.safe_load or storage backend

        Returns:
            Any: Loaded YAML content as Python object

        Raises:
            StorageError: If loading fails
            ValueError: If sub_path is provided and file_path also contains path separators
        """
        try:
            # Handle potential Azure paths
            if str(file_path).startswith("azure://"):
                if sub_path:
                    raise ValueError(
                        "Cannot use sub_path with an absolute Azure path in file_path."
                    )
                full_path = file_path
            else:
                # Construct local path
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )

                    # Check if file_path also contains directory structure
                    if file_path_obj.parent != Path("."):
                        raise ValueError(
                            f"Cannot provide sub_path ('{sub_path}') when file_path "
                            f"('{file_path}') already contains directory separators."
                        )
                    full_path = base_dir / safe_sub_path / file_path_obj
                else:
                    # No sub_path, use file_path relative to base_dir
                    full_path = base_dir / file_path_obj

            return self.storage.load_yaml(full_path, **kwargs)
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to load YAML file {file_path}: {e}")
            raise StorageError(f"Failed to load YAML file {file_path}: {e}") from e

    def load_json(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Any:
        """Load a JSON file as a Python object.

        Args:
            file_path: Path to JSON file, relative to input_type/sub_path directory
                       OR relative to input_type directory if sub_path is None.
            input_type: Type of input directory ("raw", "processed", "config", "logs", etc.)
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to json.load or storage backend

        Returns:
            Any: Loaded JSON content as Python object

        Raises:
            StorageError: If loading fails
            ValueError: If sub_path is provided and file_path also contains path separators
        """
        try:
            # Handle potential Azure paths
            if str(file_path).startswith("azure://"):
                if sub_path:
                    raise ValueError(
                        "Cannot use sub_path with an absolute Azure path in file_path."
                    )
                full_path = file_path
            else:
                # Construct local path
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )

                    # Check if file_path also contains directory structure
                    if file_path_obj.parent != Path("."):
                        raise ValueError(
                            f"Cannot provide sub_path ('{sub_path}') when file_path "
                            f"('{file_path}') already contains directory separators."
                        )
                    full_path = base_dir / safe_sub_path / file_path_obj
                else:
                    # No sub_path, use file_path relative to base_dir
                    full_path = base_dir / file_path_obj

            return self.storage.load_json(full_path, **kwargs)
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to load JSON file {file_path}: {e}")
            raise StorageError(f"Failed to load JSON file {file_path}: {e}") from e

    # def get_directory_structure(self) -> Dict[str, List[str]]:
    #     """Get the actual current directory structure by scanning the filesystem.

    #     Returns:
    #         Dict[str, List[str]]: Dictionary mapping parent directories to their existing subdirectories

    #     Example:
    #         >>> file_utils.get_directory_structure()
    #         {
    #             'data': ['raw', 'processed', 'interim', 'features'],
    #             'reports': ['figures', 'monthly'],
    #             'models': ['trained']
    #         }
    #     """
    #     structure = {}

    #     # Scan through base directories defined in config
    #     for parent_dir in self.config["directory_structure"].keys():
    #         parent_path = self.project_root / parent_dir

    #         # Skip if parent directory doesn't exist
    #         if not parent_path.exists():
    #             continue

    #         # Get all existing subdirectories
    #         subdirs = [
    #             path.name
    #             for path in parent_path.iterdir()
    #             if path.is_dir()
    #             and not path.name.startswith(".")  # Skip hidden directories
    #         ]

    #         structure[parent_dir] = sorted(subdirs)  # Sort for consistent order

    #     return structure

    def set_logging_level(self, level: str) -> None:
        """Set the logging level after initialization.

        Args:
            level: Logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

        Raises:
            ValueError: If invalid logging level provided
        """
        try:
            # Validate logging level
            level = level.upper()
            if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                raise ValueError(
                    f"Invalid logging level: {level}. "
                    "Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL"
                )

            # Update logger level
            self.logger.setLevel(level)

            # Update config
            self.config["logging_level"] = level

            self.logger.info(f"Logging level set to: {level}")

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to set logging level: {e}")

    def save_document_to_storage(
        self,
        content: Union[str, Dict[str, Any], bytes, Path],
        output_filetype: Union[OutputFileType, str],
        output_type: str = "processed",
        file_name: Optional[str] = None,
        sub_path: Optional[Union[str, Path]] = None,
        include_timestamp: Optional[bool] = None,
        root_level: bool = False,
        structured_result: bool = False,
        **kwargs,
    ) -> Tuple[Union[str, SaveResult], Optional[str]]:
        """Save document content using configured storage backend.

        Args:
            content: Document content (string, dict, bytes, or Path).
                    For PPTX: accepts bytes (file content) or Path/str (path to source .pptx file).
            output_filetype: Type of output file (DOCX, MARKDOWN, PDF, PPTX, JSON, YAML)
            output_type: Type of output (e.g., "processed", "raw", "config", "logs")
            file_name: Base name for output file
            sub_path: Optional subdirectory path relative to output_type directory
            include_timestamp: Whether to include timestamp in filename
            root_level: If True, output_type is a directory at project root level.
                       If False (default), output_type is under the data directory.
            **kwargs: Additional arguments for storage backend

        Returns:
            Tuple of (saved file path, optional metadata path)

        Raises:
            ValueError: If output_filetype is not a document format
            StorageError: If saving fails
        """
        if isinstance(output_filetype, str):
            output_filetype = OutputFileType(output_filetype.lower())

        # Validate document format
        document_formats = {
            OutputFileType.DOCX,
            OutputFileType.MARKDOWN,
            OutputFileType.PDF,
            OutputFileType.PPTX,
            OutputFileType.JSON,
            OutputFileType.YAML,
        }
        if output_filetype not in document_formats:
            raise ValueError(
                f"Invalid document format: {output_filetype}. "
                f"Must be one of: {', '.join(fmt.value for fmt in document_formats)}"
            )

        # Generate output path
        base_dir = self._get_base_path(output_type, root_level=root_level)
        full_file_path_str = format_file_path(
            base_dir,
            file_name or "document",
            output_filetype.value,
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
        )

        # Insert sub_path if provided
        full_file_path = Path(full_file_path_str)
        if sub_path:
            # Ensure sub_path is relative
            safe_sub_path = (
                Path(sub_path).relative_to(Path(sub_path).anchor)
                if Path(sub_path).is_absolute()
                else Path(sub_path)
            )
            # Construct the full path: base_dir / sub_path / filename
            full_file_path = base_dir / safe_sub_path / full_file_path.name

        try:
            saved_path = self.storage.save_document(
                content, full_file_path, output_filetype.value, **kwargs
            )
            self.logger.info(f"Document saved successfully: {saved_path}")
            if structured_result:
                url = saved_path if str(saved_path).startswith("azure://") else None
                return SaveResult(path=str(saved_path), url=url), None
            return saved_path, None

        except Exception as e:
            self.logger.error(f"Failed to save document: {e}")
            raise StorageError(f"Failed to save document: {e}") from e

    def save_bytes(
        self,
        content: bytes,
        file_stem: str,
        *,
        sub_path: Optional[Union[str, Path]] = None,
        output_type: Union[str, OutputArea] = "processed",
        file_ext: str = "png",
        include_timestamp: Optional[bool] = None,
        root_level: bool = False,
        **kwargs,
    ) -> str:
        """Convenience method to save raw bytes with standardized pathing.

        Returns the saved path or azure URL.
        """
        base_dir = self._get_base_path(output_type, root_level=root_level)
        full_file_path_str = format_file_path(
            base_dir,
            file_stem,
            file_ext,
            (
                include_timestamp
                if include_timestamp is not None
                else self.config.get("include_timestamp", True)
            ),
        )

        full_file_path = Path(full_file_path_str)
        if sub_path:
            safe_sub_path = (
                Path(sub_path).relative_to(Path(sub_path).anchor)
                if Path(sub_path).is_absolute()
                else Path(sub_path)
            )
            full_file_path = base_dir / safe_sub_path / full_file_path.name

        saved_path = self.storage.save_bytes(content, full_file_path)
        self.logger.info(f"Bytes saved successfully: {saved_path}")
        return saved_path

    def load_document_from_storage(
        self,
        file_path: Union[str, Path],
        input_type: str = "raw",
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Union[str, Dict[str, Any], bytes]:
        """Load document content from storage.

        Args:
            file_path: Path to file, relative to input_type/sub_path directory
                       OR relative to input_type directory if sub_path is None.
            input_type: Type of input directory (e.g., "raw", "processed", "config", "logs")
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            **kwargs: Additional arguments passed to storage backend

        Returns:
            Document content (string, dict, or bytes depending on file type).
            For PPTX: returns bytes.

        Raises:
            StorageError: If loading fails
            ValueError: If sub_path is provided and file_path also contains path separators
        """
        try:
            # Handle potential Azure paths
            if str(file_path).startswith("azure://"):
                if sub_path:
                    raise ValueError(
                        "Cannot use sub_path with an absolute Azure path in file_path."
                    )
                full_path = file_path
            else:
                # Construct local path
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )

                    # Check if file_path also contains directory structure
                    if file_path_obj.parent != Path("."):
                        raise ValueError(
                            f"Cannot provide sub_path ('{sub_path}') when file_path "
                            f"('{file_path}') already contains directory separators."
                        )
                    search_dir = base_dir / safe_sub_path
                    full_path = search_dir / file_path_obj
                else:
                    # No sub_path, use file_path relative to base_dir
                    search_dir = base_dir
                    full_path = search_dir / file_path_obj

                # If the exact file doesn't exist, try to find a file with timestamp
                if not full_path.exists():
                    # Look for files matching the pattern (with timestamp)
                    pattern = f"{file_path_obj.stem}_*{file_path_obj.suffix}"
                    matching_files = list(search_dir.glob(pattern))

                    if matching_files:
                        # Use the most recent file (by modification time)
                        full_path = max(matching_files, key=lambda f: f.stat().st_mtime)
                    else:
                        # If no timestamped file found, try the original path
                        pass

            return self.storage.load_document(full_path, **kwargs)
        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to load document {file_path}: {e}")
            raise StorageError(f"Failed to load document {file_path}: {e}") from e

    def convert_excel_to_csv_with_structure(
        self,
        excel_file_path: Union[str, Path],
        input_type: str = "raw",
        output_type: str = "processed",
        file_name: Optional[str] = None,
        preserve_structure: bool = True,
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> Tuple[Dict[str, str], str]:
        """Convert Excel file with multiple worksheets to CSV files while maintaining
        workbook structure.

        This method loads all sheets from an Excel file, converts each sheet to a
        separate CSV file, and creates a JSON file containing the workbook structure
        and metadata.

        Args:
            excel_file_path: Path to Excel file, relative to input_type/sub_path directory
            input_type: Type of input directory (e.g., "raw", "processed", "config", "logs")
            output_type: Type of output directory (e.g., "processed", "raw", "config", "logs")
            file_name: Base name for output files (defaults to Excel filename without extension)
            preserve_structure: Whether to create a structure JSON file
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type and output_type are directories at project
                       root level. If False (default), they are under the data directory.
            **kwargs: Additional arguments for CSV saving (encoding, delimiter, etc.)

        Returns:
            Tuple of (csv_files_dict, structure_json_path):
            - csv_files_dict: Dictionary mapping sheet names to CSV file paths
            - structure_json_path: Path to the structure JSON file (empty string if preserve_structure=False)

        Raises:
            StorageError: If conversion fails
            ValueError: If sub_path is provided and file_path also contains path separators

        Example:
            >>> file_utils = FileUtils()
            >>> csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
            ...     "workbook.xlsx",
            ...     file_name="converted_workbook"
            ... )
            >>> # Result:
            >>> # csv_files = {
            >>> #     "Sheet1": "data/processed/converted_workbook_Sheet1.csv",
            >>> #     "Sheet2": "data/processed/converted_workbook_Sheet2.csv"
            >>> # }
            >>> # structure_file = "data/processed/converted_workbook_structure.json"
        """
        try:
            # Load all sheets from Excel file
            self.logger.info(f"Loading Excel file: {excel_file_path}")
            sheets_dict = self.load_excel_sheets(
                excel_file_path,
                input_type=input_type,
                sub_path=sub_path,
                root_level=root_level,
                **kwargs,
            )

            if not sheets_dict:
                raise StorageError(f"No sheets found in Excel file: {excel_file_path}")

            # Determine output file name
            if file_name is None:
                excel_path = Path(excel_file_path)
                file_name = excel_path.stem

            # Convert each sheet to CSV
            csv_files = {}
            structure_data = {
                "workbook_info": {
                    "source_file": str(excel_file_path),
                    "conversion_timestamp": pd.Timestamp.now().isoformat(),
                    "total_sheets": len(sheets_dict),
                    "sheet_names": list(sheets_dict.keys()),
                },
                "sheets": {},
            }

            self.logger.info(f"Converting {len(sheets_dict)} sheets to CSV format")

            for sheet_name, df in sheets_dict.items():
                # Create CSV file name
                csv_file_name = f"{file_name}_{sheet_name}"

                # Save sheet as CSV
                saved_files, _ = self.save_data_to_storage(
                    data=df,
                    output_filetype=OutputFileType.CSV,
                    output_type=output_type,
                    file_name=csv_file_name,
                    sub_path=sub_path,
                    root_level=root_level,
                    **kwargs,
                )

                # Get the CSV file path (should be single file)
                saved_val = list(saved_files.values())[0]
                if hasattr(saved_val, "path"):
                    csv_file_path = saved_val.path  # type: ignore
                else:
                    csv_file_path = str(saved_val)
                csv_files[sheet_name] = csv_file_path

                # Collect sheet metadata for structure file
                if preserve_structure:
                    structure_data["sheets"][sheet_name] = {
                        "csv_file": csv_file_path,
                        "csv_filename": Path(csv_file_path).name,
                        "dimensions": {"rows": len(df), "columns": len(df.columns)},
                        "columns": {
                            "names": df.columns.tolist(),
                            "dtypes": df.dtypes.astype(str).to_dict(),
                            "count": len(df.columns),
                        },
                        "data_info": {
                            "has_index": df.index.name is not None,
                            "index_name": df.index.name,
                            "memory_usage": df.memory_usage(deep=True).sum(),
                            "null_counts": df.isnull().sum().to_dict(),
                        },
                    }

                self.logger.debug(
                    f"Converted sheet '{sheet_name}' to CSV: {csv_file_path}"
                )

            # Save structure JSON file if requested
            structure_json_path = ""
            if preserve_structure:
                structure_file_name = f"{file_name}_structure"
                saved_path, _ = self.save_document_to_storage(
                    content=structure_data,
                    output_filetype=OutputFileType.JSON,
                    output_type=output_type,
                    file_name=structure_file_name,
                    sub_path=sub_path,
                    root_level=root_level,
                )
                if isinstance(saved_path, str):
                    structure_json_path = saved_path
                else:
                    structure_json_path = str(saved_path)
                self.logger.info(f"Created structure file: {structure_json_path}")

            self.logger.info(
                f"Successfully converted Excel file to {len(csv_files)} CSV files"
            )
            return csv_files, structure_json_path

        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to convert Excel file {excel_file_path}: {e}")
            raise StorageError(
                f"Failed to convert Excel file {excel_file_path}: {e}"
            ) from e

    def convert_csv_to_excel_workbook(
        self,
        structure_json_path: Union[str, Path],
        input_type: str = "processed",
        output_type: str = "processed",
        file_name: Optional[str] = None,
        sub_path: Optional[Union[str, Path]] = None,
        root_level: bool = False,
        **kwargs,
    ) -> str:
        """Convert CSV files back to Excel workbook using structure JSON.

        This method reconstructs an Excel workbook from CSV files that were previously
        created using convert_excel_to_csv_with_structure(). It uses the structure JSON
        to determine which CSV files to load and how to organize them into sheets.

        Args:
            structure_json_path: Path to the structure JSON file created during CSV conversion
            input_type: Type of input directory where CSV files are located
            output_type: Type of output directory for the Excel workbook
            file_name: Base name for output Excel file (defaults to structure file name)
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type and output_type are directories at project
                       root level. If False (default), they are under the data directory.
            **kwargs: Additional arguments for Excel saving (engine, etc.)

        Returns:
            Path to the created Excel workbook file

        Raises:
            StorageError: If conversion fails
            ValueError: If structure JSON is invalid or CSV files are missing

        Example:
            >>> file_utils = FileUtils()
            >>> # First convert Excel to CSV
            >>> csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
            ...     "workbook.xlsx", file_name="converted_workbook"
            ... )
            >>> # ... make changes to CSV files ...
            >>> # Then convert back to Excel
            >>> excel_path = file_utils.convert_csv_to_excel_workbook(
            ...     structure_file, file_name="reconstructed_workbook"
            ... )
        """
        try:
            import json

            # Load structure JSON
            self.logger.info(f"Loading structure file: {structure_json_path}")
            structure_path = Path(structure_json_path)

            if not structure_path.exists():
                raise StorageError(f"Structure file not found: {structure_json_path}")

            with open(structure_path, "r") as f:
                structure_data = json.load(f)

            # Validate structure data
            if "sheets" not in structure_data:
                raise ValueError("Invalid structure JSON: missing 'sheets' key")

            # Determine output file name
            if file_name is None:
                file_name = (
                    structure_path.stem.replace("_structure", "") + "_reconstructed"
                )

            # Load CSV files and reconstruct workbook
            workbook_data = {}
            missing_files = []

            self.logger.info(
                f"Reconstructing workbook from {len(structure_data['sheets'])} CSV files"
            )

            for sheet_name, sheet_info in structure_data["sheets"].items():
                csv_filename = sheet_info.get("csv_filename")
                if not csv_filename:
                    self.logger.warning(
                        f"No CSV filename found for sheet '{sheet_name}', skipping"
                    )
                    continue

                try:
                    # Load CSV file
                    df = self.load_single_file(
                        csv_filename,
                        input_type=input_type,
                        sub_path=sub_path,
                        root_level=root_level,
                    )
                    workbook_data[sheet_name] = df
                    self.logger.debug(
                        f"Loaded sheet '{sheet_name}' from {csv_filename}"
                    )

                except Exception as e:
                    missing_files.append(f"{sheet_name}: {csv_filename}")
                    self.logger.warning(
                        f"Failed to load CSV file for sheet '{sheet_name}': {e}"
                    )

            if not workbook_data:
                raise StorageError(
                    f"No CSV files could be loaded. Missing files: {missing_files}"
                )

            if missing_files:
                self.logger.warning(f"Some CSV files were missing: {missing_files}")

            # Save as Excel workbook
            self.logger.info(
                f"Saving reconstructed workbook with {len(workbook_data)} sheets"
            )
            saved_files, _ = self.save_data_to_storage(
                data=workbook_data,
                output_filetype=OutputFileType.XLSX,
                output_type=output_type,
                file_name=file_name,
                sub_path=sub_path,
                root_level=root_level,
                **kwargs,
            )

            # Get the Excel file path (should be single file)
            excel_file_path = list(saved_files.values())[0]

            # Create reconstruction metadata
            reconstruction_info = {
                "reconstruction_info": {
                    "source_structure_file": str(structure_json_path),
                    "reconstruction_timestamp": pd.Timestamp.now().isoformat(),
                    "original_workbook_info": structure_data.get("workbook_info", {}),
                    "sheets_reconstructed": len(workbook_data),
                    "sheets_original": len(structure_data["sheets"]),
                    "missing_files": missing_files,
                },
                "sheets": {
                    sheet_name: {
                        "csv_source": sheet_info.get("csv_filename"),
                        "dimensions": {"rows": len(df), "columns": len(df.columns)},
                        "columns": {
                            "names": df.columns.tolist(),
                            "count": len(df.columns),
                        },
                    }
                    for sheet_name, df in workbook_data.items()
                },
            }

            # Save reconstruction metadata
            metadata_file_name = f"{file_name}_reconstruction_metadata"
            self.save_document_to_storage(
                content=reconstruction_info,
                output_filetype=OutputFileType.JSON,
                output_type=output_type,
                file_name=metadata_file_name,
                sub_path=sub_path,
                root_level=root_level,
            )

            self.logger.info(
                f"Successfully reconstructed Excel workbook: {excel_file_path}"
            )
            return str(excel_file_path)

        except Exception as e:
            if isinstance(e, (ValueError, StorageError)):
                raise
            self.logger.error(f"Failed to convert CSV files to Excel workbook: {e}")
            raise StorageError(
                f"Failed to convert CSV files to Excel workbook: {e}"
            ) from e

    def file_exists(
        self,
        file_path: str,
        input_type: Optional[str] = None,
        sub_path: Optional[str] = None,
        root_level: bool = False,
    ) -> bool:
        """Check if a file exists in storage.

        Args:
            file_path: Path to file (relative to input_type/sub_path or absolute)
            input_type: Type of input directory (e.g., "raw", "config", "processed", "templates")
            sub_path: Optional subdirectory path relative to input_type directory
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.

        Returns:
            bool: True if file exists, False otherwise. Never raises exceptions.

        Examples:
            # Check config file
            fu.file_exists("ACME.config-defaults.yml", input_type="config", sub_path="ACME")

            # Check template file (root level)
            fu.file_exists("ADP-template_ADM.pptx", input_type="templates", sub_path="ADM", root_level=True)

            # Check absolute path
            fu.file_exists("/absolute/path/to/file.yml")
        """
        try:
            # Handle Azure paths
            if str(file_path).startswith("azure://"):
                if sub_path:
                    # Can't use sub_path with absolute Azure path
                    return False
                return self.storage.exists(file_path)

            # Handle absolute paths
            if Path(file_path).is_absolute():
                return self.storage.exists(file_path)

            # Construct path using input_type/sub_path
            if input_type is None:
                # If no input_type, assume relative to project root
                full_path = self.project_root / file_path
            else:
                base_dir = self._get_base_path(input_type, root_level=root_level)
                file_path_obj = Path(file_path)

                if sub_path:
                    # Ensure sub_path is relative
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )
                    full_path = base_dir / safe_sub_path / file_path_obj
                else:
                    full_path = base_dir / file_path_obj

            return self.storage.exists(full_path)
        except Exception:
            # Return False on any error (per requirements)
            return False

    def list_directory(
        self,
        directory_path: Optional[str] = None,
        input_type: Optional[str] = None,
        sub_path: Optional[str] = None,
        pattern: Optional[str] = None,
        root_level: bool = False,
        files_only: bool = False,
        directories_only: bool = False,
    ) -> List[str]:
        """List files and directories in a storage path.

        Args:
            directory_path: Path to directory (relative to input_type/sub_path or absolute).
                            If None and input_type provided, lists input_type directory.
            input_type: Type of input directory (e.g., "raw", "config", "processed", "templates")
            sub_path: Optional subdirectory path relative to input_type directory
            pattern: Optional glob pattern to filter results (e.g., "*.yml", "*.pptx", "ACME.*")
            root_level: If True, input_type is a directory at project root level.
                       If False (default), input_type is under the data directory.
            files_only: If True, return only files (exclude directories)
            directories_only: If True, return only directories (exclude files)

        Returns:
            List[str]: List of file/directory names in the directory (not full paths).
                      Returns empty list if directory doesn't exist or on error.

        Examples:
            # List all config files for a customer
            fu.list_directory(input_type="config", sub_path="ACME", pattern="*.yml")

            # List templates in customer directory (root level)
            fu.list_directory(input_type="templates", sub_path="ADM", root_level=True, pattern="*.pptx")

            # List all files in a directory
            fu.list_directory("/absolute/path/to/dir", files_only=True)
        """
        try:
            # Handle Azure paths
            if directory_path and str(directory_path).startswith("azure://"):
                if sub_path:
                    # Can't use sub_path with absolute Azure path
                    return []
                return self.storage.list_directory(
                    directory_path,
                    pattern=pattern,
                    files_only=files_only,
                    directories_only=directories_only,
                )

            # Determine the directory to list
            if directory_path is None:
                # If no directory_path but input_type provided, list input_type directory
                if input_type is None:
                    return []
                base_dir = self._get_base_path(input_type, root_level=root_level)
                if sub_path:
                    safe_sub_path = (
                        Path(sub_path).relative_to(Path(sub_path).anchor)
                        if Path(sub_path).is_absolute()
                        else Path(sub_path)
                    )
                    target_dir = base_dir / safe_sub_path
                else:
                    target_dir = base_dir
            else:
                # Handle absolute paths
                if Path(directory_path).is_absolute():
                    target_dir = Path(directory_path)
                else:
                    # Relative path - construct using input_type/sub_path
                    if input_type is None:
                        # Assume relative to project root
                        target_dir = self.project_root / directory_path
                    else:
                        base_dir = self._get_base_path(
                            input_type, root_level=root_level
                        )
                        if sub_path:
                            safe_sub_path = (
                                Path(sub_path).relative_to(Path(sub_path).anchor)
                                if Path(sub_path).is_absolute()
                                else Path(sub_path)
                            )
                            target_dir = base_dir / safe_sub_path / directory_path
                        else:
                            target_dir = base_dir / directory_path

            return self.storage.list_directory(
                target_dir,
                pattern=pattern,
                files_only=files_only,
                directories_only=directories_only,
            )
        except Exception:
            # Return empty list on any error (per requirements)
            return []

    def open_run(
        self,
        sub_path_prefix: str,
        customer: str,
        *,
        fmt: str = "%Y%m%d-%H%M%S",
    ) -> Tuple[str, str]:
        """Create a standardized run sub_path and return (sub_path, run_id)."""
        run_id = pd.Timestamp.now().strftime(fmt)
        sub_path = f"{sub_path_prefix}/{customer}/{run_id}"
        return sub_path, run_id
