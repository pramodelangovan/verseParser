#!/usr/bin/env python3
"""
Setup script for Verse Parser project.
Creates virtual environment, installs dependencies, and builds the executable.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}\n")

    try:
        result = subprocess.run(command, shell=True, check=False)
        if result.returncode != 0:
            print(f"\n❌ Error: {description} failed with return code {result.returncode}")
            return False
        print(f"\n✓ {description} completed successfully")
        return True
    except Exception as e:
        print(f"\n❌ Error running command: {e}")
        return False


def get_python_executable():
    """Get the Python executable path based on OS"""
    is_windows = platform.system() == "Windows"
    venv_path = Path(".venv")

    if is_windows:
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    return str(python_exe)


def get_pip_executable():
    """Get the pip executable path based on OS"""
    is_windows = platform.system() == "Windows"
    venv_path = Path(".venv")

    if is_windows:
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"

    return str(pip_exe)


def get_pyinstaller_executable():
    """Get the PyInstaller executable path based on OS"""
    is_windows = platform.system() == "Windows"
    venv_path = Path(".venv")

    if is_windows:
        pyinstaller_exe = venv_path / "Scripts" / "pyinstaller.exe"
    else:
        pyinstaller_exe = venv_path / "bin" / "pyinstaller"

    return str(pyinstaller_exe)


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  VERSE PARSER - SETUP SCRIPT")
    print("="*60)

    # Navigate to parent directory (project root)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Step 1: Create virtual environment
    if not Path(".venv").exists():
        if not run_command(f"{sys.executable} -m venv .venv", "Creating virtual environment"):
            return False
    else:
        print("\n✓ Virtual environment already exists")

    # Step 2: Upgrade pip
    pip_exe = get_pip_executable()
    if not run_command(f"{pip_exe} install --upgrade pip", "Upgrading pip"):
        return False

    # Step 3: Install requirements
    if not run_command(f"{pip_exe} install -r requirements.txt", "Installing requirements"):
        return False

    # Step 4: Build executable with PyInstaller
    pyinstaller_exe = get_pyinstaller_executable()
    # .venv\Scripts\pyinstaller --onefile --windowed --name VerseParser gui.py
    build_command = (
        f'{pyinstaller_exe} --onefile --windowed --name VerseParser '
        '--distpath ./dist --buildpath ./build gui.py'
    )
    if not run_command(build_command, "Building executable with PyInstaller"):
        return False

    # Success message
    print("\n" + "="*60)
    print("  ✓ SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nThe executable is located at: dist/VerseParser.exe")
    print("You can now run the application using the generated .exe file")
    print()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
