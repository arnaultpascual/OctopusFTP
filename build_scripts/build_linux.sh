#!/bin/bash

# OctopusFTP - Linux Build Script
# This script creates a standalone executable for Linux

echo "========================================"
echo "OctopusFTP - Linux Build Script"
echo "========================================"
echo ""

# Get project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-tk"
    echo "  Fedora/RHEL:   sudo dnf install python3 python3-pip python3-tkinter"
    echo "  Arch:          sudo pacman -S python python-pip tk"
    exit 1
fi

echo "[1/4] Installing build dependencies..."
python3 -m pip install --upgrade pip --quiet
python3 -m pip install pyinstaller pillow --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[2/4] Creating icon..."
cd build_scripts
python3 create_icon.py
if [ $? -ne 0 ]; then
    echo "Warning: Failed to create icon, continuing without custom icon"
fi

echo ""
echo "[3/4] Building executable..."
cd "$PROJECT_ROOT"

# Check if icon exists
ICON_PATH="$PROJECT_ROOT/build_scripts/assets/OctopusFTP.ico"
ICON_ARG=""
if [ -f "$ICON_PATH" ]; then
    echo "Using custom icon: $ICON_PATH"
    ICON_ARG="--icon=$ICON_PATH"
else
    echo "Warning: Icon not found, using default"
fi

python3 -m PyInstaller \
    --onefile \
    --windowed \
    --name="OctopusFTP" \
    --paths="$PROJECT_ROOT/lib" \
    --add-data="$PROJECT_ROOT/lib:lib" \
    --hidden-import=PIL._tkinter_finder \
    $ICON_ARG \
    main.py

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "[4/4] Cleaning up..."
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
