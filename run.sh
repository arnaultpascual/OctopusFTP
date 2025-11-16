#!/bin/bash
# OctopusFTP Launcher Script for macOS
# This script finds and uses a Python installation with working Tkinter

echo "🐙 Starting OctopusFTP..."
echo ""

# Function to test if Python + Tkinter works
test_python() {
    local python_cmd=$1
    if ! command -v "$python_cmd" &> /dev/null; then
        return 1
    fi

    # Try to import tkinter and create a window (tests if Tk actually works)
    if $python_cmd -c "import tkinter; root = tkinter.Tk(); root.destroy()" 2>/dev/null; then
        return 0
    fi
    return 1
}

# Try Homebrew Python with python-tk@3.12 first (best for modern macOS)
# Check keg-only installation first
BREW_PYTHON312="/opt/homebrew/opt/python@3.12/bin/python3.12"
if test_python "$BREW_PYTHON312"; then
    echo "✓ Using Homebrew Python 3.12 with Tkinter"
    $BREW_PYTHON312 main.py
    exit $?
fi

# Try regular Homebrew python3.12
if test_python "/opt/homebrew/bin/python3.12"; then
    echo "✓ Using Homebrew Python 3.12 with Tkinter"
    /opt/homebrew/bin/python3.12 main.py
    exit $?
fi

# Try regular Homebrew python3
if test_python "/opt/homebrew/bin/python3"; then
    echo "✓ Using Homebrew Python with Tkinter"
    /opt/homebrew/bin/python3 main.py
    exit $?
fi

# Try python3 from PATH
if test_python "python3"; then
    echo "✓ Using Python 3 with Tkinter"
    python3 main.py
    exit $?
fi

# Try system Python (may have Tk version issues on newer macOS)
if test_python "/usr/bin/python3"; then
    echo "⚠️  Using system Python (may have Tk issues on macOS Sequoia)"
    /usr/bin/python3 main.py
    exit $?
fi

# No working Python+Tkinter found
echo "❌ ERROR: No Python installation with working Tkinter found"
echo ""
echo "OctopusFTP requires Python 3.8+ with Tkinter (Tcl/Tk) support."
echo ""
echo "🔧 To fix this issue:"
echo ""
echo "Option 1: Install Python with Tkinter via Homebrew (recommended for macOS)"
echo "  brew install python-tk@3.12"
echo ""
echo "Option 2: Download Python from python.org"
echo "  https://www.python.org/downloads/"
echo "  (Make sure to install the macOS installer, not just the framework)"
echo ""
echo "Option 3: Use PyInstaller to build a standalone app"
echo "  cd build_scripts"
echo "  ./build_mac.sh"
echo ""
exit 1
