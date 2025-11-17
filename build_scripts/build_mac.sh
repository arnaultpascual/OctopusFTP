#!/bin/bash

# OctopusFTP - Mac Build Script
# This script creates a standalone application for macOS

echo "========================================"
echo "OctopusFTP - Mac Build Script"
echo "========================================"
echo ""

# Get project root (parent of build_scripts)
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Use virtual environment with Homebrew Python 3.12 (has modern Tcl/Tk 9.0)
VENV_DIR="$PROJECT_ROOT/build_env"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PYINSTALLER="$VENV_DIR/bin/pyinstaller"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "[0/4] Creating build environment with Homebrew Python 3.12..."
    if ! command -v /opt/homebrew/opt/python@3.12/bin/python3.12 &> /dev/null; then
        echo "ERROR: Homebrew Python 3.12 not found"
        echo "Please install it with: brew install python-tk@3.12"
        exit 1
    fi

    /opt/homebrew/opt/python@3.12/bin/python3.12 -m venv "$VENV_DIR"
    $VENV_PYTHON -m pip install --upgrade pip --quiet
    $VENV_PYTHON -m pip install pyinstaller pillow --quiet
    echo "✓ Build environment created"
    echo ""
fi

echo "Build Python: $VENV_PYTHON"
$VENV_PYTHON --version

echo ""
echo "[1/4] Creating icon..."
cd build_scripts
$VENV_PYTHON create_icon.py
if [ $? -ne 0 ]; then
    echo "Warning: Failed to create icon, continuing without custom icon"
fi

echo ""
echo "[2/4] Preparing build..."
cd "$PROJECT_ROOT"

echo ""
echo "[3/4] Building application..."

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Check if icon exists
ICON_PATH="$PROJECT_ROOT/build_scripts/assets/OctopusFTP.icns"
ICON_ARG=""
if [ -f "$ICON_PATH" ]; then
    echo "Using custom icon: $ICON_PATH"
    ICON_ARG="--icon=$ICON_PATH"
else
    echo "Warning: Icon not found at $ICON_PATH, using default"
fi

# Build with modern Tcl/Tk from Homebrew Python
echo "Building for $ARCH with modern Tcl/Tk 9.0..."

$VENV_PYINSTALLER \
    --windowed \
    --onedir \
    --name="OctopusFTP" \
    --paths="$PROJECT_ROOT/lib" \
    --add-data="$PROJECT_ROOT/lib:lib" \
    --hidden-import='PIL._tkinter_finder' \
    --osx-bundle-identifier com.octopusftp.app \
    --noconfirm \
    $ICON_ARG \
    main.py

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "[4/4] Cleaning up..."
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
