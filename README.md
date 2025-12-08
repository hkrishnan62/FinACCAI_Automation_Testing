# Accessibility-2025
# FinAccAI – Accessibility Checker Prototype (Accessibility-2025)

## ✅ What is this project

**FinAccAI** is a Python-based prototype tool designed to help audit financial and other websites for basic web accessibility issues. It performs automated rule-based checks — such as missing image alt-text, unlabeled form inputs, low color contrast, and incorrect heading structure — and produces a visually-presentable HTML report summarizing all findings across one or more websites.  

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

