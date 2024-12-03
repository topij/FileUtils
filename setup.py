from setuptools import setup

setup(
    name="FileUtils",
    version="0.4.5",
    author="Topi Järvinen",
    description="File utilities for data science projects with Azure support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["FileUtils"],
    package_data={
        "FileUtils": [
            "config/*.yaml",
            "templates/*.example",
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
        ],
        "excel": [
            "openpyxl>=3.0.9",
        ],
        "all": [
            "azure-storage-blob>=12.0.0",
            "azure-identity>=1.5.0",
            "pyarrow>=7.0.0",
            "openpyxl>=3.0.9",
        ],
    },
    python_requires=">=3.8",
)
