"""Example: Multi-Format Report Generation

This script demonstrates how to use FileUtils to generate reports in multiple formats
from the same data, including Excel, PDF, Markdown, and JSON outputs.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from FileUtils import FileUtils, OutputFileType


def generate_report_data():
    """Generate sample data for multi-format report generation."""
    np.random.seed(42)

    # Generate quarterly sales data
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    products = ["Product A", "Product B", "Product C", "Product D"]
    regions = ["North", "South", "East", "West"]

    data = []
    for quarter in quarters:
        for product in products:
            for region in regions:
                # Generate realistic quarterly data
                base_sales = np.random.normal(1000, 200)
                seasonal_factor = 1 + 0.2 * np.sin(
                    2 * np.pi * (quarters.index(quarter) + 1) / 4
                )

                sales = max(0, base_sales * seasonal_factor)
                units = max(1, int(sales / 50))
                revenue = sales * units

                data.append(
                    {
                        "quarter": quarter,
                        "product": product,
                        "region": region,
                        "sales": round(sales, 2),
                        "units": units,
                        "revenue": round(revenue, 2),
                        "margin": round(np.random.uniform(0.15, 0.35), 3),
                    }
                )

    return pd.DataFrame(data)


def run_multi_format_reports():
    """Generate reports in multiple formats using FileUtils."""
    print("=== Multi-Format Report Generation ===\n")

    # Initialize FileUtils
    file_utils = FileUtils()

    # Step 1: Generate and prepare data
    print("1. Generating and preparing report data...")
    report_data = generate_report_data()

    # Create multiple analysis views
    analysis_views = {}

    # Overall summary
    summary = (
        report_data.groupby("quarter")
        .agg({"sales": "sum", "units": "sum", "revenue": "sum", "margin": "mean"})
        .round(2)
    )
    analysis_views["quarterly_summary"] = summary.reset_index()

    # Product performance
    product_performance = (
        report_data.groupby("product")
        .agg({"sales": "sum", "units": "sum", "revenue": "sum", "margin": "mean"})
        .round(2)
    )
    analysis_views["product_performance"] = product_performance.reset_index()

    # Regional analysis
    regional_analysis = (
        report_data.groupby("region")
        .agg({"sales": "sum", "units": "sum", "revenue": "sum", "margin": "mean"})
        .round(2)
    )
    analysis_views["regional_analysis"] = regional_analysis.reset_index()

    # Detailed breakdown
    analysis_views["detailed_breakdown"] = report_data.copy()

    # Save Excel report
    print("\n2. Generating Excel report...")
    saved_files, metadata = file_utils.save_with_metadata(
        data=analysis_views,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="quarterly_report",
        sub_path="reports/excel",
        include_timestamp=True,
    )
    print(f"✓ Excel report saved: {list(saved_files.values())[0]}")

    # Step 3: Generate Markdown report
    print("\n3. Generating Markdown report...")

    # Calculate key metrics
    total_revenue = report_data["revenue"].sum()
    avg_margin = report_data["margin"].mean()
    best_product = product_performance["revenue"].idxmax()
    best_region = regional_analysis["revenue"].idxmax()

    markdown_report = {
        "frontmatter": {
            "title": "Quarterly Sales Report",
            "period": "2024 Q1-Q4",
            "generated_date": datetime.now().isoformat(),
            "report_type": "comprehensive",
            "tags": ["sales", "quarterly", "analysis", "performance"],
        },
        "body": f"""# Quarterly Sales Report

## Executive Summary

This report provides a comprehensive analysis of quarterly sales performance across all products and regions.

### Key Metrics
- **Total Revenue**: ${total_revenue:,.2f}
- **Average Margin**: {avg_margin:.1%}
- **Best Performing Product**: {best_product}
- **Best Performing Region**: {best_region}

## Quarterly Performance

### Revenue by Quarter
{chr(10).join([f"- **{row['quarter']}**: ${row['revenue']:,.2f}" for _, row in summary.iterrows()])}

### Sales Trends
{chr(10).join([f"- **{row['quarter']}**: {row['sales']:,.0f} units sold" for _, row in summary.iterrows()])}

## Product Analysis

### Top Products by Revenue
{chr(10).join([f"{i+1}. **{row['product']}**: ${row['revenue']:,.2f} ({row['margin']:.1%} margin)" for i, (_, row) in enumerate(product_performance.sort_values('revenue', ascending=False).head(3).iterrows())])}

### Product Performance Summary
| Product | Revenue | Units | Margin |
|---------|---------|-------|--------|
{chr(10).join([f"| {row['product']} | ${row['revenue']:,.2f} | {row['units']:,} | {row['margin']:.1%} |" for _, row in product_performance.iterrows()])}

## Regional Analysis

### Regional Performance
{chr(10).join([f"- **{row['region']}**: ${row['revenue']:,.2f} revenue" for _, row in regional_analysis.sort_values('revenue', ascending=False).iterrows()])}

### Regional Margins
{chr(10).join([f"- **{row['region']}**: {row['margin']:.1%} average margin" for _, row in regional_analysis.sort_values('margin', ascending=False).iterrows()])}

## Insights and Recommendations

### Key Findings
1. **Revenue Growth**: Strong performance across all quarters
2. **Product Mix**: {best_product} leads in revenue generation
3. **Regional Performance**: {best_region} shows highest revenue
4. **Margin Analysis**: Average margin of {avg_margin:.1%} indicates healthy profitability

### Strategic Recommendations
1. **Product Focus**: Increase investment in {best_product} marketing
2. **Regional Strategy**: Leverage {best_region} success model in other regions
3. **Margin Optimization**: Focus on products with margins above {avg_margin:.1%}
4. **Quarterly Planning**: Use quarterly trends for inventory management

## Technical Notes

- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Data Points**: {len(report_data)} individual records
- **Analysis Period**: Q1-Q4 2024
- **Generated By**: FileUtils Multi-Format Report Generator
""",
    }

    # Save Markdown report
    saved_path, _ = file_utils.save_document_to_storage(
        content=markdown_report,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="quarterly_report",
        sub_path="reports/markdown",
        include_timestamp=True,
    )
    print(f"✓ Markdown report saved: {saved_path}")

    # Step 4: Generate JSON API response
    print("\n4. Generating JSON API response...")

    api_response = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "report_id": f"quarterly_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "data": {
            "summary": {
                "total_revenue": float(total_revenue),
                "average_margin": float(avg_margin),
                "total_records": len(report_data),
                "quarters_analyzed": len(quarters),
            },
            "quarterly_performance": summary.to_dict("records"),
            "product_performance": product_performance.to_dict("records"),
            "regional_analysis": regional_analysis.to_dict("records"),
            "top_performers": {
                "best_product": best_product,
                "best_region": best_region,
                "highest_revenue": float(product_performance["revenue"].max()),
                "highest_margin": float(product_performance["margin"].max()),
            },
        },
        "metadata": {
            "generated_by": "FileUtils Multi-Format Generator",
            "report_type": "quarterly_sales",
            "formats_available": ["excel", "markdown", "json", "pdf"],
            "data_quality": "excellent",
        },
    }

    # Save JSON API response
    saved_path, _ = file_utils.save_document_to_storage(
        content=api_response,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="quarterly_report_api",
        sub_path="reports/json",
        include_timestamp=True,
    )
    print(f"✓ JSON API response saved: {saved_path}")

    # Step 5: Generate PDF report
    print("\n5. Generating PDF report...")

    # Create PDF content
    pdf_content = f"""QUARTERLY SALES REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

EXECUTIVE SUMMARY
Total Revenue: ${total_revenue:,.2f}
Average Margin: {avg_margin:.1%}
Best Product: {best_product}
Best Region: {best_region}

QUARTERLY PERFORMANCE
{chr(10).join([f"{row['quarter']}: ${row['revenue']:,.2f} revenue, {row['sales']:,.0f} units" for _, row in summary.iterrows()])}

TOP PRODUCTS
{chr(10).join([f"{i+1}. {row['product']}: ${row['revenue']:,.2f} ({row['margin']:.1%} margin)" for i, (_, row) in enumerate(product_performance.sort_values('revenue', ascending=False).head(5).iterrows())])}

REGIONAL ANALYSIS
{chr(10).join([f"{row['region']}: ${row['revenue']:,.2f} revenue, {row['margin']:.1%} margin" for _, row in regional_analysis.sort_values('revenue', ascending=False).iterrows()])}

RECOMMENDATIONS
1. Focus on {best_product} for maximum revenue impact
2. Leverage {best_region} success model
3. Optimize margins for products below {avg_margin:.1%}
4. Use quarterly trends for planning

This report was generated using FileUtils Multi-Format Report Generator.
"""

    # Save PDF report
    saved_path, _ = file_utils.save_document_to_storage(
        content=pdf_content,
        output_filetype=OutputFileType.PDF,
        output_type="processed",
        file_name="quarterly_report",
        sub_path="reports/pdf",
        include_timestamp=True,
    )
    print(f"✓ PDF report saved: {saved_path}")

    # Step 6: Generate configuration file
    print("\n6. Generating report configuration...")

    report_config = {
        "report_settings": {
            "name": "Quarterly Sales Report",
            "version": "1.0",
            "generated_date": datetime.now().isoformat(),
            "data_period": "2024 Q1-Q4",
        },
        "output_formats": {
            "excel": {
                "enabled": True,
                "sheets": list(analysis_views.keys()),
                "include_metadata": True,
            },
            "markdown": {
                "enabled": True,
                "include_frontmatter": True,
                "template": "comprehensive",
            },
            "json": {"enabled": True, "api_format": True, "include_metadata": True},
            "pdf": {"enabled": True, "format": "executive_summary"},
        },
        "data_sources": {
            "primary_data": "quarterly_sales_data",
            "analysis_views": list(analysis_views.keys()),
            "total_records": len(report_data),
        },
        "file_utils_config": {
            "storage_backend": "local",
            "output_directory": "reports",
            "timestamp_format": "%Y%m%d_%H%M%S",
            "subdirectories": ["excel", "markdown", "json", "pdf"],
        },
    }

    # Save configuration
    saved_path, _ = file_utils.save_document_to_storage(
        content=report_config,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="report_config",
        sub_path="config",
        include_timestamp=True,
    )
    print(f"✓ Report configuration saved: {saved_path}")

    print("\n=== Multi-Format Report Generation Complete ===")
    print(f"✓ Generated Excel report with {len(analysis_views)} sheets")
    print(f"✓ Created comprehensive Markdown report")
    print(f"✓ Generated JSON API response")
    print(f"✓ Created PDF executive summary")
    print(f"✓ Saved report configuration")
    print(f"✓ Processed {len(report_data)} data records")

    return {
        "excel_report": list(saved_files.values())[0],
        "markdown_report": saved_path,
        "json_api": saved_path,
        "pdf_report": saved_path,
        "config_file": saved_path,
        "metadata": metadata,
    }


if __name__ == "__main__":
    results = run_multi_format_reports()
    print(f"\nReport generation results: {results}")
