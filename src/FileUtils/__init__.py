"""FileUtils package."""

from FileUtils.core.enums import OutputFileType
from FileUtils.core.file_utils import FileUtils
from FileUtils.core.types import SaveResult
from FileUtils.version import __author__, __version__

# Template system imports (optional)
try:
    from FileUtils.templates import (DocxTemplateManager,
                                     MarkdownToDocxConverter, StyleMapper)

    __all__ = [
        "FileUtils",
        "OutputFileType",
        "SaveResult",
        "__version__",
        "__author__",
        "DocxTemplateManager",
        "MarkdownToDocxConverter",
        "StyleMapper",
    ]
except ImportError:
    __all__ = ["FileUtils", "OutputFileType", "SaveResult", "__version__", "__author__"]
