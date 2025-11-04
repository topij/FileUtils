"""Example showing Azure Storage integration with FileUtils."""

import pandas as pd

from FileUtils import FileUtils
from FileUtils.core.base import StorageConnectionError, StorageOperationError
from FileUtils.core.enums import OutputFileType


def setup_azure(connection_string: str):
    """Set up Azure Storage connection."""
    try:
        # Initialize Azure-enabled FileUtils
        utils = FileUtils(storage_type="azure", connection_string=connection_string)
        return utils
    except StorageConnectionError as e:
        print(f"Failed to connect to Azure: {e}")
        return None


def demonstrate_azure_operations(file_utils: FileUtils):
    """Demonstrate Azure Storage operations."""
    try:
        # Create sample data
        df = pd.DataFrame(
            {
                "product": ["Laptop", "Phone", "Tablet"],
                "price": [1200, 800, 500],
                "stock": [50, 100, 75],
            }
        )

        # Save to Azure Storage with metadata
        saved_files, metadata = file_utils.save_with_metadata(
            data={"products": df},
            output_filetype=OutputFileType.PARQUET,  # Using Parquet for efficiency
            output_type="processed",
            file_name="products",
        )
        print(f"Saved files to Azure: {saved_files}")
        print(f"Metadata location: {metadata}")

        # Load from Azure Storage using metadata
        loaded_data = file_utils.load_from_metadata(metadata)
        print("\nLoaded data from Azure:")
        print(loaded_data["products"])

        # Save multiple DataFrames
        df2 = df.copy()
        df2["price"] = df2["price"] * 1.1  # 10% price increase
        df3 = df.groupby("product").agg({"price": "mean", "stock": "sum"}).reset_index()

        multi_df = {"current_prices": df, "new_prices": df2, "summary": df3}

        saved_files, metadata = file_utils.save_with_metadata(
            data=multi_df,
            output_filetype=OutputFileType.XLSX,
            output_type="processed",
            file_name="price_comparison",
        )
        print(f"\nSaved multi-sheet file to Azure: {saved_files}")

        # Load and verify Excel sheets
        sheets = file_utils.load_excel_sheets(saved_files["price_comparison"])
        print("\nLoaded Excel sheets:")
        for name, sheet_df in sheets.items():
            print(f"\n{name}:")
            print(sheet_df)

    except StorageOperationError as e:
        print(f"Storage operation failed: {e}")


if __name__ == "__main__":
    # Get connection string from environment or config
    import os

    from dotenv import load_dotenv

    load_dotenv()
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    if not connection_string:
        print(
            "Azure connection string not found. Please set AZURE_STORAGE_CONNECTION_STRING"
        )
    else:
        utils = setup_azure(connection_string)
        if utils:
            demonstrate_azure_operations(utils)
