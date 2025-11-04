"""Example: Performance Optimization

This script demonstrates performance optimization techniques when using FileUtils
with large datasets, including memory management and parallel processing.
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
import psutil
import os
from FileUtils import FileUtils, OutputFileType


def generate_large_dataset(size_mb=100):
    """Generate a large dataset for performance testing."""
    print(f"Generating {size_mb}MB dataset...")

    # Calculate approximate number of rows for target size
    # Each row is roughly 100 bytes, so 1MB ≈ 10,000 rows
    target_rows = size_mb * 10000

    # Generate data in chunks to manage memory
    chunk_size = 50000
    chunks = []

    for i in range(0, target_rows, chunk_size):
        current_chunk_size = min(chunk_size, target_rows - i)

        chunk = pd.DataFrame(
            {
                "id": range(i, i + current_chunk_size),
                "timestamp": pd.date_range(
                    "2024-01-01", periods=current_chunk_size, freq="1min"
                ),
                "value": np.random.normal(100, 20, current_chunk_size),
                "category": np.random.choice(
                    ["A", "B", "C", "D", "E"], current_chunk_size
                ),
                "region": np.random.choice(
                    ["North", "South", "East", "West"], current_chunk_size
                ),
                "score": np.random.uniform(0, 100, current_chunk_size),
            }
        )

        chunks.append(chunk)

        # Memory management
        if i % (chunk_size * 10) == 0:
            print(f"  Generated {i:,} rows...")

    # Concatenate all chunks
    large_df = pd.concat(chunks, ignore_index=True)
    print(
        f"✓ Generated {len(large_df):,} rows ({large_df.memory_usage(deep=True).sum() / 1024**2:.1f}MB)"
    )

    return large_df


def monitor_memory():
    """Monitor memory usage."""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        "rss_mb": memory_info.rss / 1024**2,
        "vms_mb": memory_info.vms / 1024**2,
        "percent": process.memory_percent(),
    }


def run_performance_optimization():
    """Demonstrate performance optimization techniques."""
    print("=== Performance Optimization Demo ===\n")

    # Initialize FileUtils
    file_utils = FileUtils()

    # Step 1: Generate large dataset
    print("1. Generating large dataset...")
    start_time = time.time()
    start_memory = monitor_memory()

    large_data = generate_large_dataset(size_mb=50)  # 50MB dataset

    generation_time = time.time() - start_time
    generation_memory = monitor_memory()

    print(f"   ✓ Dataset generation completed")
    print(f"   - Time: {generation_time:.2f} seconds")
    print(
        f"   - Memory used: {generation_memory['rss_mb'] - start_memory['rss_mb']:.1f}MB"
    )
    print(f"   - Total memory: {generation_memory['rss_mb']:.1f}MB")

    # Step 2: Optimize data types
    print("\n2. Optimizing data types...")
    start_time = time.time()
    start_memory = monitor_memory()

    # Convert to more memory-efficient types
    optimized_data = large_data.copy()

    # Convert category to categorical
    optimized_data["category"] = optimized_data["category"].astype("category")
    optimized_data["region"] = optimized_data["region"].astype("category")

    # Convert float64 to float32 where precision allows
    optimized_data["value"] = optimized_data["value"].astype("float32")
    optimized_data["score"] = optimized_data["score"].astype("float32")

    # Convert int64 to int32
    optimized_data["id"] = optimized_data["id"].astype("int32")

    optimization_time = time.time() - start_time
    optimization_memory = monitor_memory()

    original_memory = large_data.memory_usage(deep=True).sum() / 1024**2
    optimized_memory = optimized_data.memory_usage(deep=True).sum() / 1024**2
    memory_savings = original_memory - optimized_memory

    print(f"   ✓ Data type optimization completed")
    print(f"   - Time: {optimization_time:.2f} seconds")
    print(
        f"   - Memory reduction: {memory_savings:.1f}MB ({memory_savings/original_memory*100:.1f}%)"
    )
    print(f"   - Original size: {original_memory:.1f}MB")
    print(f"   - Optimized size: {optimized_memory:.1f}MB")

    # Step 3: Chunked processing
    print("\n3. Processing data in chunks...")
    start_time = time.time()

    # Process data in chunks to manage memory
    chunk_size = 100000
    processed_chunks = []

    for i in range(0, len(optimized_data), chunk_size):
        chunk = optimized_data.iloc[i : i + chunk_size]

        # Perform some processing on the chunk
        chunk["value_normalized"] = (chunk["value"] - chunk["value"].mean()) / chunk[
            "value"
        ].std()
        chunk["score_category"] = pd.cut(
            chunk["score"],
            bins=5,
            labels=["Very Low", "Low", "Medium", "High", "Very High"],
        )

        processed_chunks.append(chunk)

        if i % (chunk_size * 5) == 0:
            print(f"   Processed {i:,} rows...")

    # Combine processed chunks
    processed_data = pd.concat(processed_chunks, ignore_index=True)

    processing_time = time.time() - start_time
    processing_memory = monitor_memory()

    print(f"   ✓ Chunked processing completed")
    print(f"   - Time: {processing_time:.2f} seconds")
    print(f"   - Memory peak: {processing_memory['rss_mb']:.1f}MB")

    # Step 4: Optimized saving
    print("\n4. Optimized data saving...")
    start_time = time.time()

    try:
        # Save as Parquet (most efficient for large datasets)
        saved_files, metadata = file_utils.save_data_to_storage(
            data=processed_data,
            output_filetype=OutputFileType.PARQUET,
            output_type="processed",
            file_name="large_dataset_optimized",
            include_timestamp=True,
        )

        save_time = time.time() - start_time
        save_memory = monitor_memory()

        print(f"   ✓ Data saved as Parquet")
        print(f"   - Time: {save_time:.2f} seconds")
        print(
            f"   - File size: {Path(list(saved_files.values())[0]).stat().st_size / 1024**2:.1f}MB"
        )
        print(f"   - Memory after save: {save_memory['rss_mb']:.1f}MB")

    except Exception as e:
        print(f"   ✗ Parquet save failed: {e}")
        # Fallback to CSV
        saved_files, metadata = file_utils.save_data_to_storage(
            data=processed_data,
            output_filetype=OutputFileType.CSV,
            output_type="processed",
            file_name="large_dataset_optimized",
            include_timestamp=True,
        )
        print(f"   ✓ Data saved as CSV (fallback)")

    # Step 5: Memory cleanup
    print("\n5. Memory cleanup...")
    start_memory = monitor_memory()

    # Delete large objects
    del large_data
    del optimized_data
    del processed_data
    del processed_chunks

    # Force garbage collection
    import gc

    gc.collect()

    cleanup_memory = monitor_memory()
    memory_freed = start_memory["rss_mb"] - cleanup_memory["rss_mb"]

    print(f"   ✓ Memory cleanup completed")
    print(f"   - Memory freed: {memory_freed:.1f}MB")
    print(f"   - Current memory: {cleanup_memory['rss_mb']:.1f}MB")

    # Step 6: Generate performance report
    print("\n6. Generating performance report...")

    performance_report = {
        "frontmatter": {
            "title": "Performance Optimization Report",
            "generated_date": datetime.now().isoformat(),
            "dataset_size": "50MB",
            "optimization_level": "high",
        },
        "body": f"""# Performance Optimization Report

## Dataset Overview

- **Original Size**: {original_memory:.1f}MB
- **Optimized Size**: {optimized_memory:.1f}MB
- **Memory Savings**: {memory_savings:.1f}MB ({memory_savings/original_memory*100:.1f}%)
- **Total Records**: {len(processed_data):,}

## Performance Metrics

### Generation Phase
- **Time**: {generation_time:.2f} seconds
- **Memory Used**: {generation_memory['rss_mb'] - start_memory['rss_mb']:.1f}MB
- **Peak Memory**: {generation_memory['rss_mb']:.1f}MB

### Optimization Phase
- **Time**: {optimization_time:.2f} seconds
- **Memory Reduction**: {memory_savings:.1f}MB
- **Optimization Rate**: {memory_savings/original_memory*100:.1f}%

### Processing Phase
- **Time**: {processing_time:.2f} seconds
- **Chunk Size**: {chunk_size:,} rows
- **Peak Memory**: {processing_memory['rss_mb']:.1f}MB

### Saving Phase
- **Time**: {save_time:.2f} seconds
- **Format**: Parquet
- **File Size**: {Path(list(saved_files.values())[0]).stat().st_size / 1024**2:.1f}MB

## Optimization Techniques Applied

### 1. Data Type Optimization
- **Categorical Conversion**: category → category type
- **Float Precision**: float64 → float32
- **Integer Optimization**: int64 → int32
- **Memory Savings**: {memory_savings:.1f}MB

### 2. Chunked Processing
- **Chunk Size**: {chunk_size:,} rows
- **Memory Management**: Controlled memory usage
- **Processing Efficiency**: Maintained performance

### 3. Format Optimization
- **Primary Format**: Parquet (compressed, efficient)
- **Fallback Format**: CSV (compatibility)
- **Compression**: Automatic compression

### 4. Memory Management
- **Garbage Collection**: Explicit cleanup
- **Object Deletion**: Remove large objects
- **Memory Monitoring**: Real-time tracking

## Recommendations

### For Large Datasets
1. **Use Parquet Format**: Best compression and performance
2. **Optimize Data Types**: Reduce memory footprint
3. **Process in Chunks**: Manage memory usage
4. **Monitor Memory**: Track usage patterns

### For Production Use
1. **Implement Monitoring**: Track performance metrics
2. **Set Memory Limits**: Prevent out-of-memory errors
3. **Use Efficient Formats**: Parquet for large data
4. **Clean Up Resources**: Explicit memory management

## Technical Details

- **FileUtils Version**: Latest
- **Processing Method**: Chunked processing
- **Memory Management**: Explicit cleanup
- **Format Optimization**: Parquet with compression
- **Performance Monitoring**: Real-time metrics
""",
    }

    # Save performance report
    saved_path, _ = file_utils.save_document_to_storage(
        content=performance_report,
        output_filetype=OutputFileType.MARKDOWN,
        output_type="processed",
        file_name="performance_report",
        sub_path="reports",
        include_timestamp=True,
    )
    print(f"   ✓ Performance report saved: {saved_path}")

    # Step 7: Create performance configuration
    print("\n7. Creating performance configuration...")

    performance_config = {
        "optimization_settings": {
            "data_types": {
                "categorical_columns": ["category", "region"],
                "float32_columns": ["value", "score"],
                "int32_columns": ["id"],
            },
            "chunked_processing": {
                "chunk_size": chunk_size,
                "memory_threshold_mb": 1000,
                "enable_chunking": True,
            },
            "format_optimization": {
                "primary_format": "parquet",
                "fallback_format": "csv",
                "compression": "snappy",
            },
        },
        "memory_management": {
            "monitoring": True,
            "cleanup_threshold_mb": 500,
            "garbage_collection": True,
            "object_deletion": True,
        },
        "performance_metrics": {
            "generation_time": generation_time,
            "optimization_time": optimization_time,
            "processing_time": processing_time,
            "save_time": save_time,
            "memory_savings_mb": memory_savings,
            "total_memory_freed_mb": memory_freed,
        },
        "file_utils_integration": {
            "storage_backend": "local",
            "performance_mode": "optimized",
            "memory_monitoring": True,
            "chunked_processing": True,
        },
    }

    # Save performance configuration
    saved_path, _ = file_utils.save_document_to_storage(
        content=performance_config,
        output_filetype=OutputFileType.YAML,
        output_type="processed",
        file_name="performance_config",
        sub_path="config",
        include_timestamp=True,
    )
    print(f"   ✓ Performance configuration saved: {saved_path}")

    print("\n=== Performance Optimization Complete ===")
    print(f"✓ Processed {len(processed_data):,} records")
    print(
        f"✓ Saved {memory_savings:.1f}MB memory ({memory_savings/original_memory*100:.1f}%)"
    )
    print(
        f"✓ Total processing time: {generation_time + optimization_time + processing_time + save_time:.2f} seconds"
    )
    print(f"✓ Memory cleanup: {memory_freed:.1f}MB freed")
    print(f"✓ Performance report generated")

    return {
        "data_file": list(saved_files.values())[0],
        "performance_report": saved_path,
        "performance_config": saved_path,
        "metrics": {
            "total_time": generation_time
            + optimization_time
            + processing_time
            + save_time,
            "memory_savings": memory_savings,
            "memory_freed": memory_freed,
            "records_processed": len(processed_data),
        },
    }


if __name__ == "__main__":
    results = run_performance_optimization()
    print(f"\nPerformance optimization results: {results}")
