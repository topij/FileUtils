"""Example: Complete Excel ↔ CSV Round-Trip Workflow

This script demonstrates the complete round-trip workflow:
1. Excel → CSV conversion with structure preservation
2. Data modification and processing on CSV files
3. CSV → Excel reconstruction for distribution

This is particularly useful for data processing pipelines where you need to:
- Work with individual CSV files for analysis
- Make modifications to the data
- Distribute the results as a consolidated Excel workbook

Features demonstrated:
- Excel to CSV conversion with structure preservation
- CSV data modification and processing
- CSV to Excel reconstruction
- Metadata tracking throughout the workflow
- Error handling for missing files
"""

import sys
from pathlib import Path
import pandas as pd
import json

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)  # Insert at beginning to prioritize

from FileUtils import FileUtils, OutputFileType


def create_sample_workbook():
    """Create a sample Excel workbook for demonstration."""
    print("=== Creating Sample Excel Workbook ===\n")

    file_utils = FileUtils()

    # Create realistic business data
    # Sheet 1: Sales data
    sales_df = pd.DataFrame(
        {
            "sale_id": [1, 2, 3, 4, 5, 6],
            "customer_name": [
                "Alice Corp",
                "Bob Industries",
                "Charlie Ltd",
                "Diana Inc",
                "Eve Systems",
                "Frank Co",
            ],
            "product": [
                "Widget A",
                "Widget B",
                "Widget A",
                "Widget C",
                "Widget B",
                "Widget A",
            ],
            "quantity": [10, 5, 15, 8, 12, 20],
            "unit_price": [25.50, 45.00, 25.50, 60.00, 45.00, 25.50],
            "sale_date": pd.date_range("2024-01-01", periods=6, freq="W"),
            "sales_rep": ["John", "Jane", "John", "Bob", "Jane", "John"],
        }
    )

    # Calculate total for each sale
    sales_df["total_amount"] = sales_df["quantity"] * sales_df["unit_price"]

    # Sheet 2: Customer information
    customers_df = pd.DataFrame(
        {
            "customer_name": [
                "Alice Corp",
                "Bob Industries",
                "Charlie Ltd",
                "Diana Inc",
                "Eve Systems",
                "Frank Co",
            ],
            "industry": [
                "Technology",
                "Manufacturing",
                "Finance",
                "Healthcare",
                "Technology",
                "Retail",
            ],
            "company_size": ["Large", "Medium", "Small", "Large", "Medium", "Small"],
            "contact_email": [
                "alice@alicecorp.com",
                "bob@bobind.com",
                "charlie@charlie.com",
                "diana@dianainc.com",
                "eve@evesys.com",
                "frank@frankco.com",
            ],
            "annual_revenue": [5000000, 2000000, 800000, 12000000, 3000000, 1500000],
        }
    )

    # Sheet 3: Product catalog
    products_df = pd.DataFrame(
        {
            "product": ["Widget A", "Widget B", "Widget C"],
            "category": ["Basic", "Premium", "Enterprise"],
            "cost": [15.00, 30.00, 40.00],
            "margin": [10.50, 15.00, 20.00],
            "inventory": [100, 50, 25],
            "supplier": ["Supplier A", "Supplier B", "Supplier C"],
        }
    )

    # Combine all sheets
    workbook_data = {
        "Sales": sales_df,
        "Customers": customers_df,
        "Products": products_df,
    }

    # Save as Excel workbook
    saved_files, metadata = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="business_data",
    )

    excel_file_path = list(saved_files.values())[0]
    print(f"✓ Created sample Excel workbook: {excel_file_path}")
    print(f"  - Sheets: {list(workbook_data.keys())}")
    print(f"  - Total records: {sum(len(df) for df in workbook_data.values())}")

    return excel_file_path


def demonstrate_excel_to_csv_conversion(excel_file_path):
    """Demonstrate Excel to CSV conversion."""
    print("\n=== Step 1: Excel to CSV Conversion ===\n")

    file_utils = FileUtils()

    # Convert Excel to CSV with structure preservation
    print("Converting Excel workbook to CSV files...")
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=excel_file_path,
        input_type="raw",
        output_type="processed",
        file_name="business_data_csv",
        preserve_structure=True,
    )

    print(f"✓ Conversion completed!")
    print(f"  - CSV files created: {len(csv_files)}")
    print(f"  - Structure file: {structure_file}")

    # Display results
    print(f"\n📁 Generated CSV Files:")
    for sheet_name, csv_path in csv_files.items():
        print(f"  - {sheet_name}: {Path(csv_path).name}")

    return csv_files, structure_file


def demonstrate_data_modification(csv_files):
    """Demonstrate data modification on CSV files."""
    print(f"\n=== Step 2: Data Modification and Processing ===\n")

    file_utils = FileUtils()

    # Load and modify Sales data
    print("📊 Processing Sales data...")
    sales_df = file_utils.load_single_file(
        Path(csv_files["Sales"]).name, input_type="processed"
    )

    print(f"  - Original sales records: {len(sales_df)}")

    # Add new calculated fields
    sales_df["profit_margin"] = sales_df["total_amount"] * 0.15  # Assume 15% margin

    # Convert sale_date back to datetime if it was loaded as string
    if sales_df["sale_date"].dtype == "object":
        sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])

    sales_df["quarter"] = sales_df["sale_date"].dt.quarter
    sales_df["is_large_sale"] = sales_df["total_amount"] > 500

    # Add some new sales records
    new_sales = pd.DataFrame(
        {
            "sale_id": [7, 8, 9],
            "customer_name": ["Grace Corp", "Henry Ltd", "Ivy Inc"],
            "product": ["Widget B", "Widget C", "Widget A"],
            "quantity": [8, 3, 25],
            "unit_price": [45.00, 60.00, 25.50],
            "sale_date": pd.date_range("2024-02-01", periods=3, freq="W"),
            "sales_rep": ["Alice", "Bob", "John"],
            "total_amount": [360.00, 180.00, 637.50],
            "profit_margin": [54.00, 27.00, 95.63],
            "quarter": [1, 1, 1],
            "is_large_sale": [False, False, True],
        }
    )

    # Combine original and new sales
    updated_sales_df = pd.concat([sales_df, new_sales], ignore_index=True)
    print(f"  - Updated sales records: {len(updated_sales_df)}")

    # Save modified Sales data
    file_utils.save_data_to_storage(
        data=updated_sales_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="business_data_csv_Sales",  # Keep same name for reconstruction
        include_timestamp=False,  # Don't add timestamp to maintain structure
    )
    print(f"  ✓ Updated Sales CSV saved")

    # Load and modify Customers data
    print("\n👥 Processing Customers data...")
    customers_df = file_utils.load_single_file(
        Path(csv_files["Customers"]).name, input_type="processed"
    )

    # Add customer tier based on revenue
    def get_customer_tier(revenue):
        if revenue >= 10000000:
            return "Enterprise"
        elif revenue >= 5000000:
            return "Premium"
        elif revenue >= 1000000:
            return "Standard"
        else:
            return "Basic"

    customers_df["customer_tier"] = customers_df["annual_revenue"].apply(
        get_customer_tier
    )

    # Add new customers
    new_customers = pd.DataFrame(
        {
            "customer_name": ["Grace Corp", "Henry Ltd", "Ivy Inc"],
            "industry": ["Technology", "Finance", "Healthcare"],
            "company_size": ["Large", "Small", "Medium"],
            "contact_email": [
                "grace@gracecorp.com",
                "henry@henry.com",
                "ivy@ivyinc.com",
            ],
            "annual_revenue": [8000000, 1200000, 4000000],
            "customer_tier": ["Premium", "Standard", "Premium"],
        }
    )

    updated_customers_df = pd.concat([customers_df, new_customers], ignore_index=True)
    print(f"  - Updated customer records: {len(updated_customers_df)}")

    # Save modified Customers data
    file_utils.save_data_to_storage(
        data=updated_customers_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="business_data_csv_Customers",
        include_timestamp=False,
    )
    print(f"  ✓ Updated Customers CSV saved")

    # Load and modify Products data
    print("\n📦 Processing Products data...")
    products_df = file_utils.load_single_file(
        Path(csv_files["Products"]).name, input_type="processed"
    )

    # Update inventory levels
    products_df["inventory"] = products_df["inventory"] - [20, 10, 5]  # Simulate sales
    products_df["reorder_level"] = (
        products_df["inventory"] * 0.2
    )  # 20% of current inventory

    # Add new product
    new_product = pd.DataFrame(
        {
            "product": ["Widget D"],
            "category": ["Premium"],
            "cost": [35.00],
            "margin": [18.00],
            "inventory": [30],
            "supplier": ["Supplier D"],
            "reorder_level": [6.0],
        }
    )

    updated_products_df = pd.concat([products_df, new_product], ignore_index=True)
    print(f"  - Updated product records: {len(updated_products_df)}")

    # Save modified Products data
    file_utils.save_data_to_storage(
        data=updated_products_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="business_data_csv_Products",
        include_timestamp=False,
    )
    print(f"  ✓ Updated Products CSV saved")

    print(f"\n✅ Data modification completed!")
    print(f"  - Added new sales records")
    print(f"  - Enhanced customer data with tiers")
    print(f"  - Updated product inventory")
    print(f"  - Added calculated fields")


def demonstrate_csv_to_excel_reconstruction(structure_file):
    """Demonstrate CSV to Excel reconstruction."""
    print(f"\n=== Step 3: CSV to Excel Reconstruction ===\n")

    file_utils = FileUtils()

    # Reconstruct Excel workbook from modified CSV files
    print("Reconstructing Excel workbook from modified CSV files...")
    excel_path = file_utils.convert_csv_to_excel_workbook(
        structure_json_path=structure_file,
        input_type="processed",
        output_type="processed",
        file_name="business_data_reconstructed",
    )

    print(f"✓ Reconstruction completed!")
    print(f"  - Excel workbook: {Path(excel_path).name}")

    # Verify the reconstruction by loading the Excel file
    print(f"\n🔍 Verifying reconstruction...")
    reconstructed_sheets = file_utils.load_excel_sheets(
        Path(excel_path).name, input_type="processed"
    )

    print(f"  - Sheets in reconstructed workbook: {list(reconstructed_sheets.keys())}")
    for sheet_name, df in reconstructed_sheets.items():
        print(f"    - {sheet_name}: {df.shape[0]} rows × {df.shape[1]} columns")

    return excel_path


def demonstrate_workflow_comparison(original_excel, reconstructed_excel):
    """Compare original and reconstructed workbooks."""
    print(f"\n=== Step 4: Workflow Comparison ===\n")

    file_utils = FileUtils()

    # Load original workbook
    print("📊 Comparing original vs reconstructed workbooks...")
    original_sheets = file_utils.load_excel_sheets(
        Path(original_excel).name, input_type="raw"
    )

    reconstructed_sheets = file_utils.load_excel_sheets(
        Path(reconstructed_excel).name, input_type="processed"
    )

    print(f"\n📈 Data Changes Summary:")
    for sheet_name in original_sheets.keys():
        if sheet_name in reconstructed_sheets:
            orig_df = original_sheets[sheet_name]
            recon_df = reconstructed_sheets[sheet_name]

            print(f"\n  {sheet_name}:")
            print(
                f"    - Original: {orig_df.shape[0]} rows × {orig_df.shape[1]} columns"
            )
            print(
                f"    - Reconstructed: {recon_df.shape[0]} rows × {recon_df.shape[1]} columns"
            )
            print(f"    - Row difference: +{recon_df.shape[0] - orig_df.shape[0]}")
            print(f"    - Column difference: +{recon_df.shape[1] - orig_df.shape[1]}")

            # Show new columns if any
            new_columns = set(recon_df.columns) - set(orig_df.columns)
            if new_columns:
                print(f"    - New columns: {list(new_columns)}")


def demonstrate_error_handling():
    """Demonstrate error handling for missing files."""
    print(f"\n=== Step 5: Error Handling Demo ===\n")

    file_utils = FileUtils()

    # Create a structure file with missing CSV files
    print("🔧 Testing error handling with missing CSV files...")

    # Create a minimal structure file
    test_structure = {
        "workbook_info": {
            "source_file": "test_workbook.xlsx",
            "conversion_timestamp": "2024-01-01T00:00:00",
            "total_sheets": 2,
            "sheet_names": ["Existing_Sheet", "Missing_Sheet"],
        },
        "sheets": {
            "Existing_Sheet": {
                "csv_filename": "business_data_csv_Sales.csv",  # This exists
                "dimensions": {"rows": 10, "columns": 5},
            },
            "Missing_Sheet": {
                "csv_filename": "nonexistent_file.csv",  # This doesn't exist
                "dimensions": {"rows": 5, "columns": 3},
            },
        },
    }

    # Save test structure file
    test_structure_path, _ = file_utils.save_document_to_storage(
        content=test_structure,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="test_structure",
    )

    try:
        # Try to reconstruct with missing files
        excel_path = file_utils.convert_csv_to_excel_workbook(
            structure_json_path=test_structure_path,
            input_type="processed",
            output_type="processed",
            file_name="test_reconstruction",
        )

        print(f"✓ Partial reconstruction successful: {Path(excel_path).name}")
        print(f"  - Missing files were handled gracefully")

    except Exception as e:
        print(f"❌ Reconstruction failed: {e}")


def main():
    """Main demonstration function."""
    print("🔄 Complete Excel ↔ CSV Round-Trip Workflow")
    print("=" * 60)

    try:
        # Step 1: Create and convert Excel workbook
        excel_file_path = create_sample_workbook()
        csv_files, structure_file = demonstrate_excel_to_csv_conversion(excel_file_path)

        # Step 2: Modify CSV data
        demonstrate_data_modification(csv_files)

        # Step 3: Reconstruct Excel workbook
        reconstructed_excel = demonstrate_csv_to_excel_reconstruction(structure_file)

        # Step 4: Compare workflows
        demonstrate_workflow_comparison(excel_file_path, reconstructed_excel)

        # Step 5: Error handling
        demonstrate_error_handling()

        print(f"\n🎉 Complete round-trip workflow demonstration finished!")
        print(f"\nKey Benefits:")
        print(f"  ✓ Excel → CSV conversion preserves structure")
        print(f"  ✓ Individual CSV files enable easy data processing")
        print(f"  ✓ CSV → Excel reconstruction maintains workbook format")
        print(f"  ✓ Metadata tracking throughout the workflow")
        print(f"  ✓ Graceful handling of missing or modified files")
        print(f"  ✓ Perfect for data processing pipelines")

        print(f"\nUse Cases:")
        print(f"  📊 Data analysis workflows")
        print(f"  🔄 ETL pipelines")
        print(f"  📈 Report generation")
        print(f"  🤝 Collaborative data processing")
        print(f"  📋 Data distribution and sharing")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
