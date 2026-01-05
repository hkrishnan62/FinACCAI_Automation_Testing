#!/bin/bash
# Setup script for FinACCAI Browser Extension

echo "==================================="
echo "FinACCAI Browser Extension Setup"
echo "==================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Generate icons if they don't exist
if [ ! -d "browser-extension/icons" ]; then
    echo "🎨 Generating extension icons..."
    python3 browser-extension/generate_icons.py
    echo "✓ Icons generated"
else
    echo "✓ Icons already exist"
fi
echo ""

echo "==================================="
echo "✅ Setup Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Install the browser extension:"
echo "   - Open Chrome/Edge and go to extensions page"
echo "   - Enable 'Developer mode'"
echo "   - Click 'Load unpacked'"
echo "   - Select the 'browser-extension' folder"
echo ""
echo "2. Start the API server (optional but recommended):"
echo "   python browser-extension/api_server.py"
echo ""
echo "3. Or continue using the batch mode:"
echo "   python finaccai.py --csv websites.csv"
echo ""
echo "For more information, see browser-extension/README.md"
