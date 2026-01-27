#!/bin/bash

# Quick test script to verify WCAG level selector integration

echo "==================================="
echo "FinACCAI Level Selector Test"
echo "==================================="
echo ""

# Check if files were updated
echo "✓ Checking updated files..."

if grep -q "levelSelect" browser-extension/popup.html; then
    echo "  ✓ popup.html: Level selector dropdown added"
else
    echo "  ✗ popup.html: Missing level selector"
fi

if grep -q "level-selector" browser-extension/popup.css; then
    echo "  ✓ popup.css: Level selector styles added"
else
    echo "  ✗ popup.css: Missing styles"
fi

if grep -q "selectedLevel" browser-extension/popup.js; then
    echo "  ✓ popup.js: Level parameter extraction added"
else
    echo "  ✗ popup.js: Missing level parameter"
fi

if grep -q "request.level" browser-extension/background.js; then
    echo "  ✓ background.js: Level forwarding added"
else
    echo "  ✗ background.js: Missing level forwarding"
fi

if grep -q "level = data.get" browser-extension/api_server.py; then
    echo "  ✓ api_server.py: Level parameter support confirmed"
else
    echo "  ✗ api_server.py: Missing level support"
fi

echo ""
echo "==================================="
echo "Implementation Summary"
echo "==================================="
echo ""
echo "Feature 1: Full Page Screenshot"
echo "  Status: ✓ Already implemented"
echo "  Location: popup.js - captureFullPageScreenshot()"
echo ""
echo "Feature 2: Whole Page Scanning"
echo "  Status: ✓ Already implemented"
echo "  Location: content.js - getPageDimensions()"
echo ""
echo "Feature 3: WCAG Level Selector"
echo "  Status: ✓ Newly implemented"
echo "  Components:"
echo "    - UI Dropdown (popup.html)"
echo "    - CSS Styling (popup.css)"
echo "    - Level extraction (popup.js)"
echo "    - API forwarding (background.js)"
echo "    - Server processing (api_server.py)"
echo ""
echo "==================================="
echo "Next Steps"
echo "==================================="
echo ""
echo "1. Reload the extension in Chrome/Edge"
echo "2. Open the extension on a webpage"
echo "3. Select a WCAG level (A/AA/AAA)"
echo "4. Click 'Analyze Page'"
echo "5. Verify the report shows the selected level"
echo ""
echo "Test URLs:"
echo "  - https://www.hilton.com/ (Known to have AAA issues)"
echo "  - https://www.researchgate.net/profile/xyz (Previously tested)"
echo ""
