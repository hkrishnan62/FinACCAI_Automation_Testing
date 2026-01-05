# Accessibility Testing Automation — FinAccAI

FinAccAI is a Python-based accessibility testing prototype that performs automated, rule-based testing on websites to identify common WCAG-aligned accessibility issues. The tool is useful for QA engineers, accessibility auditors, and development teams who want a fast, lightweight assessment of baseline accessibility across one or more web applications.

**NEW**: Now available as a browser extension! Test any webpage in real-time with a single click. See the [Browser Extension](#browser-extension) section below.

[![Accessibility scan](https://github.com/hkrishnan62/Accessibility-2025/actions/workflows/scan.yml/badge.svg)](https://github.com/hkrishnan62/Accessibility-2025/actions/workflows/scan.yml)

---
## Architecture Overview
![FinAccAI Architecture](docs/FinACCAI_Architecture_Diagram_1.png)

## Key Capabilities ✅

- **🆕 Browser Extension** — Real-time accessibility testing as you browse
- **Batch URL Scanning** — Process multiple websites from CSV files
- **Model-driven analysis (optional)** — integrates ML/NLP/vision modules to supplement rule-based checks (image captioning, NLP context checks, and explainability outputs)

---

## Intended Use Cases

3. Applies rule-based accessibility checks and, optionally, model-driven ML/NLP/vision checks for supplementary findings
- QA validation before accessibility audits
- Regression checks in CI/CD pipelines
- Early identification of WCAG-related risks

### AI & ML features (experimental)

- **Vision captioning & image context:** optional modules can generate captions or detect decorative vs meaningful images to improve `alt` coverage checks.
- **NLP-assisted checks:** analyze surrounding text, labels, and form context to surface likely missing labels or semantic mismatches.
- **Explainability outputs:** XAI helpers provide human-readable rationale for model-driven flags so results remain auditable.
- **Opt-in & auditable:** model-driven checks are optional; they augment rule-based findings and are intended for research and CI augmentation, not as sole sources of truth.
## Prerequisites

- Python 3.7 or higher

- Experimental ML/NLP/vision modules included; model-driven checks are optional and intended for research/augmentation of rule-based results
Install dependencies:

```bash
pip install requests beautifulsoup4
```

---

## How it works (high-level)

1. Reads a CSV file containing website URLs (expects a `url` column)
2. Fetches HTML for each URL
3. Applies rule-based accessibility checks
4. Aggregates findings across sites
5. Writes a timestamped HTML report to `log/`

---

## Input format

CSV must contain a column named `url`, for example:

```csv
url
https://example.com
https://another-site.com
```

---

## Running the tool

Recommended: create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the scanner as a package (recommended):

```bash
python -m finaccai --csv websites.csv
```

A backwards-compatible wrapper is provided, so you can also run:

```bash
python finaccai.py --csv websites.csv
```

Output: a timestamped HTML report saved under `log/`, e.g. `log/accessibility_report_YYYY-MM-DD_HHMMSS.html`.

---

## Project structure

- `finaccai/` — package modules
  - `finaccai/script.py` — core scanner functions (fetching, checks, report generation, CSV handling)
  - `finaccai/cli.py` — CLI entrypoint (`main()`)
  - `finaccai/__main__.py` — package entry so `python -m finaccai` works
- `finaccai.py` — lightweight wrapper delegating to the package CLI (backwards compatibility)
- `tests/` — test suite (includes a smoke test to ensure pytest finds at least one test)
- `models/` — large model artifacts (tracked with Git LFS)
- `log/` — generated HTML reports
- `browser-extension/` — browser extension for real-time testing

---

## Browser Extension

FinACCAI is now available as a browser extension for Chrome and Edge! Test any webpage in real-time without leaving your browser.

### Quick Setup

1. **Install dependencies:**
   ```bash
   ./setup_extension.sh
   ```

2. **Load the extension:**
   - Open Chrome/Edge and navigate to `chrome://extensions/` (or `edge://extensions/`)
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `browser-extension` folder

3. **Start the API server (optional but recommended):**
   ```bash
   python browser-extension/api_server.py
   ```

4. **Use the extension:**
   - Navigate to any webpage
   - Click the FinACCAI extension icon
   - Click "Analyze Page"
   - View instant results and detailed reports

### Extension Features

- ✅ **Instant Client-Side Checks**: Fast accessibility checks without backend
- ✅ **AI-Powered Analysis**: Optional ML/NLP analysis when backend is running
- ✅ **Visual Reports**: Beautiful, detailed HTML reports
- ✅ **Export Options**: Download reports for sharing
- ✅ **Zero Configuration**: Works immediately for basic checks

For detailed extension documentation, see [browser-extension/README.md](browser-extension/README.md).

---

## Models & Git LFS

Large model files (e.g. `.safetensors`) are tracked using Git LFS and are not stored directly in Git history. After cloning the repository, fetch the LFS objects:

```bash
git lfs install
git lfs pull
```

Do not commit raw model files directly; either add them to `.gitignore` or host externally (Hugging Face, S3, etc.).

---

## Running tests & CI

Run unit tests locally:

```bash
pip install pytest
python -m pytest --maxfail=1 --disable-warnings -q
```

The GitHub Actions workflow installs `pytest` before running tests and a small smoke test is included so the job does not fail with "no tests ran".

---

## CI/CD Compatibility

FinAccAI is CI-friendly and can be integrated into pipelines. This repository includes a GitHub Actions workflow (`.github/workflows/scan.yml`) that runs the scanner and uploads generated reports as workflow artifacts.

---

## Project status & scope

- Rule-based checks only (no headless browser or JS execution)
- Color contrast limited to inline CSS hex colors
- Static HTML analysis (no JS-rendered DOM at this time)
- Prototype / research focus

**Future enhancements (examples):** CSS file parsing, ARIA role validation, JavaScript DOM rendering support, accessibility scoring metrics.

## Why choose FinAccAI over Wave and Axe

- **Bulk, multi-site scanning:** FinAccAI accepts CSV input to scan many sites in one run and produce aggregated reports. Wave (a browser extension) and Axe (a page-by-page library/extension) are primarily focused on single-page or interactive testing.
- **CI/CD & automation friendly:** FinAccAI is a CLI-first Python tool designed to run in pipelines and produce timestamped HTML artifacts suitable for archival and automation.
- **Lightweight, scriptable, and transparent:** Implemented in Python with rule logic in plain code, making it easy to customize checks, extend rules, and integrate with existing Python tooling and data workflows.
- **Team-ready reporting:** Generates consistent HTML reports saved under `log/` for sharing, tracking regressions, and attaching to CI runs—useful for audits and batch reviews.
- **Extensible with model/XAI modules:** The project contains modules for model-driven analysis and explainability (where applicable), enabling research workflows that go beyond single-page, manual inspections.
- **Complements, not replaces, manual & browser-based testing:** Wave and Axe are excellent for in-browser, interactive, and DOM-level analysis; FinAccAI is complementary for fast baseline scans, batch auditing, and CI integration.

## License & usage

This project is provided for research, education, and evaluation. Feel free to adapt and extend the framework for your own accessibility workflows.  

This project targets web developers, accessibility auditors, QA teams, or anyone who needs to quickly gauge accessibility compliance on a set of URLs.  

---

## 📄 Features & What It Checks

- Detects `<img>` tags missing or having empty `alt` attributes  
- Identifies `<input>` fields without a corresponding `<label>` or `aria-label` / `aria-labelledby`  
- Detects inline-styled text elements with insufficient color contrast (hex colors only)  
- Checks for heading structure consistency: warns if heading levels are skipped (e.g., `<h1>` → `<h3>`)  
- Supports scanning multiple websites listed in a CSV file  
- Generates a clean, styled HTML report (saved under `log/`) with summary and per-site issue breakdown  

---

## 🧰 Prerequisites

- Python 3.7 or above  
- `requests` library  
- `beautifulsoup4` (bs4) library  

You can install required dependencies via:

```bash
pip install requests beautifulsoup4

