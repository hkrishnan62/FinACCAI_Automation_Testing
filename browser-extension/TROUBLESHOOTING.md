# Troubleshooting Guide - FinACCAI Browser Extension

## Common Issues and Solutions

### ❌ "Could not connect to page" Error

This is the most common issue. Here's how to fix it:

#### Solution 1: Refresh the Page
1. Refresh the webpage you're trying to analyze (press F5 or Ctrl+R)
2. Wait for the page to fully load
3. Click the extension icon and try again

#### Solution 2: Check Page Type
The extension cannot analyze:
- Browser internal pages (`chrome://`, `edge://`, `about:`)
- Extension pages (`chrome-extension://`)
- Local file URLs (`file://`) - unless you enable it in extension settings
- New Tab pages

**To test:** Navigate to a real website like `https://example.com` or use the included test page.

#### Solution 3: Reload the Extension
1. Go to `chrome://extensions/`
2. Find "FinACCAI Accessibility Checker"
3. Click the reload icon (🔄)
4. Go back to your webpage and refresh it
5. Try analyzing again

#### Solution 4: Check Permissions
1. Go to `chrome://extensions/`
2. Find "FinACCAI Accessibility Checker"
3. Click "Details"
4. Scroll to "Site access" and ensure it's set to:
   - "On all sites" (recommended) OR
   - "On click" (you'll need to click the extension icon and allow access each time)

#### Solution 5: Enable File URLs (if testing local HTML files)
1. Go to `chrome://extensions/`
2. Find "FinACCAI Accessibility Checker"
3. Click "Details"
4. Enable "Allow access to file URLs"

### 🧪 Testing the Extension

Use the included test page to verify the extension works:

**Method 1: Open as file**
```
file:///workspaces/FinACCAI_Automation_Testing/browser-extension/test_page.html
```
(Remember to enable file URL access first!)

**Method 2: Serve via Python**
```bash
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
python3 -m http.server 8080
```
Then open: `http://localhost:8080/test_page.html`

**Method 3: Test on a public website**
Navigate to any website like:
- https://example.com
- https://www.google.com
- https://github.com

### 🔍 Other Common Issues

#### Extension Icon Not Showing
1. Click the puzzle piece icon (🧩) in your browser toolbar
2. Find "FinACCAI Accessibility Checker"
3. Click the pin icon to pin it to your toolbar

#### No Results After Clicking "Analyze"
1. Open browser console (F12)
2. Look for any JavaScript errors
3. Check if the page has fully loaded
4. Try refreshing and analyzing again

#### "Backend API not available" Warning
This is normal if you haven't started the API server. The extension will still work with client-side checks only.

**To enable full AI analysis:**
```bash
python browser-extension/api_server.py
```

#### Extension Popup Closes Immediately
This is normal browser behavior. The popup stays open while you're interacting with it.

#### Results Look Wrong
1. Make sure you're on a regular webpage (not a browser internal page)
2. Wait for the page to fully load before analyzing
3. Try refreshing the page and analyzing again

### 📋 Quick Checklist

Before reporting a bug, please verify:
- [ ] I'm on a regular webpage (not chrome://, edge://, etc.)
- [ ] I've refreshed the webpage
- [ ] The extension is enabled in chrome://extensions/
- [ ] The extension has proper permissions
- [ ] I've reloaded the extension
- [ ] I've checked the browser console for errors (F12)

### 🔧 Debug Mode

To see detailed logging:
1. Open browser console (F12)
2. Go to the "Console" tab
3. Click the extension icon and analyze a page
4. Look for messages starting with "FinACCAI"

### 📞 Still Having Issues?

1. **Verify Setup:**
   ```bash
   cd /workspaces/FinACCAI_Automation_Testing/browser-extension
   python verify_setup.py
   ```

2. **Check Extension Files:**
   Make sure all these files exist:
   - manifest.json
   - background.js
   - content.js
   - popup.html
   - popup.js
   - popup.css
   - icons/ (folder with icon files)

3. **Test Basic Functionality:**
   - Open `test_page.html` in your browser
   - Click the extension icon
   - Click "Analyze Page"
   - You should see results within a few seconds

### 💡 Tips for Best Results

1. **Always refresh** the page after installing or updating the extension
2. **Wait for page load** - Don't click analyze until the page is fully loaded
3. **Use regular websites** - Browser internal pages won't work
4. **Check permissions** - Make sure the extension has access to the site
5. **Start simple** - Test on the included test_page.html first

### 🚀 Advanced: Manual Content Script Injection

If the content script isn't loading automatically, the extension now tries to inject it manually. If you still have issues:

1. Open browser console (F12)
2. Paste this code:
   ```javascript
   chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
     chrome.scripting.executeScript({
       target: {tabId: tabs[0].id},
       files: ['content.js']
     });
   });
   ```
3. Press Enter
4. Try the extension again

---

## Working Configuration Example

```
✓ Browser: Chrome 88+ or Edge 88+
✓ Page: https://example.com
✓ Extension: Loaded and enabled
✓ Permissions: "On all sites" or "On click"
✓ Status: Page loaded and ready
→ Click extension icon → Click "Analyze Page" → See results!
```

---

For more help, see:
- Main README: [../README.md](../README.md)
- Extension README: [README.md](README.md)
- Quick Start: [../QUICKSTART.md](../QUICKSTART.md)
