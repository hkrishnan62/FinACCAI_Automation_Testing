#!/usr/bin/env python3
"""
FinAccAI Accessibility Checker (CSV + HTML Report Version)

Features:
- Reads a CSV file containing website URLs (expects a 'url' column).
- For each URL, fetches the HTML and runs basic accessibility checks:
    * Missing alt text on <img>
    * <input> fields without <label> or aria-label
    * Low color contrast (inline styles only; hex colors)
    * Heading structure issues (skipped heading levels)
- Generates a visually presentable HTML report in a 'log' folder.

Usage:
    python finaccai.py --csv sites.csv

Run in CI: the included GitHub Actions workflow executes the scanner and uploads `log/` HTML reports as artifacts.

CSV format:
    url
    https://example.com
    https://another-site.com

Dependencies:
    pip install requests beautifulsoup4
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime

import requests
from bs4 import BeautifulSoup


# -------------------------
# HTML / network utilities
# -------------------------

def get_html(url):
    """Fetch HTML from a URL. Returns (html_text, error_message)."""
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.text, None
    except Exception as e:
        return None, str(e)


# -------------------------
# Accessibility checks
# -------------------------

def check_images(soup):
    """Check for <img> elements missing alt text."""
    issues = []
    for img in soup.find_all('img'):
        alt = img.get('alt')
        if alt is None or alt.strip() == '':
            snippet = str(img)[:200].replace('\n', ' ')
            issues.append(f"Image with missing/empty alt: {snippet}...")
    return issues


def check_inputs(soup):
    """Check for <input> fields without a label or accessible name."""
    issues = []

    # All labels with 'for'
    labels_for = {
        label.get('for'): label.get_text().strip()
        for label in soup.find_all('label') if label.get('for')
    }

    # Inputs wrapped inside a label
    wrapped_ids = set()
    for label in soup.find_all('label'):
        inp = label.find('input')
        if inp and inp.get('id'):
            wrapped_ids.add(inp.get('id'))

    for inp in soup.find_all('input'):
        input_id = inp.get('id')
        has_label = False

        # Explicit for="id"
        if input_id and input_id in labels_for:
            has_label = True

        # Wrapped in a <label>
        if input_id and input_id in wrapped_ids:
            has_label = True

        # aria-label / aria-labelledby
        if inp.get('aria-label') or inp.get('aria-labelledby'):
            has_label = True

        # Skip some non-user-input types
        input_type = (inp.get('type') or '').lower()
        if input_type in ['hidden', 'submit', 'button', 'image', 'reset']:
            has_label = True

        if not has_label:
            snippet = str(inp)[:200].replace('\n', ' ')
            issues.append(f"Input without label/aria-label: {snippet}...")
    return issues


def parse_color(color_str):
    """Convert a CSS color (#RGB or #RRGGBB) to an (R,G,B) tuple of floats 0–1."""
    color_str = color_str.strip().lower()
    if not color_str.startswith('#'):
        return None
    hex_val = color_str[1:]
    if len(hex_val) == 3:
        hex_val = ''.join([c * 2 for c in hex_val])
    if len(hex_val) != 6:
        return None
    try:
        r = int(hex_val[0:2], 16) / 255.0
        g = int(hex_val[2:4], 16) / 255.0
        b = int(hex_val[4:6], 16) / 255.0
        return (r, g, b)
    except ValueError:
        return None


def rel_luminance(r, g, b):
    """Compute relative luminance for sRGB values (0–1)."""
    def f(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast_ratio(l1, l2):
    """Compute WCAG contrast ratio given two luminances."""
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_contrast(soup):
    """
    Check inline styles for color contrast issues.
    Only handles hex colors in 'color' and 'background-color'.
    """
    issues = []
    color_prop = re.compile(r'color\s*:\s*([^;]+)', re.IGNORECASE)
    bg_prop = re.compile(r'background-color\s*:\s*([^;]+)', re.IGNORECASE)

    for elem in soup.find_all(style=True):
        style = elem['style']
        color_match = color_prop.search(style)
        bg_match = bg_prop.search(style)
        if color_match and bg_match:
            fg = parse_color(color_match.group(1))
            bg = parse_color(bg_match.group(1))
            if fg and bg:
                l1 = rel_luminance(*fg)
                l2 = rel_luminance(*bg)
                ratio = contrast_ratio(l1, l2)
                if ratio < 4.5:
                    text = elem.get_text(strip=True)
                    short_text = (text[:80] + '...') if len(text) > 80 else text
                    issues.append(
                        f"Low contrast (ratio {ratio:.2f}) for text: '{short_text}' | style='{style}'"
                    )
    return issues


def check_headings(soup):
    """Check heading tags for skipped levels (e.g. h1 -> h3)."""
    issues = []
    heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    last_level = 0

    for tag in soup.find_all(heading_tags):
        level = int(tag.name[1])
        if last_level and level > last_level + 1:
            text = tag.get_text(strip=True)
            issues.append(
                f"Skipped heading level: <{tag.name}> follows <h{last_level}> | text='{text}'"
            )
        last_level = level
    return issues


def run_checks(html_content):
    """Run all checks on HTML content and return a dict of issues."""
    soup = BeautifulSoup(html_content, 'html.parser')
    issues = {
        'images_missing_alt': check_images(soup),
        'inputs_missing_label': check_inputs(soup),
        'low_contrast': check_contrast(soup),
        'heading_issues': check_headings(soup),
    }
    return issues


# -------------------------
# Report generation
# -------------------------

def generate_html_report(results_by_site, output_path):
    """
    Generate a single HTML report for all scanned sites.

    results_by_site: list of dicts:
        {
          "url": str,
          "title": str or None,
          "error": str or None,
          "issues": {category: [str, ...]}
        }
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_sites = len(results_by_site)
    sites_with_errors = sum(1 for r in results_by_site if r.get("error"))
    sites_with_issues = sum(
        1 for r in results_by_site
        if not r.get("error") and any(r["issues"].get(k) for k in r["issues"])
    )

    html_parts = []

    html_parts.append("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>FinAccAI Accessibility Report</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f5f5f5;
      margin: 0;
      padding: 0;
    }
    header {
      background: #003366;
      color: white;
      padding: 20px;
    }
    header h1 {
      margin: 0 0 10px 0;
      font-size: 24px;
    }
    header p {
      margin: 4px 0;
      font-size: 14px;
    }
    .container {
      max-width: 1200px;
      margin: 20px auto;
      padding: 0 15px 30px 15px;
    }
    .summary {
      background: white;
      border-radius: 8px;
      padding: 15px 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .summary span {
      display: inline-block;
      margin-right: 20px;
      font-size: 14px;
    }
    .card {
      background: white;
      border-radius: 8px;
      padding: 15px 20px;
      margin-bottom: 20px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    .card h2 {
      margin-top: 0;
      font-size: 18px;
      word-break: break-all;
    }
    .url {
      font-size: 13px;
      color: #555;
      margin-bottom: 5px;
    }
    .status-ok {
      color: #1b5e20;
      font-weight: bold;
    }
    .status-error {
      color: #b71c1c;
      font-weight: bold;
    }
    .tag {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 11px;
      margin-right: 6px;
    }
    .tag-issues {
      background: #ffebee;
      color: #c62828;
    }
    .tag-ok {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .tag-error {
      background: #fff3e0;
      color: #ef6c00;
    }
    h3 {
      margin-top: 15px;
      font-size: 15px;
      border-bottom: 1px solid #eee;
      padding-bottom: 4px;
    }
    ul {
      margin-top: 5px;
      padding-left: 18px;
      font-size: 13px;
    }
    li {
      margin-bottom: 4px;
    }
    .no-issues {
      font-size: 13px;
      color: #2e7d32;
      font-weight: bold;
    }
    footer {
      text-align: center;
      font-size: 11px;
      color: #777;
      padding: 10px 0 20px 0;
    }
  </style>
</head>
<body>
<header>
  <h1>FinAccAI Accessibility Report</h1>
  <p>Generated: """ + now + """</p>
</header>
<div class="container">
  <div class="summary">
    <span><strong>Total sites scanned:</strong> """ + str(total_sites) + """</span>
    <span><strong>Sites with issues:</strong> """ + str(sites_with_issues) + """</span>
    <span><strong>Sites with errors:</strong> """ + str(sites_with_errors) + """</span>
  </div>
""")

    for site in results_by_site:
        url = site["url"]
        title = site.get("title") or "(no title)"
        error = site.get("error")
        issues = site.get("issues", {})

        has_any_issue = not error and any(issues.get(k) for k in issues)

        html_parts.append('<div class="card">')
        html_parts.append(f"<h2>{title}</h2>")
        html_parts.append(f'<div class="url">{url}</div>')

        if error:
            html_parts.append(
                f'<div class="status-error">Error fetching page: {error}</div>'
            )
            html_parts.append('<span class="tag tag-error">Fetch error</span>')
        elif has_any_issue:
            html_parts.append(
                '<div class="status-error">Accessibility issues detected.</div>'
            )
            html_parts.append('<span class="tag tag-issues">Has issues</span>')
        else:
            html_parts.append(
                '<div class="status-ok">No issues detected by current checks.</div>'
            )
            html_parts.append('<span class="tag tag-ok">Clean</span>')

        if not error:
            # Detail per category
            for category, items in issues.items():
                if category == 'images_missing_alt':
                    cat_label = "Images missing alt text"
                elif category == 'inputs_missing_label':
                    cat_label = "Inputs without labels"
                elif category == 'low_contrast':
                    cat_label = "Low color contrast"
                elif category == 'heading_issues':
                    cat_label = "Heading structure issues"
                else:
                    cat_label = category

                html_parts.append(f"<h3>{cat_label} ({len(items)})</h3>")
                if items:
                    html_parts.append("<ul>")
                    for it in items:
                        html_parts.append(f"<li>{it}</li>")
                    html_parts.append("</ul>")
                else:
                    html_parts.append(
                        '<div class="no-issues">No issues in this category.</div>'
                    )

        html_parts.append("</div>")  # .card

    html_parts.append("""
</div>
<footer>
  FinAccAI Prototype &mdash; Rule-based HTML accessibility checks (images, inputs, headings, contrast).
</footer>
</body>
</html>
""")

    html = "".join(html_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


# -------------------------
# CSV handling & main
# -------------------------

def read_urls_from_csv(csv_path):
    """Read URLs from a CSV file expecting a 'url' column."""
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        if 'url' not in reader.fieldnames:
            raise ValueError("CSV must contain a 'url' column.")
        for row in reader:
            url = row.get('url', '').strip()
            if url:
                urls.append(url)
    return urls


def main():
    parser = argparse.ArgumentParser(
        description="FinAccAI Accessibility Checker - CSV to HTML report"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file containing a 'url' column"
    )
    args = parser.parse_args()

    try:
        urls = read_urls_from_csv(args.csv)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if not urls:
        print("No URLs found in CSV.", file=sys.stderr)
        sys.exit(1)

    results_by_site = []
    for url in urls:
        print(f"Scanning: {url}")
        html, error = get_html(url)

        if error:
            results_by_site.append({
                "url": url,
                "title": None,
                "error": error,
                "issues": {}
            })
            continue

        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else None
        issues = run_checks(html)

        results_by_site.append({
            "url": url,
            "title": title,
            "error": None,
            "issues": issues
        })

    # Ensure log folder exists
    os.makedirs("log", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = os.path.join("log", f"accessibility_report_{timestamp}.html")

    generate_html_report(results_by_site, output_path)
    print(f"\nReport generated: {output_path}")


if __name__ == "__main__":
    main()
