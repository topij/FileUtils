"""Build script for FileUtils package."""

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


def run_command(command, check=True):
    """Run a command and print output."""
    print(f"\n=== Running: {command} ===")
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=True, text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if not check:
            return e
        sys.exit(1)


def clean_previous_builds():
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


def verify_version():
    """Verify version consistency."""
    print("\n=== Verifying version ===")
    sys.path.insert(0, str(Path.cwd()))
    from FileUtils.version import __version__

    with open("setup.py", "r") as f:
        setup_content = f.read()
    with open("pyproject.toml", "r") as f:
        pyproject_content = f.read()

    if f'version="{__version__}"' not in setup_content:
        raise ValueError("Version mismatch in setup.py")
    if f'version = "{__version__}"' not in pyproject_content:
        raise ValueError("Version mismatch in pyproject.toml")

    print(f"Version {__version__} verified in all files")
    return __version__


def build_package():
    """Build the package."""
    print("\n=== Building package ===")
    run_command("python -m build")


def verify_build(version):
    """Verify the built package."""
    print("\n=== Verifying build ===")
    run_command("twine check dist/*")

    # Check if expected files exist
    dist_dir = Path("dist")
    expected_files = [
        f"FileUtils-{version}.tar.gz",
        f"FileUtils-{version}-py3-none-any.whl",
    ]
    for file in expected_files:
        if not (dist_dir / file).exists():
            raise FileNotFoundError(f"Expected build file missing: {file}")
    print("Build files verified")


def test_installation():
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
    ]

    for cmd in commands:
        run_command(cmd)

    print("Installation test completed")


def main():
    """Main build process."""
    try:
        # Ensure build dependencies
        run_command("python -m pip install --upgrade pip build twine")

        # Clean and verify
        clean_previous_builds()
        version = verify_version()

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

    except Exception as e:
        print(f"\nBuild failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
