from pathlib import Path
from FileUtils.utils.pathing import find_project_root


def test_find_project_root_current_dir(tmp_path: Path, monkeypatch):
    # Simulate a project root by creating pyproject.toml
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[build-system]\n")
    root = find_project_root()
    assert root == tmp_path


