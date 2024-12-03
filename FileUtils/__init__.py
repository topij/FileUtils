# src/utils/FileUtils/__init__.py
"""FileUtils package."""
from .file_utils import FileUtils, OutputFileType
from .version import __version__, __author__

# Make version accessible as FileUtils.__version__
__all__ = ["FileUtils", "OutputFileType", "__version__", "__author__"]
