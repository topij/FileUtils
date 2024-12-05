"""Build script for FileUtils package."""

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Optional



def clean_previous_builds() -> None:
    """Remove previous build artifacts."""
    print("\n=== Cleaning previous builds ===")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    
    cleaned = []
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            cleaned.append(str(path))
    
    if cleaned:
        print("Cleaned:")
        for path in cleaned:
            print(f"  {path}")
    else:
        print("Nothing to clean")
    
    # Verify dist directory is empty/doesn't exist
    dist_dir = Path("dist")
    if dist_dir.exists():
        remaining = list(dist_dir.iterdir())
        if remaining:
            print("\nWARNING: Files still present in dist/:")
            for file in remaining:
                print(f"  {file.name}")
    
    print("Clean completed")


def verify_directory_structure() -> None:
    """Verify package directory structure."""
    print("\n=== Verifying directory structure ===")

    required_dirs = [
        "src/FileUtils",
        "src/FileUtils/core",
        "src/FileUtils/storage",
        "src/FileUtils/config",
        "src/FileUtils/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "docs",
    ]

    required_files = [
        "src/FileUtils/__init__.py",
        "src/FileUtils/core/__init__.py",
        "src/FileUtils/storage/__init__.py",
        "src/FileUtils/config/__init__.py",
        "src/FileUtils/utils/__init__.py",
        "pyproject.toml",
        "setup.py",
        "README.md",
    ]

    # Check directories
    for dir_path in required_dirs:
        path = Path(dir_path)
        if not path.exists():
            print(f"Creating missing directory: {dir_path}")
            path.mkdir(parents=True)

    # Check files
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")

    print("Directory structure verified")


def verify_version() -> str:
    """Verify version consistency."""
    print("\n=== Verifying version ===")
    sys.path.insert(0, str(Path.cwd() / "src"))
    from FileUtils.version import __version__

    files_to_check = {
        # "setup.py": f'version="{__version__}"',
        "pyproject.toml": f'version = "{__version__}"',
    }

    for file_path, version_string in files_to_check.items():
        with open(file_path, "r") as f:
            content = f.read()
            if version_string not in content:
                raise ValueError(f"Version mismatch in {file_path}")

    print(f"Version {__version__} verified in all files")
    return __version__


def verify_dependencies():
    """Verify all dependencies are listed in pyproject.toml."""
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
        
        required_deps = [
            "pandas>=1.3.0",
            "pyyaml>=5.4.1", 
            "python-dotenv>=0.19.0",
            "jsonschema>=3.2.0"
        ]

        for dep in required_deps:
            if dep not in content:
                raise ValueError(f"Missing core dependency in pyproject.toml: {dep}")

        print("Dependencies verified")
    except Exception as e:
        raise ValueError(f"Dependency verification failed: {e}")


def run_command(cmd: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command and print output in real-time unless captured.
    
    Args:
        cmd: Command to run
        check: Whether to treat non-zero exit codes as error
        capture_output: Whether to capture and return output instead of printing
        
    Returns:
        CompletedProcess: The completed process with return code and output
    """
    print(f"\nRunning: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                check=False,
                text=True,
                capture_output=True
            )
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                check=False,
                text=True
            )
        
        if check and result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
            if capture_output and result.stderr:
                print(f"Error output: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd)
            
        return result
        
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if check:
            raise
        return subprocess.CompletedProcess(cmd, -1)


def test_installation() -> None:
    """Test package installation in a fresh conda environment."""
    print("\n=== Testing installation ===")
    test_env_name = "fileutils_test"

    # Remove existing test environment if it exists
    run_command(f"conda env remove -n {test_env_name} --yes", check=False)

    # Create fresh conda environment with minimum Python
    result = run_command(f"conda create -n {test_env_name} python=3.8 -y")
    if result.returncode != 0:
        print("Failed to create conda environment")
        return

    # Get wheel file
    wheel = next(Path("dist").glob("*.whl"))

    # Install and test package
    commands = [
        f"conda run -n {test_env_name} pip install {wheel}[all]",
        f'conda run -n {test_env_name} python -c "from FileUtils.version import __version__; print(__version__)"',
        f'conda run -n {test_env_name} python -c "from FileUtils.core.base import BaseStorage"',
        f'conda run -n {test_env_name} python -c "from FileUtils.storage.azure import AzureStorage"',
        f'conda run -n {test_env_name} python -c "from FileUtils import FileUtils"',  # Basic import test
    ]

    success = True
    for cmd in commands:
        result = run_command(cmd)
        if result.returncode != 0:
            print(f"\nInstallation test failed at command: {cmd}")
            success = False
            break

    # Clean up
    run_command(f"conda env remove -n {test_env_name} --yes", check=False)

    if success:
        print("Installation test completed successfully")
    else:
        print("Installation test failed")


def build_package() -> None:
    """Build the package."""
    print("\n=== Building package ===")
    try:
        # First try to build
        result = subprocess.run(
            ["python", "-m", "build"], capture_output=True, text=True
        )

        # Print output regardless of success/failure
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Now raise if there was an error
        result.check_returncode()
    except Exception as e:
        print(f"Build failed: {e}")
        print("Try running with: python -m build -v")  # Suggest verbose build
        raise


def verify_build(version: str) -> None:
    """Verify the built package."""
    print("\n=== Verifying build ===")
    run_command("twine check dist/*")

    dist_dir = Path("dist")
    print("\nActual files in dist/:")
    for file in dist_dir.iterdir():
        print(f"  {file.name}")

    # Find files that match the version pattern regardless of trailing zeros
    wheel_pattern = f"FileUtils-{version.split('.')[0]}.{version.split('.')[1]}"
    tar_pattern = f"fileutils-{version.split('.')[0]}.{version.split('.')[1]}"

    matching_wheel = list(dist_dir.glob(f"{wheel_pattern}*-py3-none-any.whl"))
    matching_tar = list(dist_dir.glob(f"{tar_pattern}*.tar.gz"))

    if not matching_wheel or not matching_tar:
        print(f"\nMissing expected files for version {version}")
        raise FileNotFoundError("Build verification failed - missing files")

    print("Build files verified successfully!")

def run_tests(skip_tests: bool = False) -> bool:
    """Run the test suite.

    Args:
        skip_tests: If True, skip running tests

    Returns:
        bool: True if tests passed or were skipped, False if tests failed
    """
    if skip_tests:
        print("\n=== Skipping tests ===")
        return True

    print("\n=== Running tests ===")
    try:
        result = run_command("pytest tests/unit", check=False)
        if result and result.returncode != 0:
            print("Warning: Unit tests failed!")
            return False

        # Only run integration tests if credentials are available
        if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
            result = run_command("pytest tests/integration", check=False)
            if result and result.returncode != 0:
                print("Warning: Integration tests failed!")
                return False
        else:
            print("Skipping integration tests (no Azure credentials)")

        return True
    except Exception as e:
        print(f"Warning: Failed to run tests: {e}")
        return False


def main() -> None:
    """Main build process."""
    try:
        # Add command line argument parsing
        import argparse

        parser = argparse.ArgumentParser(description="Build FileUtils package")
        parser.add_argument(
            "--skip-tests", action="store_true", help="Skip running tests"
        )
        args = parser.parse_args()

        # Ensure build dependencies
        run_command("python -m pip install --upgrade pip build twine", check=False)

        # If not skipping tests, try to install test dependencies
        if not args.skip_tests:
            result = run_command("python -m pip install pytest pytest-cov", check=False)
            if result and result.returncode != 0:
                print(
                    "Warning: Could not install test dependencies. Tests will be skipped."
                )
                args.skip_tests = True

        # Verify structure and dependencies
        verify_directory_structure()
        verify_dependencies()

        # Clean and verify
        clean_previous_builds()
        version = verify_version()

        # Run tests (if not skipped)
        tests_ok = run_tests(args.skip_tests)
        if not tests_ok:
            print("\nWarning: Tests failed or were skipped. Continuing with build...")

        # Build and verify
        build_package()
        verify_build(version)

        # Test installation
        test_installation()

        print("\n=== Build completed successfully ===")
        print(f"Version: {version}")
        print("Built files:")
        for file in Path("dist").glob("*"):
            print(f"  - {file.name}")

        if not tests_ok:
            print(
                "\nWarning: Build completed but tests were not successful or were skipped."
            )

    except Exception as e:
        print(f"\nBuild failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
