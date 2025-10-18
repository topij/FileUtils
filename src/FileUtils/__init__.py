"""FileUtils package."""

from FileUtils.core.file_utils import FileUtils
from FileUtils.core.enums import OutputFileType
from FileUtils.version import __version__, __author__

__all__ = ["FileUtils", "OutputFileType", "__version__", "__author__"]
