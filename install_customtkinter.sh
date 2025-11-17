#!/bin/bash
# Install customtkinter for Homebrew Python

echo "🐙 Installing CustomTkinter for OctopusFTP..."
echo ""

# Find Homebrew Python
PYTHON_BIN="/opt/homebrew/opt/python@3.12/bin/python3.12"

if [ ! -f "$PYTHON_BIN" ]; then
    echo "❌ Homebrew Python 3.12 not found!"
    echo "Please install it first: brew install python-tk@3.12"
    exit 1
fi

echo "✓ Found Homebrew Python: $PYTHON_BIN"
echo ""

# Download customtkinter files directly into project
echo "📥 Downloading CustomTkinter..."

# Create lib directory
mkdir -p lib

# Download customtkinter package
cd lib
if [ ! -d "customtkinter" ]; then
    echo "Downloading from GitHub..."
    curl -L "https://github.com/TomSchimansky/CustomTkinter/archive/refs/heads/master.zip" -o ctk.zip
    unzip -q ctk.zip
    mv CustomTkinter-master/customtkinter .
    rm -rf CustomTkinter-master ctk.zip
    echo "✓ CustomTkinter downloaded"
else
    echo "✓ CustomTkinter already exists"
fi

# Download darkdetect
if ! $PYTHON_BIN -c "import darkdetect" 2>/dev/null; then
    echo "Installing darkdetect..."
    $PYTHON_BIN -m pip install --user --break-system-packages darkdetect packaging 2>/dev/null || true
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Run OctopusFTP with: ./run.sh"
