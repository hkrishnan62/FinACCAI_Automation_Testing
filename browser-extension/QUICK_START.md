# Quick Start Guide

## 1. Start the API Server

The API server is **already running** on port 5000 with AI/ML features enabled.

Verify it's running:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{"service":"FinACCAI API","status":"healthy","version":"1.0.0"}
```

If not running, start it:
```bash
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
python api_server.py
```

## 2. Load the Extension

### Chrome/Edge:
1. Open `chrome://extensions/` (or `edge://extensions/`)
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select: `/workspaces/FinACCAI_Automation_Testing/browser-extension`
5. Extension should load without errors

### Verify Extension Loaded:
- Look for "FinACCAI" icon in browser toolbar
- No errors in extension management page
- Click icon to see popup

## 3. Test the Extension

### Quick Test with Test Page:

1. **Open test page in browser:**
   ```
   file:///workspaces/FinACCAI_Automation_Testing/browser-extension/test_page_full.html
   ```

2. **Click the FinACCAI extension icon**

3. **Select WCAG Level:** Choose A, AA, or AAA

4. **Click "Analyze Page"**

5. **Watch the progress:**
   - Analyzing page...
   - Highlighting issues...
   - Capturing screenshot...
   - Running AI analysis...
   - ✓ Full scan complete!

6. **Verify in popup:**
   - ✅ Screenshot preview visible
   - ✅ "🤖 AI/ML Status" shows features enabled
   - ✅ Quick checks summary displayed

7. **Click "View Full Report"**

8. **Verify report contains:**
   - ✅ Full screenshot with red-highlighted issues
   - ✅ "🤖 AI/ML Analysis" section
   - ✅ "💡 AI-Powered Recommendations"
   - ✅ "🔬 Explainable AI (XAI)"
   - ✅ Detailed issue breakdowns
   - ✅ NO "Client-side analysis" text

## 4. Test with Real Website

Try analyzing any website:
1. Navigate to `https://example.com` or any other site
2. Click extension icon
3. Analyze the page
4. View the full report

## 5. Troubleshooting

### "Backend API not available"
**Fix:** Start the API server (see step 1)

### "Client-side analysis" in report
**Fix:** API server not running or not accessible. Start it:
```bash
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
python api_server.py &
```

### Extension won't load
**Check for:**
- No `__pycache__` directories in extension folder
- Valid `manifest.json`
- All required files present

**Fix:**
```bash
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
# Remove any Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
# Reload extension in browser
```

### No screenshot in report
**Fix:**
- Refresh the page
- Analyze again
- Check browser console for errors

## What's Fixed

All three reported issues are now resolved:

1. ✅ **Full Screenshot** - Captures viewport with highlighted issues
2. ✅ **AI/ML Analysis** - Present when API server is running
3. ✅ **Server-Side Validation** - API server processes all requests

## Expected Test Results

### Test Page (test_page_full.html)
Should find approximately **9 issues:**
- 2 images without alt text
- 3 form inputs without labels
- 1 heading hierarchy violation
- 3 links with non-descriptive text

### Real Websites
Results will vary based on actual accessibility issues found.

## Need Help?

See detailed testing instructions in:
- `TESTING_GUIDE.md` - Comprehensive testing procedures
- `FIXES_SUMMARY.md` - Technical details of all fixes
- `README.md` - General extension documentation

## Server Logs

View server activity:
```bash
tail -f /tmp/api_server.log
```

Check screenshot debugging:
```bash
tail -f /tmp/screenshot_debug.log
```
