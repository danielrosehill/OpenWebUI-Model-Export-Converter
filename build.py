#!/usr/bin/env python3
"""
Build script for creating a standalone executable for the GUI application using PyInstaller.
"""

import os
import sys
import subprocess

def check_pyinstaller():
    """Check if PyInstaller is installed, and install it if not."""
    try:
        import PyInstaller
        print("PyInstaller is already installed.")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully.")

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        "pandas",
        "openpyxl",
        "pyyaml",
        "ttkthemes"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Package {package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Package {package} installed successfully.")

def build_gui():
    """Build the GUI application."""
    print("\n=== Building GUI Application ===")
    
    # Create gui/dist directory if it doesn't exist
    os.makedirs("gui/dist", exist_ok=True)
    
    # Define PyInstaller command for GUI
    gui_command = [
        "pyinstaller",
        "--name=OpenWebUI-Export-GUI",
        "--windowed",  # No console window
        "--onefile",   # Single executable file
        "--icon=gui/icon.ico" if os.path.exists("gui/icon.ico") else "",
        "--distpath=gui/dist",  # Output to gui/dist directory
        "--workpath=gui/build",  # Work files in gui/build directory
        "--clean",
        "gui/program.py"
    ]
    
    # Remove empty arguments
    gui_command = [arg for arg in gui_command if arg]
    
    # Run PyInstaller
    subprocess.check_call(gui_command)
    
    print("GUI application built successfully.")
    print(f"Executable created at: {os.path.abspath('gui/dist/OpenWebUI-Export-GUI')}")

def main():
    """Main function to build the GUI application."""
    print("=== OpenWebUI Model Export Converter Build Script ===")
    
    # Check if PyInstaller is installed
    check_pyinstaller()
    
    # Check if all dependencies are installed
    check_dependencies()
    
    # Build GUI application
    build_gui()
    
    print("\n=== Build Completed Successfully ===")
    print("The executable is available in the 'gui/dist' directory.")

if __name__ == "__main__":
    main()
