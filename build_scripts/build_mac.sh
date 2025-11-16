#!/bin/bash

# OctopusFTP - Mac Build Script
# This script creates a standalone application for macOS

echo "========================================"
echo "OctopusFTP - Mac Build Script"
echo "========================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
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
echo "[2/3] Building application..."
cd ..

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Build for Apple Silicon (arm64) or Intel (x86_64)
if [ "$ARCH" = "arm64" ]; then
    echo "Building for Apple Silicon (M1/M2/M3)..."
    python3 -m PyInstaller \
        --onedir \
        --windowed \
        --name="OctopusFTP" \
        --target-arch arm64 \
        --collect-all customtkinter \
        --collect-all darkdetect \
        --collect-all packaging \
        --hidden-import='PIL._tkinter_finder' \
        main.py
else
    echo "Building for Intel x86_64..."
    python3 -m PyInstaller \
        --onedir \
        --windowed \
        --name="OctopusFTP" \
        --collect-all customtkinter \
        --collect-all darkdetect \
        --collect-all packaging \
        --hidden-import='PIL._tkinter_finder' \
        main.py
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "[3/3] Cleaning up..."
# Keep the application, remove build artifacts
rm -rf build
rm -f OctopusFTP.spec

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Application location: dist/OctopusFTP.app"
echo ""
echo "You can now:"
echo "  1. Move OctopusFTP.app to your Applications folder"
echo "  2. Double-click to run"
echo "  3. Share with other Mac users (no Python required!)"
echo ""
echo "Note: On first run, you may need to right-click > Open"
echo "      to bypass macOS security (unsigned app)"
echo ""
