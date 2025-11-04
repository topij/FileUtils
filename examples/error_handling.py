"""Example: Error Handling and Recovery

This script demonstrates robust error handling and recovery strategies
when using FileUtils in production environments.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import time
import random
from FileUtils import FileUtils, OutputFileType
from FileUtils.core.base import StorageError, StorageOperationError


def simulate_unreliable_data_source():
    """Simulate a data source that might fail or return incomplete data."""
    # Simulate various failure scenarios
    failure_type = random.choice(
        ["success", "incomplete", "corrupted", "timeout", "success"]
    )

    if failure_type == "success":
        # Generate normal data
        data = pd.DataFrame(
            {
                "id": range(1, 101),
                "value": np.random.normal(100, 20, 100),
                "category": np.random.choice(["A", "B", "C"], 100),
                "timestamp": datetime.now(),
            }
        )
        return data, None

    elif failure_type == "incomplete":
        # Return incomplete data
        data = pd.DataFrame(
            {
                "id": range(1, 51),  # Only half the data
                "value": np.random.normal(100, 20, 50),
                "category": np.random.choice(["A", "B", "C"], 50),
                "timestamp": datetime.now(),
            }
        )
        return data, "Incomplete data received"

    elif failure_type == "corrupted":
        # Return corrupted data
        data = pd.DataFrame(
            {
                "id": range(1, 101),
                "value": [None] * 50
                + list(np.random.normal(100, 20, 50)),  # Half missing
                "category": ["INVALID"] * 30
                + list(np.random.choice(["A", "B", "C"], 70)),
                "timestamp": datetime.now(),
            }
        )
        return data, "Data corruption detected"

    elif failure_type == "timeout":
        # Simulate timeout
        time.sleep(2)  # Simulate slow response
        return None, "Data source timeout"

    else:
        # Simulate complete failure
        return None, "Data source unavailable"


def robust_data_processing():
    """Demonstrate robust data processing with error handling."""
    print("=== Error Handling and Recovery Demo ===\n")

    # Initialize FileUtils
    file_utils = FileUtils()

    # Step 1: Data collection with retry logic
    print("1. Collecting data with retry logic...")

    max_retries = 3
    retry_delay = 1
    data = None
    error_log = []

    for attempt in range(max_retries):
        try:
            print(f"   Attempt {attempt + 1}/{max_retries}...")
            data, warning = simulate_unreliable_data_source()

            if data is not None:
                print(f"   ✓ Data collected successfully ({len(data)} records)")
                if warning:
                    print(f"   ⚠ Warning: {warning}")
                    error_log.append(f"Attempt {attempt + 1}: {warning}")
                break
            else:
                raise Exception("Data collection failed")

        except Exception as e:
            error_msg = f"Attempt {attempt + 1} failed: {str(e)}"
            print(f"   ✗ {error_msg}")
            error_log.append(error_msg)

            if attempt < max_retries - 1:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print("   All retry attempts failed")
                # Create fallback data
                data = pd.DataFrame(
                    {
                        "id": range(1, 11),
                        "value": [0] * 10,
                        "category": ["FALLBACK"] * 10,
                        "timestamp": datetime.now(),
                    }
                )
                print("   ✓ Using fallback data")

    # Step 2: Data validation and cleaning
    print("\n2. Validating and cleaning data...")

    try:
        # Data quality checks
        original_count = len(data)

        # Remove rows with missing values
        data_cleaned = data.dropna()
        missing_count = original_count - len(data_cleaned)

        # Remove invalid categories
        valid_categories = ["A", "B", "C"]
        data_cleaned = data_cleaned[data_cleaned["category"].isin(valid_categories)]
        invalid_count = len(data_cleaned) - len(
            data_cleaned[data_cleaned["category"].isin(valid_categories)]
        )

        # Remove extreme outliers (values > 3 standard deviations)
        if len(data_cleaned) > 0:
            mean_val = data_cleaned["value"].mean()
            std_val = data_cleaned["value"].std()
            if std_val > 0:
                data_cleaned = data_cleaned[
                    abs(data_cleaned["value"] - mean_val) <= 3 * std_val
                ]

        print(f"   ✓ Data validation complete")
        print(f"   - Original records: {original_count}")
        print(f"   - Missing values removed: {missing_count}")
        print(f"   - Invalid categories removed: {invalid_count}")
        print(f"   - Final records: {len(data_cleaned)}")

        if len(data_cleaned) == 0:
            raise ValueError("No valid data remaining after cleaning")

        data = data_cleaned

    except Exception as e:
        print(f"   ✗ Data validation failed: {e}")
        error_log.append(f"Data validation failed: {str(e)}")
        raise

    # Step 3: Safe data saving with error handling
    print("\n3. Saving data with error handling...")

    try:
        # Try to save as primary format (Parquet)
        saved_files, metadata = file_utils.save_data_to_storage(
            data=data,
            output_filetype=OutputFileType.PARQUET,
            output_type="processed",
            file_name="robust_data",
            include_timestamp=True,
        )
        print(f"   ✓ Data saved as Parquet: {list(saved_files.values())[0]}")
        primary_format = "parquet"

    except Exception as e:
        print(f"   ✗ Parquet save failed: {e}")
        error_log.append(f"Parquet save failed: {str(e)}")

        try:
            # Fallback to CSV
            saved_files, metadata = file_utils.save_data_to_storage(
                data=data,
                output_filetype=OutputFileType.CSV,
                output_type="processed",
                file_name="robust_data",
                include_timestamp=True,
            )
            print(f"   ✓ Data saved as CSV (fallback): {list(saved_files.values())[0]}")
            primary_format = "csv"

        except Exception as e2:
            print(f"   ✗ CSV save also failed: {e2}")
            error_log.append(f"CSV save failed: {str(e2)}")
            raise StorageError(f"All save attempts failed: {e}, {e2}")

    # Step 4: Generate error report
    print("\n4. Generating error report...")

    error_report = {
        "frontmatter": {
            "title": "Data Processing Error Report",
            "generated_date": datetime.now().isoformat(),
            "processing_status": (
                "completed_with_issues" if error_log else "completed_successfully"
            ),
            "total_errors": len(error_log),
        },
        "body": f"""# Data Processing Error Report

## Processing Summary

- **Status**: {'Completed with issues' if error_log else 'Completed successfully'}
- **Data Records Processed**: {len(data)}
- **Primary Format**: {primary_format}
- **Total Errors/Warnings**: {len(error_log)}

## Error Log

{chr(10).join([f"- {error}" for error in error_log]) if error_log else "No errors encountered"}

## Data Quality Metrics

- **Original Records**: {original_count}
- **Final Records**: {len(data)}
- **Data Retention Rate**: {len(data)/original_count*100:.1f}%
- **Processing Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Recommendations

{chr(10).join([
    "1. **Data Source Monitoring**: Implement monitoring for data source reliability",
    "2. **Retry Logic**: Current retry logic handled failures appropriately",
    "3. **Data Validation**: Validation rules successfully cleaned data",
    "4. **Fallback Strategies**: Fallback formats ensured data persistence",
    "5. **Error Logging**: Comprehensive error logging for debugging"
])}

## Technical Details

- **FileUtils Version**: Latest
- **Error Handling**: Robust with multiple fallback strategies
- **Data Formats**: Primary {primary_format}, fallback CSV
- **Recovery Mechanisms**: Automatic retry, format fallback, data cleaning
""",
    }

    # Save error report
    try:
        saved_path, _ = file_utils.save_document_to_storage(
            content=error_report,
            output_filetype=OutputFileType.MARKDOWN,
            output_type="processed",
            file_name="error_report",
            sub_path="reports",
            include_timestamp=True,
        )
        print(f"   ✓ Error report saved: {saved_path}")

    except Exception as e:
        print(f"   ✗ Error report save failed: {e}")
        # Even if report save fails, we continue

    # Step 5: Create recovery configuration
    print("\n5. Creating recovery configuration...")

    recovery_config = {
        "error_handling": {
            "max_retries": max_retries,
            "retry_delay": 1,
            "exponential_backoff": True,
            "fallback_formats": ["parquet", "csv", "json"],
            "data_validation": {
                "remove_missing": True,
                "validate_categories": True,
                "outlier_threshold": 3.0,
            },
        },
        "monitoring": {
            "error_logging": True,
            "performance_tracking": True,
            "data_quality_metrics": True,
            "alert_thresholds": {
                "data_loss_percentage": 10.0,
                "processing_time_seconds": 30.0,
                "error_rate_percentage": 5.0,
            },
        },
        "recovery_strategies": {
            "data_source_failure": "retry_with_backoff",
            "format_failure": "fallback_format",
            "validation_failure": "clean_and_continue",
            "storage_failure": "retry_with_different_path",
        },
        "file_utils_integration": {
            "storage_backend": "local",
            "error_reporting": True,
            "metadata_tracking": True,
            "timestamp_format": "%Y%m%d_%H%M%S",
        },
    }

    # Save recovery configuration
    try:
        saved_path, _ = file_utils.save_document_to_storage(
            content=recovery_config,
            output_filetype=OutputFileType.YAML,
            output_type="processed",
            file_name="recovery_config",
            sub_path="config",
            include_timestamp=True,
        )
        print(f"   ✓ Recovery configuration saved: {saved_path}")

    except Exception as e:
        print(f"   ✗ Recovery configuration save failed: {e}")

    # Step 6: Generate success summary
    print("\n6. Processing summary...")

    summary = {
        "processing_status": "completed",
        "data_processed": len(data),
        "errors_encountered": len(error_log),
        "primary_format": primary_format,
        "error_handling": "successful",
        "recovery_mechanisms": "activated" if error_log else "not_needed",
        "timestamp": datetime.now().isoformat(),
    }

    print("\n=== Error Handling Demo Complete ===")
    print(f"✓ Processed {len(data)} records")
    print(f"✓ Encountered {len(error_log)} errors/warnings")
    print(f"✓ Used {primary_format} format")
    print(f"✓ Error handling: {'Successful' if error_log else 'Not needed'}")
    print(f"✓ Recovery mechanisms: {'Activated' if error_log else 'Not needed'}")

    return {
        "data_file": list(saved_files.values())[0],
        "error_report": saved_path if "saved_path" in locals() else None,
        "recovery_config": saved_path if "saved_path" in locals() else None,
        "summary": summary,
        "error_log": error_log,
    }


if __name__ == "__main__":
    results = robust_data_processing()
    print(f"\nProcessing results: {results}")
