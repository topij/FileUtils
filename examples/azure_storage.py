"""Example showing Azure Storage integration with FileUtils."""

import pandas as pd
from FileUtils import FileUtils
from FileUtils.azure_setup import AzureSetupUtils


def setup_azure():
    """Set up Azure Storage containers."""
    # Ensure Azure is properly configured
    AzureSetupUtils.setup_azure_storage()

    # Validate setup
    is_valid = AzureSetupUtils.validate_azure_setup()
    if not is_valid:
        raise RuntimeError("Azure setup validation failed")

    return is_valid


def demonstrate_azure_operations():
    """Demonstrate Azure Storage operations."""
    # Initialize Azure-enabled FileUtils
    file_utils = FileUtils.create_azure_utils()

    # Create sample data
    df = pd.DataFrame(
        {
            "product": ["Laptop", "Phone", "Tablet"],
            "price": [1200, 800, 500],
            "stock": [50, 100, 75],
        }
    )

    # Save to Azure Storage
    saved_files, _ = file_utils.save_data_to_disk(
        data=df, output_filetype="csv", output_type="processed", file_name="products"
    )
    print(f"Saved files to Azure: {saved_files}")

    # Load from Azure Storage
    azure_path = list(saved_files.values())[0]
    loaded_df = file_utils.load_single_file(azure_path)
    print("\nLoaded data from Azure:")
    print(loaded_df)

    # Save multiple DataFrames
    df2 = df.copy()
    df2["price"] = df2["price"] * 1.1  # 10% price increase
    multi_df = {"current_prices": df, "new_prices": df2}

    saved_files, _ = file_utils.save_data_to_disk(
        data=multi_df,
        output_filetype="xlsx",
        output_type="processed",
        file_name="price_comparison",
    )
    print(f"\nSaved multi-sheet file to Azure: {saved_files}")


if __name__ == "__main__":
    if setup_azure():
        demonstrate_azure_operations()
