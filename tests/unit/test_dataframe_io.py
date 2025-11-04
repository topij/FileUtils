import pandas as pd
from pathlib import Path

from FileUtils.utils.dataframe_io import (
    read_csv_with_inference,
    json_to_dataframe,
    yaml_to_dataframe,
    dataframe_to_json,
    dataframe_to_yaml,
)


def test_json_yaml_roundtrip(tmp_path: Path):
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})

    json_path = tmp_path / "data.json"
    dataframe_to_json(json_path, df, orient="records", indent=2)
    df_json = json_to_dataframe(json_path, encoding="utf-8")
    pd.testing.assert_frame_equal(df.reindex(sorted(df.columns), axis=1), df_json)

    yaml_path = tmp_path / "data.yaml"
    dataframe_to_yaml(
        yaml_path,
        df,
        orient="records",
        yaml_options={"sort_keys": True},
        encoding="utf-8",
    )
    df_yaml = yaml_to_dataframe(yaml_path, encoding="utf-8")
    pd.testing.assert_frame_equal(df.reindex(sorted(df.columns), axis=1), df_yaml)
