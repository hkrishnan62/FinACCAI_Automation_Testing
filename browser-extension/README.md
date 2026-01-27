# FinACCAI Browser Extension

A powerful browser extension for real-time accessibility testing powered by AI and ML models.

## Features

- **Real-time Analysis**: Analyze any webpage with a single click
- **Client-Side Checks**: Instant accessibility checks performed directly in the browser
- **AI-Powered Analysis**: Deep analysis using NLP and ML models (requires backend)
- **Comprehensive Reports**: Detailed HTML reports with explanations and recommendations
- **Multiple Check Types**:
  - Image alt text validation
  - Form input labeling
  - Color contrast issues
  - Heading hierarchy
  - Link accessibility
  - ARIA attribute validation

## Installation

### Prerequisites

1. **Python Backend** (for full AI analysis):
   ```bash
   pip install -r requirements.txt
   pip install flask flask-cors
   ```

2. **Chrome or Edge Browser** (Chromium-based)

### Step 1: Install the Extension

#### Chrome/Edge:
1. Open your browser and navigate to:
   - Chrome: `chrome://extensions/`
   - Edge: `edge://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Navigate to and select the `browser-extension` folder

### Step 2: Start the API Server (Optional but Recommended)

For full AI-powered analysis, start the backend API server:

```bash
cd /workspaces/FinACCAI_Automation_Testing
python browser-extension/api_server.py
```

The server will start on `http://localhost:5000`

**Note**: The extension works without the backend but will only perform client-side checks. For full analysis including ML/NLP predictions and detailed reports, the backend server must be running.

## Usage

### Quick Start

1. Navigate to any webpage you want to test
2. Click the FinACCAI extension icon in your browser toolbar
3. Click the "Analyze Page" button
4. Wait for the analysis to complete
5. Review the results in the popup
6. Click "View Full Report" for detailed findings

### Understanding Results

#### Quick Checks (Client-Side)
These checks run instantly in your browser:
- **Missing Alt Text**: Images without alternative text
- **Unlabeled Inputs**: Form fields without proper labels
- **Heading Hierarchy**: Problems with heading structure (h1-h6)
- **Link Issues**: Links with non-descriptive text
- **ARIA Issues**: Problems with ARIA attributes

#### AI Analysis (Backend Required)
When the backend is running, you also get:
- **ML Predictions**: Machine learning-based issue detection
- **NLP Analysis**: Natural language processing for content analysis
- **XAI Explanations**: Explainable AI insights
- **Vision Analysis**: Screenshot-based visual checks

### Viewing Reports

- **In-Browser**: Click "View Full Report" to open the detailed HTML report
- **Download**: Click "Download Report" to save the report locally
- Reports are stored in: `browser-extension/reports/`

## Dual Mode Operation

FinACCAI now supports two modes:

### 1. Extension Mode (Real-time)
- Click the extension icon to analyze the current page
- Instant client-side checks
- Optional backend for AI analysis

### 2. Batch Mode (Original)
- Use the command-line interface for bulk scanning
- Process multiple URLs from CSV
- Automated reporting

```bash
# Batch mode usage
python finaccai.py --csv websites.csv
```

## Architecture

```
┌─────────────────┐
│  Browser Page   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Content  │ ← Performs client-side checks
    │ Script   │
    └────┬─────┘
         │
    ┌────▼─────┐
    │  Popup   │ ← User interface
    │   UI     │
    └────┬─────┘
         │
    ┌────▼─────┐
    │Background│ ← Manages API calls
    │ Service  │
    └────┬─────┘
         │
         │ HTTP POST
         ▼
┌──────────────────┐
│   Flask API      │ ← Backend server (optional)
│   (port 5000)    │
└────────┬─────────┘
         │
    ┌────▼─────┐
    │ FinACCAI │ ← ML/NLP/Vision analysis
    │  Engine  │
    └──────────┘
```

## Troubleshooting

### Extension Not Working
1. Refresh the page you're trying to analyze
2. Check that the extension is enabled in your browser
3. Look for errors in the browser console (F12)

### "Backend API not available"
1. Make sure you've started the API server: `python browser-extension/api_server.py`
2. Check that the server is running on port 5000
3. Verify no firewall is blocking localhost:5000
4. The extension will still show client-side checks

### No Results Showing
1. Wait a few seconds - analysis may take time
2. Check the browser console for JavaScript errors
3. Ensure the page has fully loaded before clicking "Analyze Page"

### CORS Errors
The API server uses Flask-CORS to allow requests from the extension. If you see CORS errors:
1. Make sure `flask-cors` is installed: `pip install flask-cors`
2. Check that the API server started successfully

## Development

### Project Structure
```
browser-extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker
├── content.js            # Page analysis script
├── popup.html            # Extension UI
├── popup.css             # UI styling
├── popup.js              # UI logic
├── api_server.py         # Backend API
├── icons/                # Extension icons
└── reports/              # Generated reports
```

### Adding New Checks

#### Client-Side Check
Edit `content.js` and add to `performClientSideChecks()`:

```javascript
// Example: Check for table headers
document.querySelectorAll('table').forEach((table, index) => {
  const hasTh = table.querySelector('th');
  if (!hasTh) {
    issues.tables.push({
      index: index,
      message: 'Table has no header cells'
    });
  }
});
```

#### Backend Check
Edit `finaccai/script.py` or `finaccai/rule_checks.py`:

```python
def check_tables(soup):
    """Check tables for accessibility."""
    issues = []
    for table in soup.find_all('table'):
        if not table.find('th'):
            issues.append("Table missing header cells")
    return issues
```

## Requirements

### Python Dependencies
```
beautifulsoup4
requests
flask
flask-cors
transformers
torch
Pillow
```

### Browser Requirements
- Chrome 88+ or Edge 88+
- Manifest V3 support

## License

Same as the main FinACCAI project.

## Support

For issues or questions:
1. Check this README first
2. Look at the main project documentation
3. File an issue on the GitHub repository

## Changelog

### Version 1.0.0
- Initial release
- Client-side accessibility checks
- Backend AI integration
- HTML report generation
- Chrome/Edge support
