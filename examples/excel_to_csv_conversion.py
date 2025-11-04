"""Example: Excel to CSV Conversion with Workbook Structure

This script demonstrates the new Excel to CSV conversion functionality that
maintains workbook structure in a JSON file. This is particularly useful for
data pipelines that need to convert Excel workbooks to CSV format while
preserving metadata about the original workbook structure.

Features demonstrated:
- Convert Excel workbook with multiple sheets to individual CSV files
- Create structure JSON with sheet metadata and relationships
- Handle different Excel file configurations
- Load and inspect the converted data
"""

import json
import sys
from pathlib import Path

import pandas as pd

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)  # Insert at beginning to prioritize

from FileUtils import FileUtils, OutputFileType


def create_sample_excel_workbook():
    """Create a sample Excel workbook with multiple sheets for demonstration."""
    print("=== Creating Sample Excel Workbook ===\n")

    file_utils = FileUtils()

    # Create sample data for different sheets
    # Sheet 1: Employee data
    employees_df = pd.DataFrame(
        {
            "employee_id": [1, 2, 3, 4, 5],
            "name": [
                "Alice Johnson",
                "Bob Smith",
                "Charlie Brown",
                "Diana Prince",
                "Eve Wilson",
            ],
            "department": ["Engineering", "Marketing", "Engineering", "HR", "Finance"],
            "salary": [75000, 65000, 80000, 60000, 70000],
            "hire_date": pd.date_range("2020-01-01", periods=5, freq="M"),
        }
    )

    # Sheet 2: Department summary
    departments_df = pd.DataFrame(
        {
            "department": ["Engineering", "Marketing", "HR", "Finance"],
            "head_count": [2, 1, 1, 1],
            "avg_salary": [77500, 65000, 60000, 70000],
            "budget": [200000, 100000, 80000, 120000],
        }
    )

    # Sheet 3: Project assignments
    projects_df = pd.DataFrame(
        {
            "project_id": ["P001", "P002", "P003"],
            "project_name": ["Website Redesign", "Mobile App", "Data Migration"],
            "lead_employee_id": [1, 2, 3],
            "status": ["In Progress", "Planning", "Completed"],
            "start_date": pd.date_range("2024-01-01", periods=3, freq="M"),
        }
    )

    # Combine all sheets
    workbook_data = {
        "Employees": employees_df,
        "Departments": departments_df,
        "Projects": projects_df,
    }

    # Save as Excel workbook
    saved_files, metadata = file_utils.save_data_to_storage(
        data=workbook_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="sample_workbook",
    )

    excel_file_path = list(saved_files.values())[0]
    print(f"✓ Created sample Excel workbook: {excel_file_path}")
    print(f"  - Sheets: {list(workbook_data.keys())}")
    print(f"  - Total records: {sum(len(df) for df in workbook_data.values())}")

    return excel_file_path


def demonstrate_excel_to_csv_conversion():
    """Demonstrate Excel to CSV conversion with structure preservation."""
    print("\n=== Excel to CSV Conversion Demo ===\n")

    file_utils = FileUtils()

    # First, create a sample Excel workbook
    excel_file_path = create_sample_excel_workbook()

    # Convert Excel to CSV with structure preservation
    print("Converting Excel workbook to CSV files...")
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=excel_file_path,
        input_type="raw",
        output_type="processed",
        file_name="converted_workbook",
        preserve_structure=True,
    )

    print(f"\n✓ Conversion completed!")
    print(f"  - CSV files created: {len(csv_files)}")
    print(f"  - Structure file: {structure_file}")

    # Display results
    print(f"\n📁 Generated Files:")
    for sheet_name, csv_path in csv_files.items():
        print(f"  - {sheet_name}: {csv_path}")
    print(f"  - Structure: {structure_file}")

    return csv_files, structure_file, excel_file_path


def inspect_structure_file(structure_file_path):
    """Inspect and display the structure JSON file contents."""
    print(f"\n=== Structure File Analysis ===")
    print(f"File: {structure_file_path}\n")

    # Load and display structure information
    with open(structure_file_path, "r") as f:
        structure_data = json.load(f)

    # Workbook info
    workbook_info = structure_data["workbook_info"]
    print(f"📊 Workbook Information:")
    print(f"  - Source file: {workbook_info['source_file']}")
    print(f"  - Conversion time: {workbook_info['conversion_timestamp']}")
    print(f"  - Total sheets: {workbook_info['total_sheets']}")
    print(f"  - Sheet names: {workbook_info['sheet_names']}")

    # Sheet details
    print(f"\n📋 Sheet Details:")
    for sheet_name, sheet_info in structure_data["sheets"].items():
        print(f"\n  {sheet_name}:")
        print(f"    - CSV file: {sheet_info['csv_filename']}")
        print(
            f"    - Dimensions: {sheet_info['dimensions']['rows']} rows × {sheet_info['dimensions']['columns']} columns"
        )
        print(f"    - Columns: {sheet_info['columns']['names']}")
        print(f"    - Data types: {sheet_info['columns']['dtypes']}")
        print(f"    - Memory usage: {sheet_info['data_info']['memory_usage']:,} bytes")
        print(
            f"    - Null values: {sum(sheet_info['data_info']['null_counts'].values())} total"
        )


def demonstrate_csv_loading(csv_files):
    """Demonstrate loading the converted CSV files."""
    print(f"\n=== Loading Converted CSV Files ===")

    file_utils = FileUtils()

    for sheet_name, csv_path in csv_files.items():
        print(f"\n📄 Loading {sheet_name}:")

        # Load the CSV file
        df = file_utils.load_single_file(
            Path(csv_path).name, input_type="processed"  # Just the filename
        )

        print(f"  - Shape: {df.shape}")
        print(f"  - Columns: {list(df.columns)}")
        print(f"  - First few rows:")
        print(df.head(2).to_string(index=False))
        print("  " + "-" * 50)


def demonstrate_advanced_features():
    """Demonstrate advanced features of the conversion."""
    print(f"\n=== Advanced Features Demo ===")

    file_utils = FileUtils()

    # Create another sample workbook with different characteristics
    print("Creating workbook with special characteristics...")

    # Sheet with missing values and different data types
    special_df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "name": ["Item A", "Item B", None, "Item D"],
            "price": [10.50, None, 25.00, 15.75],
            "category": ["A", "B", "A", "C"],
            "active": [True, False, True, True],
        }
    )

    # Sheet with datetime and complex data
    datetime_df = pd.DataFrame(
        {
            "event_id": [1, 2, 3],
            "event_name": ["Meeting", "Conference", "Workshop"],
            "start_time": pd.date_range("2024-01-01", periods=3, freq="D"),
            "duration_hours": [1.5, 8.0, 4.0],
            "attendees": [[10, 20, 30], [50, 60, 70], [15, 25, 35]],  # List data
        }
    )

    advanced_workbook = {"Special_Data": special_df, "Events": datetime_df}

    # Save advanced workbook
    saved_files, _ = file_utils.save_data_to_storage(
        data=advanced_workbook,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="advanced_workbook",
    )

    excel_file_path = list(saved_files.values())[0]

    # Convert with custom options
    print("Converting with custom CSV options...")
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=excel_file_path,
        input_type="raw",
        output_type="processed",
        file_name="advanced_converted",
        preserve_structure=True,
        encoding="utf-8",
        sep=",",  # Custom delimiter
    )

    print(f"✓ Advanced conversion completed!")
    print(f"  - Files: {list(csv_files.keys())}")

    # Show how the structure file handles special data
    print(f"\n🔍 Special Data Handling:")
    with open(structure_file, "r") as f:
        structure_data = json.load(f)

    special_sheet = structure_data["sheets"]["Special_Data"]
    print(f"  - Null handling: {special_sheet['data_info']['null_counts']}")
    print(f"  - Data types preserved: {special_sheet['columns']['dtypes']}")


def demonstrate_workflow_integration(excel_file_path):
    """Demonstrate how this fits into a typical data workflow."""
    print(f"\n=== Workflow Integration Example ===")

    file_utils = FileUtils()

    # Simulate a typical data pipeline
    print("🔄 Simulating data pipeline workflow...")

    # Step 1: Convert Excel to CSV
    print("1. Converting Excel workbook to CSV format...")
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path,  # Use the actual file path from earlier
        input_type="raw",
        output_type="processed",
        file_name="pipeline_data",
    )

    # Step 2: Load and process data
    print("2. Loading and processing converted data...")
    employees_df = file_utils.load_single_file(
        Path(csv_files["Employees"]).name, input_type="processed"
    )

    # Step 3: Perform analysis
    print("3. Performing analysis...")
    dept_summary = (
        employees_df.groupby("department")
        .agg({"salary": ["mean", "count"], "employee_id": "count"})
        .round(2)
    )

    print("   Department Summary:")
    print(dept_summary.to_string())

    # Step 4: Save results
    print("4. Saving analysis results...")
    file_utils.save_data_to_storage(
        data=dept_summary,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="department_analysis",
    )

    print("✓ Pipeline workflow completed!")


def main():
    """Main demonstration function."""
    print("🚀 Excel to CSV Conversion with Structure Preservation")
    print("=" * 60)

    try:
        # Basic conversion demo
        csv_files, structure_file, excel_file_path = (
            demonstrate_excel_to_csv_conversion()
        )

        # Inspect structure file
        inspect_structure_file(structure_file)

        # Demonstrate CSV loading
        demonstrate_csv_loading(csv_files)

        # Advanced features
        demonstrate_advanced_features()

        # Workflow integration
        demonstrate_workflow_integration(excel_file_path)

        print(f"\n🎉 All demonstrations completed successfully!")
        print(f"\nKey Benefits:")
        print(f"  ✓ Preserves Excel workbook structure in JSON")
        print(f"  ✓ Maintains sheet relationships and metadata")
        print(f"  ✓ Enables easy CSV-based data processing")
        print(f"  ✓ Provides detailed data quality information")
        print(f"  ✓ Integrates seamlessly with FileUtils workflow")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        raise


if __name__ == "__main__":
    main()
