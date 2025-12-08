#!/usr/bin/env python3
"""
FinAccAI Accessibility Checker (Prototype)
Checks an HTML page (from URL or file) for basic accessibility issues:
 - Missing alt text on <img>
 - <input> fields without <label> or aria-label
 - Low color contrast (inline styles only)
 - Incorrect heading order (skipped levels)

Usage:
    python finaccai.py --url https://example.com
    python finaccai.py --file localpage.html

Requires: requests, beautifulsoup4 (bs4)
"""

import argparse
import json
import re
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

def get_html(source, is_url):
    """Fetch HTML from a URL or read from a local file."""
    if is_url:
        try:
            response = requests.get(source)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching URL {source}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file {source}: {e}", file=sys.stderr)
            sys.exit(1)

def check_images(soup):
    """Check for <img> elements missing alt text."""
    issues = []
    for img in soup.find_all('img'):
        alt = img.get('alt')
        # Flag if alt is missing or empty (skip decorative empty alt if needed)
        if alt is None or alt.strip() == '':
            desc = str(img)
            issues.append(f"Image with missing/empty alt: {desc}")
    return issues

def check_inputs(soup):
    """Check for <input> fields without a label or accessible name."""
    issues = []
    # Gather all labels with 'for' target
    labels_for = {label.get('for'): label.get_text().strip()
                  for label in soup.find_all('label') if label.get('for')}
    # Also consider inputs wrapped in labels
    wrapped = set()
    for label in soup.find_all('label'):
        inp = label.find('input')
        if inp and inp.get('id'):
            wrapped.add(inp.get('id'))
    for inp in soup.find_all('input'):
        input_id = inp.get('id')
        has_label = False
        # Check explicit <label for="id">
        if input_id and input_id in labels_for:
            has_label = True
        # Check if input is wrapped by a label
        if input_id and input_id in wrapped:
            has_label = True
        # Check aria-label or aria-labelledby
        if inp.get('aria-label') or inp.get('aria-labelledby'):
            has_label = True
        # Skip hidden or submit inputs
        input_type = inp.get('type', '').lower()
        if input_type in ['hidden', 'submit', 'button', 'image', 'reset']:
            has_label = True
        if not has_label:
            desc = str(inp)
            issues.append(f"Input without label/aria-label: {desc}")
    return issues

def parse_color(color_str):
    """Convert a CSS color (#RGB or #RRGGBB) to an (R,G,B) tuple of 0-1 floats."""
    color_str = color_str.strip().lower()
    if color_str.startswith('#'):
        hex_val = color_str[1:]
        if len(hex_val) == 3:
            hex_val = ''.join([c*2 for c in hex_val])
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16) / 255.0
                g = int(hex_val[2:4], 16) / 255.0
                b = int(hex_val[4:6], 16) / 255.0
                return (r, g, b)
            except ValueError:
                return None
    return None

def rel_luminance(r, g, b):
    """Compute relative luminance for sRGB values (0-1)."""
    def channel_lum(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * channel_lum(r) + 0.7152 * channel_lum(g) + 0.0722 * channel_lum(b)

def contrast_ratio(l1, l2):
    """Compute WCAG contrast ratio given two luminances."""
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)

def check_contrast(soup):
    """
    Check inline styles for color contrast issues.
    Only handles hex colors in 'color' and 'background-color' style props.
    """
    issues = []
    # Regex to extract color values
    color_prop = re.compile(r'color\s*:\s*([^;]+)')
    bg_prop = re.compile(r'background-color\s*:\s*([^;]+)')
    for elem in soup.find_all(style=True):
        style = elem['style']
        color_match = color_prop.search(style)
        bg_match = bg_prop.search(style)
        if color_match and bg_match:
            color = parse_color(color_match.group(1))
            bg = parse_color(bg_match.group(1))
            if color and bg:
                lum1 = rel_luminance(*color)
                lum2 = rel_luminance(*bg)
                ratio = contrast_ratio(lum1, lum2)
                if ratio < 4.5:
                    issues.append(
                        f"Low contrast text (ratio {ratio:.2f}): '{elem.text.strip()}' with style '{style}'"
                    )
    return issues

def check_headings(soup):
    """Check heading tags for skipped levels (e.g., H1 followed by H3)."""
    issues = []
    heading_tags = ['h1','h2','h3','h4','h5','h6']
    last_level = 0
    for tag in soup.find_all(heading_tags):
        level = int(tag.name[1])
        if last_level and level > last_level + 1:
            issues.append(
                f"Skipped heading level: <{tag.name}> following <h{last_level}> with text '{tag.text.strip()}'"
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
        'heading_issues': check_headings(soup)
    }
    return issues

def main():
    parser = argparse.ArgumentParser(description="FinAccAI HTML Accessibility Checker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL of page to check')
    group.add_argument('--file', help='Local HTML file to check')
    args = parser.parse_args()

    if args.url:
        print(f"Fetching URL: {args.url}")
        html = get_html(args.url, is_url=True)
    else:
        print(f"Reading file: {args.file}")
        html = get_html(args.file, is_url=False)

    results = run_checks(html)
    # Print a JSON report of issues
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()
