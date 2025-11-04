"""Example: Data Pipeline with FileUtils

This script demonstrates how to use FileUtils in a typical data science pipeline,
including data processing, analysis, and report generation.
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
from datetime import datetime, timedelta
from FileUtils import FileUtils, OutputFileType


def generate_sample_data():
    """Generate sample sales data for the pipeline."""
    np.random.seed(42)

    # Generate sales data
    dates = pd.date_range("2024-01-01", periods=365, freq="D")
    products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    regions = ["North", "South", "East", "West"]

    data = []
    for date in dates:
        for product in products:
            for region in regions:
                # Generate realistic sales data
                base_sales = np.random.normal(100, 30)
                seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
                weekend_factor = 0.7 if date.weekday() >= 5 else 1.0

                sales = max(0, base_sales * seasonal_factor * weekend_factor)

                data.append(
                    {
                        "date": date,
                        "product": product,
                        "region": region,
                        "sales": round(sales, 2),
                        "units": max(1, int(sales / 10)),
                        "price": round(np.random.uniform(20, 100), 2),
                    }
                )

    return pd.DataFrame(data)


def run_data_pipeline():
    """Run a complete data pipeline using FileUtils."""
    print("=== Data Pipeline with FileUtils ===\n")

    # Initialize FileUtils
    file_utils = FileUtils()

    # Step 1: Generate and save raw data
    print("1. Generating and saving raw data...")
    raw_data = generate_sample_data()

    saved_files, metadata = file_utils.save_data_to_storage(
        data=raw_data,
        output_filetype=OutputFileType.PARQUET,
        output_type="raw",
        file_name="sales_data_2024",
        include_timestamp=True,
    )
    print(f"✓ Raw data saved: {list(saved_files.values())[0]}")

    # Step 2: Data processing and cleaning
    print("\n2. Processing and cleaning data...")

    # Load raw data
    processed_data = file_utils.load_single_file(
        file_path="sales_data_2024.parquet", input_type="raw"
    )

    # Data cleaning and feature engineering
    processed_data["revenue"] = processed_data["sales"] * processed_data["units"]
    processed_data["month"] = processed_data["date"].dt.month
    processed_data["quarter"] = processed_data["date"].dt.quarter
    processed_data["day_of_week"] = processed_data["date"].dt.day_name()

    # Remove outliers (sales > 3 standard deviations)
    sales_mean = processed_data["sales"].mean()
    sales_std = processed_data["sales"].std()
    processed_data = processed_data[
        processed_data["sales"] <= sales_mean + 3 * sales_std
    ]

    # Save processed data
    saved_files, _ = file_utils.save_data_to_storage(
        data=processed_data,
        output_filetype=OutputFileType.PARQUET,
        output_type="processed",
        file_name="sales_data_cleaned",
        include_timestamp=True,
    )
    print(f"✓ Processed data saved: {list(saved_files.values())[0]}")

    # Step 3: Generate analysis and reports
    print("\n3. Generating analysis and reports...")

    # Load processed data
    analysis_data = file_utils.load_single_file(
        file_path="sales_data_cleaned.parquet", input_type="processed"
    )

    # Create multiple analysis sheets
    analysis_sheets = {}

    # Summary statistics
    summary_stats = (
        analysis_data.groupby("product")
        .agg(
            {
                "sales": ["mean", "std", "min", "max", "count"],
                "revenue": ["sum", "mean"],
                "units": "sum",
            }
        )
        .round(2)
    )

    # Flatten MultiIndex columns
    summary_stats.columns = ["_".join(col).strip() for col in summary_stats.columns]
    analysis_sheets["summary_stats"] = summary_stats.reset_index()

    # Monthly trends
    monthly_trends = (
        analysis_data.groupby(["month", "product"])
        .agg({"sales": "mean", "revenue": "sum", "units": "sum"})
        .reset_index()
    )
    analysis_sheets["monthly_trends"] = monthly_trends

    # Regional performance
    regional_performance = (
        analysis_data.groupby("region")
        .agg({"sales": "mean", "revenue": "sum", "units": "sum"})
        .reset_index()
    )
    analysis_sheets["regional_performance"] = regional_performance

    # Top products by revenue
    top_products = (
        analysis_data.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    analysis_sheets["top_products"] = top_products.reset_index()

    # Save analysis results
    saved_files, analysis_metadata = file_utils.save_with_metadata(
        data=analysis_sheets,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="sales_analysis_report",
        include_timestamp=True,
    )
    print(f"✓ Analysis report saved: {list(saved_files.values())[0]}")
    print(f"✓ Metadata saved: {analysis_metadata}")

    # Step 4: Generate insights document
    print("\n4. Generating insights document...")

    # Calculate key metrics
    total_revenue = analysis_data["revenue"].sum()
    avg_daily_sales = analysis_data.groupby("date")["sales"].sum().mean()
    best_product = analysis_data.groupby("product")["revenue"].sum().idxmax()
    best_region = analysis_data.groupby("region")["revenue"].sum().idxmax()

    # Create insights document
    insights_doc = {
        "frontmatter": {
            "title": "Sales Analysis Insights",
            "generated_date": datetime.now().isoformat(),
            "data_period": "2024",
            "total_records": len(analysis_data),
        },
        "body": f"""# Sales Analysis Insights

## Executive Summary

This analysis covers sales data for 2024, including {len(analysis_data):,} individual sales records across 5 products and 4 regions.

## Key Metrics

- **Total Revenue**: ${total_revenue:,.2f}
- **Average Daily Sales**: ${avg_daily_sales:,.2f}
- **Best Performing Product**: {best_product}
- **Best Performing Region**: {best_region}

## Product Performance

The top 3 products by revenue are:
1. {analysis_data.groupby('product')['revenue'].sum().sort_values(ascending=False).index[0]}
2. {analysis_data.groupby('product')['revenue'].sum().sort_values(ascending=False).index[1]}
3. {analysis_data.groupby('product')['revenue'].sum().sort_values(ascending=False).index[2]}

## Regional Analysis

Regional performance shows:
- **North**: ${analysis_data[analysis_data['region'] == 'North']['revenue'].sum():,.2f}
- **South**: ${analysis_data[analysis_data['region'] == 'South']['revenue'].sum():,.2f}
- **East**: ${analysis_data[analysis_data['region'] == 'East']['revenue'].sum():,.2f}
- **West**: ${analysis_data[analysis_data['region'] == 'West']['revenue'].sum():,.2f}

## Recommendations

1. **Focus on Top Products**: Invest more in marketing for the top-performing products
2. **Regional Strategy**: Develop region-specific strategies based on performance
3. **Seasonal Planning**: Consider seasonal trends for inventory management
4. **Data Quality**: Continue monitoring for outliers and data quality issues

## Technical Notes

- Data processed using FileUtils pipeline
- Analysis includes {len(analysis_sheets)} different views
- All calculations performed on cleaned dataset
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""",
    }

    # Save insights document
    saved_path, _ = file_utils.save_document_to_storage(
        content=insights_doc,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="sales_insights",
        sub_path="reports",
        include_timestamp=True,
    )
    print(f"✓ Insights document saved: {saved_path}")

    # Step 5: Create configuration summary
    print("\n5. Creating configuration summary...")

    config_summary = {
        "pipeline_info": {
            "name": "Sales Data Pipeline",
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "description": "End-to-end sales data processing pipeline",
        },
        "data_sources": {
            "raw_data": "sales_data_2024.parquet",
            "processed_data": "sales_data_cleaned.parquet",
        },
        "outputs": {
            "analysis_report": "sales_analysis_report.xlsx",
            "insights_document": "sales_insights.md",
            "metadata_file": analysis_metadata,
        },
        "metrics": {
            "total_records": len(analysis_data),
            "total_revenue": float(total_revenue),
            "products_analyzed": analysis_data["product"].nunique(),
            "regions_analyzed": analysis_data["region"].nunique(),
        },
        "file_utils_config": {
            "project_root": str(file_utils.project_root),
            "storage_type": "local",
            "timestamp_enabled": True,
            "directory_structure": file_utils.config.get("directory_structure", {}),
        },
    }

    # Save configuration summary
    saved_path, _ = file_utils.save_document_to_storage(
        content=config_summary,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="pipeline_config",
        sub_path="config",
        include_timestamp=True,
    )
    print(f"✓ Configuration summary saved: {saved_path}")

    print("\n=== Pipeline Complete ===")
    print(f"✓ Processed {len(analysis_data):,} records")
    print(f"✓ Generated {len(analysis_sheets)} analysis sheets")
    print(f"✓ Created insights document")
    print(f"✓ Saved configuration summary")

    return {
        "raw_data_path": list(saved_files.values())[0],
        "analysis_report": list(saved_files.values())[0],
        "insights_document": saved_path,
        "config_summary": saved_path,
        "metadata": analysis_metadata,
    }


if __name__ == "__main__":
    results = run_data_pipeline()
    print(f"\nPipeline results: {results}")
