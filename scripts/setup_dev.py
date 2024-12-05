#!/usr/bin/env python3
import subprocess
import sys
import os
from pathlib import Path
import json
from typing import Optional


def get_conda_activation_command() -> str:
    """Get the proper conda activation command for the current platform."""
    if sys.platform == "win32":
        return "call activate"
    # For Linux/Mac, we need to source conda.sh first
    conda_exe = subprocess.check_output(["which", "conda"]).decode().strip()
    conda_path = Path(conda_exe).parent.parent
    return f". {conda_path}/etc/profile.d/conda.sh && conda activate"


def run_conda_command(cmd: str, env_name: Optional[str] = None, check: bool = True, capture_output: bool = False) -> tuple[bool, str]:
    """Run a command in conda environment.
    
    Args:
        cmd: Command to run
        env_name: Optional conda environment name
        check: Whether to treat non-zero exit codes as error
        capture_output: Whether to capture and return output instead of printing
    """
    if env_name:
        activate_cmd = get_conda_activation_command()
        cmd = f"{activate_cmd} {env_name} && {cmd}"
    
    # Run command in a new shell to ensure conda activation works
    shell_cmd = ["/bin/bash", "-c", cmd] if sys.platform != "win32" else ["cmd.exe", "/c", cmd]
    
    print(f"\nRunning: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(
                shell_cmd,
                check=False,
                text=True,
                capture_output=True
            )
            return result.returncode == 0, result.stdout
        else:
            result = subprocess.run(
                shell_cmd,
                check=False,
                text=True
            )
            return result.returncode == 0, ""
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        if check:
            return False, ""
        return True, ""


def get_conda_info():
    """Get conda info including environment list."""
    success, output = run_conda_command("conda env list --json", capture_output=True)
    if success:
        return json.loads(output)
    return None


def setup_dev_environment():
    """Set up development environment using conda."""
    print("Setting up development environment...")

    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Working directory: {project_root}")

    # Check if conda is available
    if not run_conda_command("conda --version", check=False)[0]:
        print("Error: conda is not installed or not in PATH")
        return False

    # Check if environment exists
    conda_info = get_conda_info()
    env_exists = False
    if conda_info:
        env_exists = any("fileutils" in env for env in conda_info.get("envs", []))

    # Setup steps
    if env_exists:
        print("\nEnvironment 'fileutils' already exists, updating...")
        steps = [
            ("conda env update -f environment.yaml", "Updating conda environment"),
            ("pip install -e .[all]", "Reinstalling package in development mode"),
        ]
    else:
        print("\nCreating new 'fileutils' environment...")
        steps = [
            ("conda env create -f environment.yaml", "Creating conda environment"),
            ("pip install -e .[all]", "Installing package in development mode"),
        ]

    # Run setup steps
    for cmd, description in steps:
        print(f"\n{description}...")
        if not run_conda_command(cmd, env_name="fileutils" if env_exists else None)[0]:
            print(f"Failed to {description.lower()}")
            return False

    # Handle pre-commit separately
    success, output = run_conda_command("pre-commit --version", env_name="fileutils", capture_output=True)
    if not success:
        print("\nSetting up pre-commit hooks...")
        if not run_conda_command("pre-commit install", env_name="fileutils")[0]:
            print("Failed to set up pre-commit hooks")
            return False

    print("\nDevelopment environment setup/update complete!")
    print("\nNext steps:")
    print("1. Activate the conda environment:")
    print("   conda activate fileutils")
    print("2. Run the tests: pytest")
    return True


if __name__ == "__main__":
    if not setup_dev_environment():
        sys.exit(1)