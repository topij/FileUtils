"""Example showing basic usage of FileUtils for local storage operations."""

import pandas as pd
from FileUtils import FileUtils, OutputFileType


def demonstrate_basic_operations():
    """Demonstrate basic FileUtils operations."""
    # Initialize FileUtils
    file_utils = FileUtils()

    # Create sample data
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [25, 30, 35],
            "city": ["New York", "London", "Paris"],
        }
    )

    # Save as CSV
    saved_files, metadata = file_utils.save_data_to_storage(
        data=df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="sample_data",
    )
    print(f"Saved CSV file: {saved_files}")

    # Save as Excel
    saved_files, metadata = file_utils.save_data_to_storage(
        data=df,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="sample_data",
    )
    print(f"Saved Excel file: {saved_files}")

    # Save multiple DataFrames to Excel with metadata
    df2 = df.copy()
    df2["age"] = df2["age"] + 1

    # Create summary without multi-index
    summary_df = df.groupby("city").agg({"age": ["mean", "count"]}).reset_index()
    # Flatten column names
    summary_df.columns = [
        f"{col[0]}_{col[1]}" if col[1] else col[0] for col in summary_df.columns
    ]

    multi_df = {"original": df, "modified": df2, "summary": summary_df}

    saved_files, metadata = file_utils.save_with_metadata(
        data=multi_df,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="multi_sheet_data",
    )
    print(f"Saved multi-sheet Excel file with metadata: {saved_files}")

    # Load data using metadata
    loaded_data = file_utils.load_from_metadata(metadata)
    print("\nLoaded data from metadata:")
    for sheet_name, sheet_df in loaded_data.items():
        print(f"\n{sheet_name}:")
        print(sheet_df)


if __name__ == "__main__":
    demonstrate_basic_operations()
