# 🔄 Extension Reload Instructions

The code has been updated to fix all three issues. Follow these steps to apply the changes:

## Steps to Reload the Extension

### 1. Open Extension Management Page
- **Chrome**: Go to `chrome://extensions/`
- **Edge**: Go to `edge://extensions/`
- **Brave**: Go to `brave://extensions/`

### 2. Enable Developer Mode
- Toggle the "Developer mode" switch in the top-right corner (if not already enabled)

### 3. Reload the Extension
- Find "FinACCAI Accessibility Checker" (version should now show 1.1.0)
- Click the **🔄 Reload** button (circular arrow icon)
- Or click **Remove** and then **Load unpacked** and select the `browser-extension` folder again

### 4. Verify the Backend Server is Running
Open a terminal and run:
```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{"service":"FinACCAI API","status":"healthy","version":"1.0.0"}
```

If not, start the server:
```bash
cd /workspaces/FinACCAI_Automation_Testing/browser-extension
python api_server.py
```

### 5. Test the Extension

1. Navigate to any website (e.g., https://www.google.com)
2. Click the FinACCAI extension icon
3. Select WCAG Level (AA or AAA)
4. Click **"Analyze Page"**
5. **Open the browser console** (F12 or Right-click → Inspect → Console tab)
6. Look for console messages starting with `[FinACCAI]`:
   - `[FinACCAI] API URL detected: http://localhost:5000/api/analyze`
   - `[FinACCAI] Screenshot captured, length: XXXXX`
   - `[FinACCAI] Backend response received: {...}`

### 6. Download and Check the Report

- Click **"Download Report"** button
- Open the downloaded HTML file
- Verify:
  - ✅ Screenshot is present at the top (red-highlighted errors)
  - ✅ Header shows "WCAG 2.1 Level [AA/AAA] with AI/ML Enhancement"
  - ✅ "🤖 AI/ML Analysis Results" section is present with:
    - NLP Analysis
    - ML Predictions
    - Explainable AI Recommendations

## Troubleshooting

### If backend is not being called:
1. Check console for `[FinACCAI] No API URL found`
2. Verify server is running: `curl http://localhost:5000/api/health`
3. Check browser console for CORS errors
4. Try reloading the extension again

### If screenshot is missing:
1. Check console for `[FinACCAI] Screenshot captured, length: 0`
2. Try on a simple page first (like Google)
3. Check if the page allows screenshots (some sites block it)

### If AI/ML section is missing:
1. Check if the report header says "Client-side analysis" (means backend wasn't used)
2. Verify server has AI/ML modules: The server log should show "✓ AI/ML modules loaded successfully"
3. Check server logs for errors

## What's Fixed

1. **Full Screenshot**: Now captures multiple viewports and includes the full top portion with highlighted errors
2. **AI/ML Analysis**: Complete AI/ML results section with NLP, ML predictions, and XAI recommendations
3. **Server Integration**: Properly connects to backend when available, includes all server-side validation results
