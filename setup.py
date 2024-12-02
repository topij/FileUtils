# src/utils/FileUtils/setup.py
from setuptools import setup, find_packages

setup(
    name="FileUtils",
    version="0.4.2",
    author="Topi Järvinen",
    packages=find_packages(),
    package_data={
        "FileUtils": ["config/*.yaml"],
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
        "parquet": ["pyarrow>=7.0.0"],
        "excel": ["openpyxl>=3.0.9"],
    },
)
