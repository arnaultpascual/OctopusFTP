#!/bin/bash
# OctopusFTP Launcher Script for macOS
# This script finds and uses a Python installation with working Tkinter

echo "🐙 Starting OctopusFTP..."
echo ""

# Function to test if Python + Tkinter + matplotlib works
test_python() {
    local python_cmd=$1
    if ! command -v "$python_cmd" &> /dev/null; then
        return 1
    fi

    # Try to import tkinter, matplotlib and create a window (tests if all dependencies work)
    if $python_cmd -c "import tkinter; import matplotlib; root = tkinter.Tk(); root.destroy()" 2>/dev/null; then
        return 0
    fi
    return 1
}

# Try build environment first (already has all dependencies)
BUILD_ENV_PYTHON="./build_env/bin/python"
if test_python "$BUILD_ENV_PYTHON"; then
    echo "✓ Using build environment Python (Recommended)"
    $BUILD_ENV_PYTHON main.py
    exit $?
fi

# Try Homebrew Python with python-tk@3.12 first (BEST for macOS - has Tk 9.0+)
# This is the recommended installation for modern macOS
BREW_PYTHON312="/opt/homebrew/opt/python@3.12/bin/python3.12"
if test_python "$BREW_PYTHON312"; then
    echo "✓ Using Homebrew Python 3.12 with Tkinter (Recommended)"
    $BREW_PYTHON312 main.py
    exit $?
fi

# Try regular Homebrew python3.12
if test_python "/opt/homebrew/bin/python3.12"; then
    echo "✓ Using Homebrew Python 3.12 with Tkinter"
    /opt/homebrew/bin/python3.12 main.py
    exit $?
fi

# Try regular Homebrew python3 (any version)
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

# No working Python+Tkinter+matplotlib found
echo "❌ ERROR: No Python installation with working Tkinter and matplotlib found"
echo ""
echo "OctopusFTP requires Python 3.8+ with Tkinter (Tcl/Tk) and matplotlib."
echo ""
echo "🔧 To fix this issue:"
echo ""
echo "Option 1: Install dependencies via Homebrew and pip (recommended for macOS)"
echo "  brew install python-tk@3.12"
echo "  /opt/homebrew/opt/python@3.12/bin/python3.12 -m pip install matplotlib"
echo ""
echo "Option 2: Build the environment automatically"
echo "  cd build_scripts"
echo "  ./build_mac.sh"
echo "  cd .."
echo "  ./run.sh"
echo ""
echo "Option 3: Download Python from python.org and install matplotlib"
echo "  https://www.python.org/downloads/"
echo "  pip install matplotlib"
echo ""
exit 1
