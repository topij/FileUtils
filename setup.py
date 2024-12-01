from setuptools import setup, find_packages
import os

# Read version from version file
with open(os.path.join("FileUtils", "version.py"), "r", encoding="utf-8") as f:
    exec(f.read())

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="FileUtils",
    version=__version__,
    author="Topi Järvinen",
    description="File utilities for data science projects with optional Azure support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/topij/FileUtils",
    packages=find_packages(exclude=["tests*"]),
    package_data={
        "FileUtils": [
            "config/*.yaml",
            "config/*.yml",
        ],
    },
    install_requires=[
        "pandas>=1.3.0",
        "pyyaml>=5.4.1",
        "python-dotenv>=0.19.0",
        "jsonschema>=3.2.0",
    ],
    extras_require={
        "azure": [
            "azure-storage-blob>=12.0.0",
            "azure-identity>=1.5.0",
        ],
        "parquet": [
            "pyarrow>=7.0.0",
            "fastparquet>=0.8.0",
        ],
        "excel": [
            "openpyxl>=3.0.9",
            "xlsxwriter>=3.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Bug Reports": "https://github.com/topij/FileUtils/issues",
        "Source": "https://github.com/topij/FileUtils",
    },
)
