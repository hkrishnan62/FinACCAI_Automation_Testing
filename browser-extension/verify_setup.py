#!/usr/bin/env python3
"""
Verify the browser extension files are properly set up.
"""
import os
import json
import sys

def check_file(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} missing: {path}")
        return False

def main():
    print("FinACCAI Browser Extension - Setup Verification")
    print("=" * 50)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check all required files
    files_to_check = [
        ("manifest.json", "Extension manifest"),
        ("background.js", "Background service worker"),
        ("content.js", "Content script"),
        ("popup.html", "Popup HTML"),
        ("popup.css", "Popup styles"),
        ("popup.js", "Popup script"),
        ("api_server.py", "API server"),
        ("README.md", "Extension documentation"),
    ]
    
    icons_to_check = [
        "icons/icon16.png",
        "icons/icon32.png",
        "icons/icon48.png",
        "icons/icon128.png",
    ]
    
    all_good = True
    
    print("Core files:")
    for filename, description in files_to_check:
        path = os.path.join(base_dir, filename)
        if not check_file(path, description):
            all_good = False
    
    print()
    print("Icons:")
    for icon in icons_to_check:
        path = os.path.join(base_dir, icon)
        if not check_file(path, f"Icon {icon}"):
            all_good = False
    
    print()
    
    # Validate manifest.json
    manifest_path = os.path.join(base_dir, "manifest.json")
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            required_fields = ["manifest_version", "name", "version", "permissions"]
            print("Manifest validation:")
            for field in required_fields:
                if field in manifest:
                    print(f"  ✓ {field}: {manifest[field]}")
                else:
                    print(f"  ✗ Missing field: {field}")
                    all_good = False
        except json.JSONDecodeError as e:
            print(f"  ✗ Invalid JSON in manifest: {e}")
            all_good = False
    
    print()
    print("=" * 50)
    
    if all_good:
        print("✅ All checks passed! Extension is ready to load.")
        print()
        print("Next steps:")
        print("1. Open Chrome/Edge and go to chrome://extensions/")
        print("2. Enable 'Developer mode'")
        print("3. Click 'Load unpacked'")
        print(f"4. Select this folder: {base_dir}")
        print()
        print("Optional: Start the API server for full AI analysis:")
        print(f"  python {os.path.join(base_dir, 'api_server.py')}")
        return 0
    else:
        print("❌ Some files are missing. Run setup_extension.sh to fix.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
