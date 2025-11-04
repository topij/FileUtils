import pandas as pd
import pytest
from pathlib import Path

from FileUtils.storage.local import LocalStorage


def test_save_dataframes_infers_format_from_suffix(tmp_path: Path):
    storage = LocalStorage(
        {
            "encoding": "utf-8",
            "csv_delimiter": ",",
            "quoting": 0,
        }
    )

    df = pd.DataFrame({"x": [1, 2]})
    data = {"a": df, "b": df}
    base = tmp_path / "multi.csv"

    saved = storage.save_dataframes(data, base)

    assert set(saved.keys()) == {"a", "b"}
    for name, p in saved.items():
        path = Path(p)
        assert path.exists()
        assert path.suffix == ".csv"
        assert path.name == f"multi_{name}.csv"


def test_save_dataframes_excel_single_file(tmp_path: Path):
    storage = LocalStorage(
        {
            "encoding": "utf-8",
            "csv_delimiter": ",",
            "quoting": 0,
        }
    )
    df = pd.DataFrame({"x": [1, 2]})
    data = {"sheet1": df, "sheet2": df}
    base = tmp_path / "book.xlsx"

    saved = storage.save_dataframes(data, base)
    # Both sheets map to the same Excel file path
    assert len(set(saved.values())) == 1
    excel_path = Path(next(iter(saved.values())))
    assert excel_path.exists()
    assert excel_path.suffix == ".xlsx"


def test_save_dataframes_deprecation_file_format_kwarg(tmp_path: Path):
    storage = LocalStorage(
        {
            "encoding": "utf-8",
            "csv_delimiter": ",",
            "quoting": 0,
        }
    )
    df = pd.DataFrame({"x": [1, 2]})
    data = {"a": df}
    base = tmp_path / "multi.csv"

    with pytest.warns(DeprecationWarning):
        saved = storage.save_dataframes(data, base, file_format="json")

    # Despite the kwarg, the suffix rules; file saved is CSV
    p = Path(next(iter(saved.values())))
    assert p.exists()
    assert p.suffix == ".csv"
