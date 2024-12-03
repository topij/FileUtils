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
    saved_files, _ = file_utils.save_data_to_disk(
        data=df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="sample_data",
    )
    print(f"Saved CSV file: {saved_files}")

    # Save as Excel
    saved_files, _ = file_utils.save_data_to_disk(
        data=df,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="sample_data",
    )
    print(f"Saved Excel file: {saved_files}")

    # Save multiple DataFrames to Excel
    df2 = df.copy()
    df2["age"] = df2["age"] + 1
    multi_df = {"original": df, "modified": df2}
    saved_files, _ = file_utils.save_data_to_disk(
        data=multi_df,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="multi_sheet_data",
    )
    print(f"Saved multi-sheet Excel file: {saved_files}")

    # Load data back
    loaded_df = file_utils.load_single_file(
        list(saved_files.values())[0], input_type="processed"
    )
    print("\nLoaded data:")
    print(loaded_df)


if __name__ == "__main__":
    demonstrate_basic_operations()
