from pathlib import Path
from typing import Optional


def find_project_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Find project root by scanning upwards for common indicators.

    Indicators: .git, pyproject.toml, setup.py, environment.yaml
    """
    current_dir = Path.cwd() if start_dir is None else Path(start_dir)
    indicators = [".git", "pyproject.toml", "setup.py", "environment.yaml"]

    while current_dir != current_dir.parent:
        if any((current_dir / indicator).exists() for indicator in indicators):
            return current_dir
        current_dir = current_dir.parent

    return None


