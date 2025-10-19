#!/usr/bin/env python3
"""
Configurable Directories Example Script

This script demonstrates how to use FileUtils with custom directory names
for domain-specific projects. Perfect for document processing, content creation,
research projects, or any workflow where "data" doesn't make sense.

Examples covered:
1. Customer Success workflow (documents/)
2. Content creation workflow (assets/)
3. Research project workflow (experiments/)
4. Backward compatibility demonstration
"""

import sys
from pathlib import Path
import pandas as pd
import tempfile
import os

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from FileUtils import FileUtils, OutputFileType
from FileUtils.core.base import StorageError


def create_sample_data():
    """Create sample data for demonstration."""
    return {
        'Sales': pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'customer': ['Alice Corp', 'Bob Industries', 'Charlie Ltd', 'Diana Inc', 'Eve Systems'],
            'product': ['Widget A', 'Widget B', 'Widget A', 'Widget C', 'Widget B'],
            'amount': [1000, 2500, 1500, 3000, 2000],
            'date': pd.date_range('2024-01-01', periods=5, freq='D')
        }),
        'Customers': pd.DataFrame({
            'customer_id': [101, 102, 103, 104, 105],
            'name': ['Alice Corp', 'Bob Industries', 'Charlie Ltd', 'Diana Inc', 'Eve Systems'],
            'industry': ['Tech', 'Manufacturing', 'Finance', 'Healthcare', 'Tech'],
            'tier': ['Enterprise', 'Mid-Market', 'SMB', 'Enterprise', 'Mid-Market']
        }),
        'Products': pd.DataFrame({
            'product_id': [1, 2, 3],
            'name': ['Widget A', 'Widget B', 'Widget C'],
            'category': ['Basic', 'Premium', 'Enterprise'],
            'price': [100, 250, 500]
        })
    }


def demonstrate_customer_success_workflow(temp_dir):
    """Demonstrate Customer Success document workflow."""
    print("\n" + "="*60)
    print("🎯 CUSTOMER SUCCESS WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Create CS workflow configuration
    cs_config = {
        "directories": {
            "data_directory": "cs_workflow",
            "subdirectories": {
                "raw": "product_docs",        # latest-product-description
                "processed": "cs_documents",  # planning-md-master, generated_docx_output
                "templates": "templates"      # DOCX templates
            }
        }
    }
    
    file_utils = FileUtils(project_root=temp_dir, config_override=cs_config)
    
    print("📁 Directory Structure:")
    print("  cs_workflow/product_docs/     → Product documentation")
    print("  cs_workflow/cs_documents/    → CS plans, AI-generated content")
    print("  cs_workflow/templates/       → DOCX templates")
    
    # Step 1: Save product documentation (raw)
    print(f"\n📄 Step 1: Saving Product Documentation")
    sample_data = create_sample_data()
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=sample_data,
        output_filetype=OutputFileType.XLSX,
        output_type="raw",
        file_name="product_specification"
    )
    
    excel_file_path = list(saved_files.values())[0]
    print(f"✅ Product spec saved: {Path(excel_file_path).name}")
    
    # Step 2: Convert to CSV for AI processing
    print(f"\n🔄 Step 2: Converting to CSV for AI Processing")
    csv_files, structure_file = file_utils.convert_excel_to_csv_with_structure(
        excel_file_path=Path(excel_file_path).name,
        input_type="raw",
        output_type="processed",
        file_name="cs_analysis"
    )
    
    print(f"✅ Converted to {len(csv_files)} CSV files:")
    for sheet_name, csv_path in csv_files.items():
        print(f"  - {sheet_name}: {Path(csv_path).name}")
    
    # Step 3: Simulate AI processing (modify data)
    print(f"\n🤖 Step 3: Simulating AI Processing")
    
    # Load and modify Sales data
    sales_df = file_utils.load_single_file("cs_analysis_Sales.csv", input_type="processed")
    sales_df['ai_insights'] = sales_df['amount'].apply(lambda x: 'High Value' if x > 2000 else 'Standard')
    sales_df['recommendation'] = sales_df['customer'].apply(lambda x: 'Upsell' if 'Corp' in x else 'Retain')
    
    # Save modified data
    file_utils.save_data_to_storage(
        data=sales_df,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="cs_analysis_Sales",  # Overwrite original
        include_timestamp=False
    )
    
    print("✅ AI insights added to Sales data")
    
    # Step 4: Generate final CS report
    print(f"\n📊 Step 4: Generating Final CS Report")
    reconstructed_excel = file_utils.convert_csv_to_excel_workbook(
        structure_json_path=structure_file,
        input_type="processed",
        output_type="processed",
        file_name="cs_final_report"
    )
    
    print(f"✅ Final report generated: {Path(reconstructed_excel).name}")
    
    # Step 5: Create DOCX report using template
    print(f"\n📝 Step 5: Creating DOCX Report")
    
    # Create markdown content for DOCX
    markdown_content = """# Customer Success Analysis Report

## Executive Summary
This report analyzes customer data and provides AI-generated insights for CS planning.

## Key Findings
- **High Value Customers**: Alice Corp, Diana Inc
- **Upsell Opportunities**: Enterprise customers
- **Retention Focus**: Mid-Market and SMB segments

## Recommendations
1. Focus upselling efforts on Enterprise customers
2. Implement retention programs for Mid-Market segment
3. Monitor SMB customer satisfaction closely

---
*Report generated by AI workflow using FileUtils*
"""
    
    docx_path, _ = file_utils.save_document_to_storage(
        content=markdown_content,
        output_filetype=OutputFileType.DOCX,
        output_type="processed",
        file_name="cs_analysis_report"
    )
    
    print(f"✅ DOCX report created: {Path(docx_path).name}")
    
    return file_utils


def demonstrate_content_creation_workflow(temp_dir):
    """Demonstrate content creation workflow."""
    print("\n" + "="*60)
    print("🎨 CONTENT CREATION WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Create content creation configuration
    content_config = {
        "directories": {
            "data_directory": "assets",
            "subdirectories": {
                "raw": "source_materials",    # Original content
                "processed": "final_content", # Final deliverables
                "templates": "brand_templates" # Brand templates
            }
        }
    }
    
    file_utils = FileUtils(project_root=temp_dir, config_override=content_config)
    
    print("📁 Directory Structure:")
    print("  assets/source_materials/   → Original content")
    print("  assets/final_content/      → Final deliverables")
    print("  assets/brand_templates/    → Brand templates")
    
    # Create content data
    content_data = pd.DataFrame({
        'article_id': [1, 2, 3, 4, 5],
        'title': ['AI Trends 2024', 'Data Science Best Practices', 'Machine Learning Guide', 'Python Tips', 'Cloud Computing'],
        'category': ['AI', 'Data Science', 'ML', 'Programming', 'Cloud'],
        'word_count': [1200, 1500, 2000, 800, 1800],
        'status': ['Draft', 'Review', 'Published', 'Draft', 'Review']
    })
    
    # Save content inventory
    saved_files, _ = file_utils.save_data_to_storage(
        data=content_data,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="content_inventory"
    )
    
    print(f"✅ Content inventory saved: {Path(list(saved_files.values())[0]).name}")
    
    # Process content (simulate editorial workflow)
    processed_content = content_data.copy()
    processed_content['priority'] = processed_content['word_count'].apply(
        lambda x: 'High' if x > 1500 else 'Medium'
    )
    processed_content['publish_date'] = pd.date_range('2024-01-01', periods=len(processed_content), freq='W')
    
    # Save processed content
    file_utils.save_data_to_storage(
        data=processed_content,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="editorial_calendar"
    )
    
    print("✅ Editorial calendar created")
    
    return file_utils


def demonstrate_research_workflow(temp_dir):
    """Demonstrate research project workflow."""
    print("\n" + "="*60)
    print("🔬 RESEARCH PROJECT WORKFLOW DEMONSTRATION")
    print("="*60)
    
    # Create research configuration
    research_config = {
        "directories": {
            "data_directory": "experiments",
            "subdirectories": {
                "raw": "data_collection",      # Raw experimental data
                "processed": "analysis_results", # Analysis outputs
                "templates": "report_templates"  # Report templates
            }
        }
    }
    
    file_utils = FileUtils(project_root=temp_dir, config_override=research_config)
    
    print("📁 Directory Structure:")
    print("  experiments/data_collection/    → Raw experimental data")
    print("  experiments/analysis_results/    → Analysis outputs")
    print("  experiments/report_templates/    → Report templates")
    
    # Create experimental data
    experiment_data = pd.DataFrame({
        'experiment_id': [1, 2, 3, 4, 5],
        'treatment': ['Control', 'Treatment A', 'Treatment B', 'Control', 'Treatment A'],
        'measurement': [45.2, 52.1, 48.7, 44.8, 51.3],
        'replicate': [1, 1, 1, 2, 2],
        'date': pd.date_range('2024-01-01', periods=5, freq='D')
    })
    
    # Save raw experimental data
    saved_files, _ = file_utils.save_data_to_storage(
        data=experiment_data,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="experiment_001"
    )
    
    print(f"✅ Experimental data saved: {Path(list(saved_files.values())[0]).name}")
    
    # Perform analysis
    analysis_results = experiment_data.copy()
    analysis_results['normalized'] = (analysis_results['measurement'] - analysis_results['measurement'].mean()) / analysis_results['measurement'].std()
    analysis_results['significant'] = analysis_results['normalized'].abs() > 1.96
    
    # Save analysis results
    file_utils.save_data_to_storage(
        data=analysis_results,
        output_filetype=OutputFileType.CSV,
        output_type="processed",
        file_name="statistical_analysis"
    )
    
    print("✅ Statistical analysis completed")
    
    return file_utils


def demonstrate_backward_compatibility(temp_dir):
    """Demonstrate backward compatibility with default configuration."""
    print("\n" + "="*60)
    print("🔄 BACKWARD COMPATIBILITY DEMONSTRATION")
    print("="*60)
    
    # Use default configuration (no custom directories)
    file_utils = FileUtils(project_root=temp_dir)
    
    print("📁 Default Directory Structure:")
    print("  data/raw/        → Raw data")
    print("  data/processed/  → Processed data")
    print("  data/templates/  → Templates")
    
    # Test that everything still works with default config
    test_data = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, 20, 30]
    })
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=test_data,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="compatibility_test"
    )
    
    saved_path = list(saved_files.values())[0]
    print(f"✅ File saved to default location: {Path(saved_path).name}")
    print(f"   Path contains 'data/raw/': {'data/raw/' in str(saved_path)}")
    
    # Test loading
    loaded_data = file_utils.load_single_file("compatibility_test.csv", input_type="raw")
    print(f"✅ Data loaded successfully: {loaded_data.shape[0]} rows")
    
    return file_utils


def demonstrate_partial_configuration(temp_dir):
    """Demonstrate partial configuration (only data_directory specified)."""
    print("\n" + "="*60)
    print("⚙️ PARTIAL CONFIGURATION DEMONSTRATION")
    print("="*60)
    
    # Create partial config (only data_directory)
    partial_config = {
        "directories": {
            "data_directory": "my_project"
            # subdirectories not specified - should use defaults
        }
    }
    
    file_utils = FileUtils(project_root=temp_dir, config_override=partial_config)
    
    print("📁 Partial Configuration:")
    print("  my_project/raw/        → Custom main dir, default subdirs")
    print("  my_project/processed/  → Custom main dir, default subdirs")
    print("  my_project/templates/  → Custom main dir, default subdirs")
    
    # Test directory configuration
    dir_config = file_utils._get_directory_config()
    print(f"\n📋 Directory Configuration:")
    print(f"  Main directory: {dir_config['data_directory']}")
    print(f"  Raw subdirectory: {dir_config['raw']}")
    print(f"  Processed subdirectory: {dir_config['processed']}")
    print(f"  Templates subdirectory: {dir_config['templates']}")
    
    # Test file operations
    test_data = pd.DataFrame({'id': [1, 2], 'name': ['A', 'B']})
    
    saved_files, _ = file_utils.save_data_to_storage(
        data=test_data,
        output_filetype=OutputFileType.CSV,
        output_type="raw",
        file_name="partial_test"
    )
    
    saved_path = list(saved_files.values())[0]
    print(f"✅ File saved to: {Path(saved_path).name}")
    print(f"   Path contains 'my_project/raw/': {'my_project/raw/' in str(saved_path)}")
    
    return file_utils


def show_directory_structure(temp_dir):
    """Show the final directory structure for all demonstrations."""
    print("\n" + "="*60)
    print("📁 FINAL DIRECTORY STRUCTURE")
    print("="*60)
    
    print("All files created during demonstrations:")
    for item in sorted(Path(temp_dir).rglob('*')):
        if item.is_file():
            relative_path = item.relative_to(temp_dir)
            print(f"  {relative_path}")
    
    # Count files by directory
    print(f"\n📊 File Count by Directory:")
    directories = {}
    for item in Path(temp_dir).rglob('*'):
        if item.is_file():
            parent_dir = item.parent.name
            directories[parent_dir] = directories.get(parent_dir, 0) + 1
    
    for dir_name, count in sorted(directories.items()):
        print(f"  {dir_name}/: {count} files")


def main():
    """Main demonstration function."""
    print("🎯 FileUtils Configurable Directories Demonstration")
    print("="*60)
    print("This script demonstrates how to use custom directory names")
    print("for domain-specific projects with FileUtils.")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\n📁 Working in temporary directory: {temp_dir}")
            
            # Run all demonstrations
            demonstrate_customer_success_workflow(temp_dir)
            demonstrate_content_creation_workflow(temp_dir)
            demonstrate_research_workflow(temp_dir)
            demonstrate_backward_compatibility(temp_dir)
            demonstrate_partial_configuration(temp_dir)
            
            # Show final structure
            show_directory_structure(temp_dir)
            
            print(f"\n🎉 All demonstrations completed successfully!")
            print(f"\nKey Benefits Demonstrated:")
            print(f"  ✅ Domain-specific directory names")
            print(f"  ✅ Seamless integration with all FileUtils features")
            print(f"  ✅ Backward compatibility with existing projects")
            print(f"  ✅ Flexible configuration options")
            print(f"  ✅ Perfect for Customer Success, Content, Research workflows")
            
            print(f"\n💡 Next Steps:")
            print(f"  1. Copy the configuration examples to your project")
            print(f"  2. Customize directory names for your domain")
            print(f"  3. Start using FileUtils with your custom structure!")
            
    except StorageError as e:
        print(f"❌ Storage error during demonstration: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
