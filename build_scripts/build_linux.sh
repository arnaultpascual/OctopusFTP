#!/bin/bash

# OctopusFTP - Linux Build Script
# This script creates a standalone executable for Linux

echo "========================================"
echo "OctopusFTP - Linux Build Script"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip python3-tkinter"
    echo "  Arch:          sudo pacman -S python python-pip tk"
    exit 1
fi

echo "[1/3] Installing PyInstaller..."
python3 -m pip install --upgrade pip
python3 -m pip install pyinstaller
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller"
    exit 1
fi

echo ""
echo "[2/3] Building executable..."
cd ..
python3 -m PyInstaller --onefile --windowed --name="OctopusFTP" main.py
if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "[3/3] Cleaning up..."
# Keep the executable, remove build artifacts
rm -rf build
rm -f OctopusFTP.spec

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Executable location: dist/OctopusFTP"
echo ""
echo "You can now:"
echo "  1. Run directly: ./dist/OctopusFTP"
echo "  2. Move to /usr/local/bin for system-wide access"
echo "  3. Create a desktop entry for your application menu"
echo "  4. Distribute to other Linux users (same architecture)"
echo ""
echo "Note: The executable is built for your CPU architecture"
echo "      (x86_64, ARM, etc.) - recipients need the same arch"
echo ""
