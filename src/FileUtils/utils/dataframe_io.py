from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import yaml


def read_csv_with_inference(
    path: Path, encoding: str, quoting: int, fallback_sep: str
) -> pd.DataFrame:
    with open(path, "r", encoding=encoding) as f:
        content = f.read(1024)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(content)
            return pd.read_csv(f, dialect=dialect, encoding=encoding, quoting=quoting)
        except Exception:
            f.seek(0)
            return pd.read_csv(f, sep=fallback_sep, encoding=encoding, quoting=quoting)


def json_to_dataframe(path: Path, encoding: str) -> pd.DataFrame:
    try:
        with open(path, "r", encoding=encoding) as f:
            data = json.load(f)

        if isinstance(data, list):
            df = pd.DataFrame(data)
            return df.reindex(sorted(df.columns), axis=1)
        elif isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, orient="index")
            return df.reindex(sorted(df.columns), axis=1)
        else:
            raise ValueError("JSON must contain list of records or dictionary")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e


def yaml_to_dataframe(path: Path, encoding: str) -> pd.DataFrame:
    try:
        with open(path, "r", encoding=encoding) as f:
            data = yaml.safe_load(f)

        if isinstance(data, list):
            df = pd.DataFrame(data)
            return df.reindex(sorted(df.columns), axis=1)
        elif isinstance(data, dict):
            df = pd.DataFrame.from_dict(data, orient="index")
            return df.reindex(sorted(df.columns), axis=1)
        else:
            raise ValueError("YAML must contain list of records or dictionary")
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}") from e


def dataframe_to_json(
    path: Path, df: pd.DataFrame, orient: str = "records", indent: int = 2
) -> None:
    df.to_json(path, orient=orient, indent=indent)


def dataframe_to_yaml(
    path: Path,
    df: pd.DataFrame,
    orient: str = "records",
    yaml_options: Dict[str, Any] | None = None,
    encoding: str = "utf-8",
) -> None:
    yaml_options = yaml_options or {}
    default_flow_style = yaml_options.pop("default_flow_style", False)
    sort_keys = yaml_options.pop("sort_keys", False)

    if orient == "records":
        data = df.to_dict(orient="records")
    elif orient == "index":
        data = df.to_dict(orient="index")
    else:
        raise ValueError(f"Unsupported YAML orientation: {orient}")

    with open(path, "w", encoding=encoding) as f:
        yaml.safe_dump(
            data,
            f,
            default_flow_style=default_flow_style,
            sort_keys=sort_keys,
            encoding=encoding,
            **yaml_options,
        )
