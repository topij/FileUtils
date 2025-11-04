"""Example: AI/Agentic Workflow with FileUtils

This script demonstrates how to use FileUtils in AI/agentic workflows,
including structured data processing, document generation, and multi-format outputs.
"""

import sys
from pathlib import Path

# Add project src directory to path (for local development)
project_root = Path(__file__).resolve().parent.parent
src_path = str(project_root / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from datetime import datetime

import numpy as np
import pandas as pd

from FileUtils import FileUtils, OutputFileType


def simulate_ai_analysis():
    """Simulate AI analysis results."""
    np.random.seed(42)

    # Simulate customer sentiment analysis
    customers = [f"Customer_{i:03d}" for i in range(1, 101)]
    sentiments = np.random.choice(
        ["positive", "negative", "neutral"], 100, p=[0.6, 0.2, 0.2]
    )
    confidence_scores = np.random.uniform(0.7, 0.95, 100)

    sentiment_data = pd.DataFrame(
        {
            "customer_id": customers,
            "sentiment": sentiments,
            "confidence": confidence_scores,
            "analysis_date": datetime.now(),
            "model_version": "sentiment-v2.1",
        }
    )

    # Simulate recommendation engine results
    products = ["Product A", "Product B", "Product C", "Product D", "Product E"]
    recommendations = []

    for customer in customers:
        # Generate personalized recommendations
        recommended_products = np.random.choice(
            products, size=np.random.randint(2, 5), replace=False
        )
        for product in recommended_products:
            score = np.random.uniform(0.6, 0.95)
            recommendations.append(
                {
                    "customer_id": customer,
                    "product": product,
                    "recommendation_score": score,
                    "reason": f"Based on purchase history and preferences",
                }
            )

    recommendation_data = pd.DataFrame(recommendations)

    return sentiment_data, recommendation_data


def run_ai_workflow():
    """Run an AI/agentic workflow using FileUtils."""
    print("=== AI/Agentic Workflow with FileUtils ===\n")

    # Initialize FileUtils
    file_utils = FileUtils()

    # Step 1: Generate AI analysis results
    print("1. Generating AI analysis results...")
    sentiment_data, recommendation_data = simulate_ai_analysis()

    # Save AI results as structured data
    ai_results = {
        "sentiment_analysis": sentiment_data,
        "recommendations": recommendation_data,
    }

    saved_files, metadata = file_utils.save_with_metadata(
        data=ai_results,
        output_filetype=OutputFileType.XLSX,
        output_type="processed",
        file_name="ai_analysis_results",
        sub_path="ai_outputs",
        include_timestamp=True,
    )
    print(f"✓ AI results saved: {list(saved_files.values())[0]}")

    # Step 2: Generate AI insights document
    print("\n2. Generating AI insights document...")

    # Calculate insights
    sentiment_summary = sentiment_data["sentiment"].value_counts()
    avg_confidence = sentiment_data["confidence"].mean()
    top_recommendations = (
        recommendation_data.groupby("product")["recommendation_score"]
        .mean()
        .sort_values(ascending=False)
    )

    # Create structured insights document
    insights_doc = {
        "frontmatter": {
            "title": "AI Analysis Report",
            "generated_by": "AI Agent v2.1",
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "Customer Sentiment & Recommendations",
            "confidence_threshold": 0.8,
            "tags": [
                "AI",
                "Sentiment Analysis",
                "Recommendations",
                "Customer Insights",
            ],
        },
        "body": f"""# AI Analysis Report

## Executive Summary

This report presents AI-generated insights from customer sentiment analysis and personalized product recommendations.

## Sentiment Analysis Results

### Overall Sentiment Distribution
- **Positive**: {sentiment_summary.get('positive', 0)} customers ({sentiment_summary.get('positive', 0)/len(sentiment_data)*100:.1f}%)
- **Negative**: {sentiment_summary.get('negative', 0)} customers ({sentiment_summary.get('negative', 0)/len(sentiment_data)*100:.1f}%)
- **Neutral**: {sentiment_summary.get('neutral', 0)} customers ({sentiment_summary.get('neutral', 0)/len(sentiment_data)*100:.1f}%)

### Model Performance
- **Average Confidence**: {avg_confidence:.3f}
- **Total Customers Analyzed**: {len(sentiment_data)}
- **Model Version**: sentiment-v2.1

## Recommendation Engine Results

### Top Recommended Products
{chr(10).join([f"- **{product}**: {score:.3f} avg score" for product, score in top_recommendations.head(3).items()])}

### Recommendation Statistics
- **Total Recommendations Generated**: {len(recommendation_data)}
- **Average Recommendation Score**: {recommendation_data['recommendation_score'].mean():.3f}
- **High-Confidence Recommendations**: {len(recommendation_data[recommendation_data['recommendation_score'] > 0.8])}

## AI-Generated Insights

### Key Findings
1. **Customer Sentiment**: {sentiment_summary.idxmax()} sentiment dominates with {sentiment_summary.max()} customers
2. **Recommendation Quality**: {top_recommendations.index[0]} shows highest recommendation scores
3. **Model Confidence**: Average confidence of {avg_confidence:.3f} indicates reliable predictions

### Actionable Recommendations
1. **Focus on Positive Sentiment**: Leverage positive customer feedback for marketing
2. **Address Negative Sentiment**: Investigate {sentiment_summary.get('negative', 0)} negative cases
3. **Optimize Recommendations**: Prioritize {top_recommendations.index[0]} in marketing campaigns
4. **Model Monitoring**: Continue monitoring model performance and confidence scores

## Technical Details

- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Data Processing**: FileUtils pipeline with AI integration
- **Output Formats**: Excel analysis + Markdown insights
- **Confidence Threshold**: 0.8 for high-confidence recommendations

## Next Steps

1. Review sentiment analysis results with customer service team
2. Implement top product recommendations in marketing campaigns
3. Schedule follow-up analysis for model performance monitoring
4. Consider A/B testing for recommendation strategies
""",
    }

    # Save insights document
    saved_path, _ = file_utils.save_document_to_storage(
        content=insights_doc,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="ai_insights_report",
        sub_path="ai_outputs",
        include_timestamp=True,
    )
    print(f"✓ AI insights document saved: {saved_path}")

    # Step 3: Generate API response format
    print("\n3. Generating API response format...")

    # Create API response structure
    api_response = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "analysis_id": f"ai_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "results": {
            "sentiment_analysis": {
                "total_customers": len(sentiment_data),
                "sentiment_distribution": sentiment_summary.to_dict(),
                "average_confidence": float(avg_confidence),
                "model_version": "sentiment-v2.1",
            },
            "recommendations": {
                "total_recommendations": len(recommendation_data),
                "average_score": float(
                    recommendation_data["recommendation_score"].mean()
                ),
                "top_products": top_recommendations.head(5).to_dict(),
                "high_confidence_count": int(
                    len(
                        recommendation_data[
                            recommendation_data["recommendation_score"] > 0.8
                        ]
                    )
                ),
            },
        },
        "metadata": {
            "processing_time": "2.3 seconds",
            "model_versions": ["sentiment-v2.1", "recommendation-v1.8"],
            "confidence_threshold": 0.8,
            "data_quality_score": 0.95,
        },
    }

    # Save API response
    saved_path, _ = file_utils.save_document_to_storage(
        content=api_response,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="ai_api_response",
        sub_path="api_outputs",
        include_timestamp=True,
    )
    print(f"✓ API response saved: {saved_path}")

    # Step 4: Generate configuration for AI models
    print("\n4. Generating AI model configuration...")

    model_config = {
        "models": {
            "sentiment_analysis": {
                "name": "sentiment-v2.1",
                "type": "transformer",
                "parameters": {
                    "max_length": 512,
                    "batch_size": 32,
                    "learning_rate": 0.0001,
                    "epochs": 10,
                },
                "performance": {
                    "accuracy": 0.92,
                    "precision": 0.89,
                    "recall": 0.91,
                    "f1_score": 0.90,
                },
            },
            "recommendation_engine": {
                "name": "recommendation-v1.8",
                "type": "collaborative_filtering",
                "parameters": {
                    "factors": 50,
                    "regularization": 0.01,
                    "iterations": 100,
                },
                "performance": {"rmse": 0.85, "mae": 0.67, "coverage": 0.95},
            },
        },
        "pipeline_config": {
            "input_formats": ["csv", "json"],
            "output_formats": ["excel", "markdown", "json"],
            "processing_steps": [
                "data_validation",
                "sentiment_analysis",
                "recommendation_generation",
                "insight_extraction",
                "report_generation",
            ],
            "quality_checks": [
                "confidence_threshold",
                "data_completeness",
                "model_performance",
            ],
        },
        "file_utils_integration": {
            "storage_backend": "local",
            "output_directory": "ai_outputs",
            "timestamp_format": "%Y%m%d_%H%M%S",
            "metadata_tracking": True,
        },
    }

    # Save model configuration
    saved_path, _ = file_utils.save_document_to_storage(
        content=model_config,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="ai_model_config",
        sub_path="config",
        include_timestamp=True,
    )
    print(f"✓ Model configuration saved: {saved_path}")

    # Step 5: Generate summary report
    print("\n5. Generating summary report...")

    summary_report = {
        "workflow_summary": {
            "name": "AI/Agentic Workflow",
            "execution_time": datetime.now().isoformat(),
            "status": "completed",
            "outputs_generated": 4,
        },
        "data_processed": {
            "sentiment_records": len(sentiment_data),
            "recommendation_records": len(recommendation_data),
            "total_insights": len(sentiment_summary) + len(top_recommendations),
        },
        "outputs": {
            "analysis_excel": "ai_analysis_results.xlsx",
            "insights_markdown": "ai_insights_report.md",
            "api_response_json": "ai_api_response.json",
            "model_config_yaml": "ai_model_config.yaml",
        },
        "quality_metrics": {
            "average_confidence": float(avg_confidence),
            "high_confidence_ratio": float(
                len(
                    recommendation_data[
                        recommendation_data["recommendation_score"] > 0.8
                    ]
                )
                / len(recommendation_data)
            ),
            "data_completeness": 1.0,
            "model_performance": "excellent",
        },
    }

    # Save summary report
    saved_path, _ = file_utils.save_document_to_storage(
        content=summary_report,
        output_filetype=OutputFileType.JSON,
        output_type="processed",
        file_name="workflow_summary",
        sub_path="reports",
        include_timestamp=True,
    )
    print(f"✓ Summary report saved: {saved_path}")

    print("\n=== AI Workflow Complete ===")
    print(f"✓ Processed {len(sentiment_data)} sentiment records")
    print(f"✓ Generated {len(recommendation_data)} recommendations")
    print(f"✓ Created 4 output files")
    print(f"✓ Generated insights document")
    print(f"✓ Saved API response format")
    print(f"✓ Created model configuration")

    return {
        "analysis_results": list(saved_files.values())[0],
        "insights_document": saved_path,
        "api_response": saved_path,
        "model_config": saved_path,
        "summary_report": saved_path,
    }


if __name__ == "__main__":
    results = run_ai_workflow()
    print(f"\nWorkflow results: {results}")
