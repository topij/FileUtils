from dataclasses import dataclass
from typing import Optional


@dataclass
class SaveResult:
    path: str
    url: Optional[str] = None
    checksum: Optional[str] = None
    mimetype: Optional[str] = None
