#!/usr/bin/env python3
"""
Development environment setup script for SuiPy.

This script automates the creation of a virtual environment and installation
of all development dependencies.
"""

import os
import subprocess
import sys
import venv
from pathlib import Path


def run_command(cmd, check=True, cwd=None):
    """Run a shell command and handle errors."""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, cwd=cwd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def create_venv(venv_path):
    """Create a virtual environment."""
    print(f"Creating virtual environment at {venv_path}")
    venv.create(venv_path, with_pip=True)


def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def get_venv_pip(venv_path):
    """Get the path to the pip executable in the virtual environment."""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "pip.exe"
    else:
        return venv_path / "bin" / "pip"


def main():
    """Main setup function."""
    # Get project root directory
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    
    print("🚀 Setting up SuiPy development environment")
    print(f"Project root: {project_root}")
    
    # Check if virtual environment already exists
    if venv_path.exists():
        response = input(f"Virtual environment already exists at {venv_path}. Recreate? (y/N): ")
        if response.lower() in ['y', 'yes']:
            print("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print("Using existing virtual environment.")
    
    # Create virtual environment if it doesn't exist
    if not venv_path.exists():
        create_venv(venv_path)
    
    # Get paths to executables
    python_exe = get_venv_python(venv_path)
    pip_exe = get_venv_pip(venv_path)
    
    # Upgrade pip
    print("Upgrading pip...")
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install production dependencies
    print("Installing production dependencies...")
    requirements_file = project_root / "requirements.txt"
    if requirements_file.exists():
        run_command([str(pip_exe), "install", "-r", str(requirements_file)])
    
    # Install development dependencies
    print("Installing development dependencies...")
    dev_requirements_file = project_root / "requirements-dev.txt"
    if dev_requirements_file.exists():
        run_command([str(pip_exe), "install", "-r", str(dev_requirements_file)])
    
    # Install package in development mode
    print("Installing SuiPy in development mode...")
    run_command([str(pip_exe), "install", "-e", "."], cwd=project_root)
    
    print("\n✅ Development environment setup complete!")
    print("\nTo activate the virtual environment:")
    
    if sys.platform == "win32":
        print(f"  {venv_path}\\Scripts\\activate")
    else:
        print(f"  source {venv_path}/bin/activate")
    
    print("\nTo run the example:")
    print("  python examples/coin_query_example.py")
    
    print("\nTo run tests (when available):")
    print("  pytest")


if __name__ == "__main__":
    main() 