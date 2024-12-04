# scripts/setup_dev.py

import subprocess
import os
import sys
from pathlib import Path


def run_command(cmd):
    """Run a command and capture output."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(e.stderr)
        return False


def setup_dev_environment():
    """Set up development environment."""
    print("Setting up development environment...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Upgrade pip
    if not run_command(f"{sys.executable} -m pip install --upgrade pip"):
        return False

    # Install test dependencies
    if not run_command(f"{sys.executable} -m pip install pytest pytest-cov"):
        return False

    # Install package in development mode
    if not run_command(f"{sys.executable} -m pip install -e ."):
        return False

    print("\nDevelopment environment setup complete!")
    return True


if __name__ == "__main__":
    if not setup_dev_environment():
        sys.exit(1)
