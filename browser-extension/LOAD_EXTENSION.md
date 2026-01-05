# Loading FinACCAI Browser Extension

## Quick Steps

1. **Open Extension Management Page**
   - Chrome: Navigate to `chrome://extensions/`
   - Edge: Navigate to `edge://extensions/`

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**
   - Click "Load unpacked" button
   - Navigate to and select the `browser-extension` folder
   - Click "Select Folder"

4. **Verify Installation**
   - You should see "FinACCAI Accessibility Checker" in your extensions list
   - The extension icon should appear in your browser toolbar

5. **Start Using**
   - Navigate to any webpage
   - Click the FinACCAI icon
   - Select WCAG level (A, AA, or AAA)
   - Click "Analyze Page"

## Optional: Enable AI/ML Features

To use full AI-powered analysis:

```bash
# In a separate terminal, start the API server
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
python api_server.py
```

The extension will automatically use AI features when the server is running.

## Troubleshooting

**Error: "Cannot load extension with file or directory name __pycache__"**
- Solution: Run `rm -rf browser-extension/__pycache__` to remove Python cache files

**Extension not appearing in toolbar**
- Solution: Pin the extension by clicking the puzzle piece icon → Pin FinACCAI

**"Analyze Page" button not working**
- Check browser console (F12) for errors
- Verify you're on a valid webpage (not chrome:// or edge:// pages)
- Try reloading the extension

For more help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
