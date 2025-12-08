#!/usr/bin/env python3
"""
FinAccAI Accessibility Checker: HTML Report Version
---------------------------------------------------
This version generates a visually rich HTML report and stores it inside /logs folder.

Usage:
    python finaccai_html_report.py --file test.html
    python finaccai_html_report.py --url https://example.com

Requires:
    pip install requests beautifulsoup4
"""

import argparse
import os
import json
import re
import sys
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# ----------------------------------------
# FETCH HTML (URL or local file)
# ----------------------------------------
def get_html(source, is_url):
    if is_url:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching URL {source}: {e}")
            sys.exit(1)
    else:
        try:
            with open(source, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            sys.exit(1)

# ----------------------------------------
# CHECKERS
# ----------------------------------------
def check_images(soup):
    issues = []
    for img in soup.find_all('img'):
        alt = img.get('alt')
        if alt is None or alt.strip() == "":
            issues.append(str(img))
    return issues

def check_inputs(soup):
    issues = []
    labels_for = {lab.get("for") for lab in soup.find_all("label")}
    for inp in soup.find_all("input"):
        input_id = inp.get("id")
        has_label = False

        if input_id and input_id in labels_for:
            has_label = True

        if inp.get("aria-label") or inp.get("aria-labelledby"):
            has_label = True

        input_type = inp.get("type", "").lower()
        if input_type in ["hidden", "submit", "button", "reset"]:
            has_label = True

        if not has_label:
            issues.append(str(inp))
    return issues

def parse_color(c):
    c = c.strip().lower()
    if c.startswith("#"):
        hex_val = c[1:]
        if len(hex_val) == 3:
            hex_val = ''.join([ch*2 for ch in hex_val])
        if len(hex_val) == 6:
            try:
                return (
                    int(hex_val[0:2], 16) / 255.0,
                    int(hex_val[2:4], 16) / 255.0,
                    int(hex_val[4:6], 16) / 255.0,
                )
            except:
                return None
    return None

def rel_lum(r, g, b):
    def adjust(c):
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*adjust(r) + 0.7152*adjust(g) + 0.0722*adjust(b)

def contrast_ratio(l1, l2):
    return (max(l1, l2)+0.05) / (min(l1, l2)+0.05)

def check_contrast(soup):
    issues = []
    style_color = re.compile(r"color\s*:\s*([^;]+)")
    style_bg = re.compile(r"background-color\s*:\s*([^;]+)")

    for elem in soup.find_all(style=True):
        style = elem["style"]

        c = style_color.search(style)
        b = style_bg.search(style)

        if c and b:
            fg = parse_color(c.group(1))
            bg = parse_color(b.group(1))

            if fg and bg:
                lum1 = rel_lum(*fg)
                lum2 = rel_lum(*bg)
                ratio = contrast_ratio(lum1, lum2)

                if ratio < 4.5:
                    issues.append(f"{elem.text} | Style: {style} | Ratio: {ratio:.2f}")

    return issues

def check_headings(soup):
    issues = []
    last = 0
    for h in soup.find_all(["h1","h2","h3","h4","h5","h6"]):
        level = int(h.name[1])
        if last != 0 and level > last + 1:
            issues.append(f"{h.text.strip()} (Found <h{level}> after <h{last}>)")
        last = level
    return issues

# ----------------------------------------
# GENERATE HTML REPORT
# ----------------------------------------
def generate_html_report(results, target_name):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"logs/report_{timestamp}.html"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<title>FinAccAI Accessibility Report</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<style>
body {{ padding: 20px; }}
.issue-block {{ margin-bottom: 30px; }}
pre {{ background: #f8f9fa; padding: 10px; border-radius: 5px; }}
</style>
</head>

<body>
<h1 class="text-primary">FinAccAI Accessibility Report</h1>
<h4>Target Scanned: {target_name}</h4>
<h6>Generated: {timestamp}</h6>
<hr>

<div class="issue-block">
<h3>1. Images Missing ALT</h3>
<p>Total: {len(results['images_missing_alt'])}</p>
<pre>{json.dumps(results['images_missing_alt'], indent=2)}</pre>
</div>

<div class="issue-block">
<h3>2. Inputs Missing Labels</h3>
<p>Total: {len(results['inputs_missing_label'])}</p>
<pre>{json.dumps(results['inputs_missing_label'], indent=2)}</pre>
</div>

<div class="issue-block">
<h3>3. Low Color Contrast Issues</h3>
<p>Total: {len(results['low_contrast'])}</p>
<pre>{json.dumps(results['low_contrast'], indent=2)}</pre>
</div>

<div class="issue-block">
<h3>4. Heading Structure Issues</h3>
<p>Total: {len(results['heading_issues'])}</p>
<pre>{json.dumps(results['heading_issues'], indent=2)}</pre>
</div>

<hr>
<p class="text-center text-muted">FinAccAI Prototype © {datetime.now().year}</p>

</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✔ HTML Report Generated: {filename}\n")
    return filename

# ----------------------------------------
# MAIN
# ----------------------------------------
def run_checks(html):
    soup = BeautifulSoup(html, "html.parser")
    return {
        "images_missing_alt": check_images(soup),
        "inputs_missing_label": check_inputs(soup),
        "low_contrast": check_contrast(soup),
        "heading_issues": check_headings(soup)
    }

def main():
    parser = argparse.ArgumentParser(description="FinAccAI HTML Accessibility Checker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="Scan a live URL")
    group.add_argument("--file", help="Scan a local HTML file")
    args = parser.parse_args()

    if args.url:
        html = get_html(args.url, True)
        results = run_checks(html)
        generate_html_report(results, args.url)

    elif args.file:
        html = get_html(args.file, False)
        results = run_checks(html)
        generate_html_report(results, args.file)

if __name__ == "__main__":
    main()
