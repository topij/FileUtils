"""Build script for FileUtils package."""

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path
from typing import List, Optional


# def run_command(
#     command: str, check: bool = True
# ) -> Optional[subprocess.CompletedProcess]:
#     """Run a command and print output."""
#     print(f"\n=== Running: {command} ===")
#     try:
#         result = subprocess.run(
#             command, shell=True, check=check, capture_output=True, text=True
#         )
#         if result.stdout:
#             print(result.stdout)
#         if result.stderr:
#             print(result.stderr, file=sys.stderr)
#         return result
#     except subprocess.CalledProcessError as e:
#         print(f"Error running command: {e}", file=sys.stderr)
#         if not check:
#             return e
#         sys.exit(1)


def clean_previous_builds() -> None:
    """Remove previous build artifacts."""
    print("\n=== Cleaning previous builds ===")
    dirs_to_clean = ["build", "dist", "*.egg-info"]

    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

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
        "setup.py": f'version="{__version__}"',
        "pyproject.toml": f'version = "{__version__}"',
    }

    for file_path, version_string in files_to_check.items():
        with open(file_path, "r") as f:
            content = f.read()
            if version_string not in content:
                raise ValueError(f"Version mismatch in {file_path}")

    print(f"Version {__version__} verified in all files")
    return __version__


def verify_dependencies() -> None:
    """Verify all dependencies are listed correctly."""
    print("\n=== Verifying dependencies ===")

    # Core dependencies from setup.py
    with open("setup.py", "r") as f:
        setup_content = f.read()

    required_deps = [
        "pandas>=1.3.0",
        "pyyaml>=5.4.1",
        "python-dotenv>=0.19.0",
        "jsonschema>=3.2.0",
    ]

    for dep in required_deps:
        if dep not in setup_content:
            raise ValueError(f"Missing core dependency in setup.py: {dep}")

    print("Dependencies verified")


def run_command(
    command: str, check: bool = True
) -> Optional[subprocess.CompletedProcess]:
    """Run a command and print output."""
    print(f"\n=== Running: {command} ===")
    try:
        # Don't capture output so we can see it in real time
        result = subprocess.run(
            command,
            shell=True,
            check=False,  # Don't raise exception immediately
            capture_output=False,  # Show output in real time
        )
        if result.returncode != 0 and check:
            print(f"Command failed with exit code {result.returncode}")
            sys.exit(result.returncode)
        return result
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if check:
            raise
        return None


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
    expected_files = [
        f"FileUtils-{version}.tar.gz",
        f"FileUtils-{version}-py3-none-any.whl",
    ]

    for file in expected_files:
        if not (dist_dir / file).exists():
            raise FileNotFoundError(f"Expected build file missing: {file}")

    print("Build files verified")


def test_installation() -> None:
    """Test package installation in a fresh environment."""
    print("\n=== Testing installation ===")
    test_env = Path("test_env")
    if test_env.exists():
        shutil.rmtree(test_env)

    # Create and activate virtual environment
    venv.create(test_env, with_pip=True)

    # Determine activation script
    if sys.platform == "win32":
        activate_script = test_env / "Scripts" / "activate.bat"
        activate_cmd = str(activate_script)
    else:
        activate_script = test_env / "bin" / "activate"
        activate_cmd = f"source {activate_script}"

    # Install and test package
    wheel = next(Path("dist").glob("*.whl"))
    commands = [
        f"{activate_cmd} && pip install {wheel}[all]",
        f'{activate_cmd} && python -c "from FileUtils import FileUtils; print(FileUtils.__version__)"',
        # Test imports of new modules
        f'{activate_cmd} && python -c "from FileUtils.core.base import BaseStorage"',
        f'{activate_cmd} && python -c "from FileUtils.storage.azure import AzureStorage"',
    ]

    for cmd in commands:
        run_command(cmd)

    print("Installation test completed")


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
