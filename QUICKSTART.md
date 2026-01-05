# FinACCAI - Quick Start Guide

## Two Ways to Use FinACCAI

### 1. 🔌 Browser Extension (NEW!)
**Best for**: Testing individual pages as you browse

**Setup (5 minutes):**
```bash
# 1. Install dependencies
./setup_extension.sh

# 2. Load extension in Chrome/Edge:
#    - Go to chrome://extensions/
#    - Enable "Developer mode"
#    - Click "Load unpacked"
#    - Select the browser-extension folder

# 3. Optional: Start API server for full AI analysis
python browser-extension/api_server.py
```

**Usage:**
1. Navigate to any webpage
2. Click the FinACCAI extension icon
3. Click "Analyze Page"
4. View instant results!

---

### 2. 📊 Batch Mode (Original)
**Best for**: Scanning multiple URLs, CI/CD pipelines

**Setup:**
```bash
# Install dependencies
pip install -r requirements.txt
```

**Usage:**
```bash
# Create a CSV with URLs (see websites.csv for example)
# Then run:
python finaccai.py --csv websites.csv

# Or use the package:
python -m finaccai --csv websites.csv
```

**Output:** HTML report in `log/` directory

---

## Feature Comparison

| Feature | Extension Mode | Batch Mode |
|---------|---------------|------------|
| Real-time testing | ✅ Yes | ❌ No |
| Bulk URL scanning | ❌ No | ✅ Yes |
| CI/CD integration | ❌ No | ✅ Yes |
| Instant results | ✅ Yes | ⏱️ Slower |
| AI analysis | ✅ Optional | ✅ Optional |
| Client-side checks | ✅ Yes | ✅ Yes |
| Zero setup testing | ✅ Yes | ❌ Needs CSV |

---

## What Gets Checked?

✅ **Images**: Missing/empty alt text  
✅ **Form Inputs**: Missing labels or ARIA attributes  
✅ **Color Contrast**: Insufficient contrast (inline CSS)  
✅ **Headings**: Incorrect heading hierarchy (h1-h6)  
✅ **Links**: Non-descriptive link text  
✅ **ARIA**: Missing accessible names for interactive elements  

With AI backend running:
- 🤖 ML-based issue prediction
- 📝 NLP content analysis
- 🔍 Explainable AI insights

---

## Troubleshooting

### Extension not working?
1. Refresh the page you're testing
2. Check extension is enabled
3. Look for errors in browser console (F12)

### "Backend API not available"?
- Start the API server: `python browser-extension/api_server.py`
- Extension works without it (client-side checks only)

### Batch mode errors?
- Check CSV has a `url` column
- Verify URLs are accessible
- Check network connectivity

---

## Getting Help

- Extension docs: `browser-extension/README.md`
- Main docs: `README.md`
- Run verification: `python browser-extension/verify_setup.py`

---

## Development & Customization

### Add custom checks
- Client-side: Edit `browser-extension/content.js`
- Backend: Edit `finaccai/script.py` or `finaccai/rule_checks.py`

### Customize reports
- Edit `finaccai/report_generator.py`

### API endpoints
- See `browser-extension/api_server.py`

---

**Happy Testing! 🎉**
