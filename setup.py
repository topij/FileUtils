# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="file-utils",
    version="0.4.2",
    author="Topi Järvinen",
    description="File utilities for data science projects with optional Azure support",
    long_description=long_description,
    long_description_content_type="markdown",
    packages=find_packages(),
    package_data={
        "FileUtils": ["config.yaml"],
    },
    install_requires=[
        "pandas>=1.3.0",
        "pyyaml>=5.4.1",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "azure": ["azure-storage-blob>=12.0.0", "azure-identity>=1.5.0"],
        "parquet": ["pyarrow>=7.0.0"],
        "excel": ["openpyxl>=3.0.9"],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)
