"""FileUtils package."""
from FileUtils.core.file_utils import FileUtils, OutputFileType
from FileUtils.version import __version__, __author__

# Expose version at package level
__version__ = __version__
__author__ = __author__

__all__ = ["FileUtils", "OutputFileType", "__version__", "__author__"]