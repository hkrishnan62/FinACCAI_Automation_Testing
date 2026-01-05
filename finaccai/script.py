"""Core scanner functions for FinAccAI.

This module contains the functions previously defined in the top-level
`finaccai.py` script (network fetching, checks, report generation,
CSV handling). The package `finaccai` exposes these at the package
level for backward compatibility.
"""

import csv
import os
import re
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


def check_contrast(soup, level='AAA'):
    """
    Check inline styles for color contrast issues.
    Only handles hex colors in 'color' and 'background-color'.
    
    Args:
        soup: BeautifulSoup object
        level: 'AA' (4.5:1 normal, 3:1 large) or 'AAA' (7:1 normal, 4.5:1 large)
    """
    issues = []
    color_prop = re.compile(r'color\s*:\s*([^;]+)', re.IGNORECASE)
    bg_prop = re.compile(r'background-color\s*:\s*([^;]+)', re.IGNORECASE)
    
    # AAA requires 7:1 for normal text, 4.5:1 for large text (18pt+ or 14pt+ bold)
    # AA requires 4.5:1 for normal text, 3:1 for large text
    min_ratio = 7.0 if level == 'AAA' else 4.5
    min_ratio_large = 4.5 if level == 'AAA' else 3.0

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
                
                # For simplicity, assume normal text (not checking font size)
                if ratio < min_ratio:
                    text = elem.get_text(strip=True)
                    short_text = (text[:80] + '...') if len(text) > 80 else text
                    issues.append(
                        f"Low contrast ({level} Level) (ratio {ratio:.2f}, needs {min_ratio}:1) for text: '{short_text}' | style='{style}'"
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


def check_language_attributes(soup):
    """AAA: Check for lang attributes on elements with different languages (3.1.2)."""
    issues = []
    
    # Check if html tag has lang attribute
    html_tag = soup.find('html')
    if html_tag and not html_tag.get('lang'):
        issues.append("Missing 'lang' attribute on <html> tag - required for screen readers")
    
    # In a real implementation, we'd check for text in different languages
    # For now, we'll just warn if no lang attributes found on any element
    elements_with_lang = soup.find_all(attrs={'lang': True})
    
    return issues


def check_link_context(soup):
    """AAA: Check that link purpose can be determined from link text alone (2.4.9)."""
    issues = []
    
    # Links that need context from surrounding text (AAA requires standalone clarity)
    vague_link_texts = ['click here', 'here', 'more', 'read more', 'link', 'this', 'continue', 'next', 'previous']
    
    for link in soup.find_all('a'):
        link_text = link.get_text(strip=True).lower()
        href = link.get('href', '')
        
        # Skip anchor links and empty links
        if not href or href.startswith('#'):
            continue
            
        # Check for vague link text
        if link_text in vague_link_texts:
            issues.append(
                f"AAA: Link text '{link_text}' needs context. Link purpose should be clear from text alone | href='{href[:60]}'"
            )
        
        # Check for very short link text (< 3 characters)
        elif len(link_text) < 3 and link_text not in ['go', 'ok']:
            issues.append(
                f"AAA: Link text too short: '{link_text}'. Make link purpose clear from text | href='{href[:60]}'"
            )
    
    return issues


def check_section_headings(soup):
    """AAA: Check that content is organized with section headings (2.4.10)."""
    issues = []
    
    # Check if page has meaningful structure with headings
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    # Count paragraphs and other content
    paragraphs = soup.find_all('p')
    sections = soup.find_all(['section', 'article', 'div'])
    
    # If page has substantial content but few headings, suggest more structure
    if len(paragraphs) > 10 and len(headings) < 3:
        issues.append(
            f"AAA: Page has {len(paragraphs)} paragraphs but only {len(headings)} headings. Use more headings to organize content into sections."
        )
    
    # Check if sections have headings
    section_tags = soup.find_all(['section', 'article', 'nav', 'aside'])
    for section in section_tags:
        has_heading = section.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if not has_heading:
            tag_id = section.get('id', 'unknown')
            issues.append(
                f"AAA: <{section.name}> element (id='{tag_id}') should have a heading to identify its purpose"
            )
    
    return issues


def check_abbreviations(soup):
    """AAA: Check for abbreviations that should be expanded (3.1.4)."""
    issues = []
    
    # Look for common abbreviation patterns
    abbr_tags = soup.find_all('abbr')
    
    # Check if abbr tags have title attribute
    for abbr in abbr_tags:
        if not abbr.get('title'):
            abbr_text = abbr.get_text(strip=True)
            issues.append(
                f"AAA: <abbr> tag '{abbr_text}' missing title attribute to provide expansion"
            )
    
    # Detect potential abbreviations in text that aren't marked up
    text_content = soup.get_text()
    
    # Common abbreviations that should be marked with <abbr>
    import re
    potential_abbrs = re.findall(r'\b[A-Z]{2,}\b', text_content)
    common_abbrs = set(['HTML', 'CSS', 'API', 'URL', 'HTTP', 'HTTPS', 'PDF', 'XML', 'JSON', 'SQL', 'USA', 'UK', 'EU', 'AI', 'ML', 'NLP'])
    
    found_unmarked = []
    for abbr in potential_abbrs[:5]:  # Limit to first 5
        if abbr in common_abbrs:
            # Check if it's already in an abbr tag
            if not soup.find('abbr', string=abbr):
                found_unmarked.append(abbr)
    
    if found_unmarked:
        issues.append(
            f"AAA: Found potential abbreviations that should use <abbr> tag: {', '.join(set(found_unmarked)[:5])}"
        )
    
    return issues


def check_unusual_words(soup):
    """AAA: Check for complex or unusual words that may need definitions (3.1.3)."""
    issues = []
    
    # This is a simplified check - in production you'd use a dictionary API
    # Look for glossary or definition lists
    has_glossary = soup.find(['dl', 'dfn']) or soup.find(attrs={'class': re.compile(r'glossary|definition')})
    
    text_content = soup.get_text()
    word_count = len(text_content.split())
    
    # If page has substantial text but no definitions/glossary, suggest adding one
    if word_count > 500 and not has_glossary:
        # Check for technical jargon indicators
        technical_indicators = ['algorithm', 'framework', 'methodology', 'implementation', 'infrastructure']
        found_technical = [word for word in technical_indicators if word in text_content.lower()]
        
        if found_technical:
            issues.append(
                f"AAA: Page contains technical terms ({', '.join(found_technical[:3])}...) but no glossary or definitions. Consider adding a glossary for unusual words."
            )
    
    return issues


def run_checks(html_content, level='AAA'):
    """Run all checks on HTML content and return a dict of issues.
    
    Args:
        html_content: HTML string to analyze
        level: 'AA' or 'AAA' - WCAG compliance level to check
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    issues = {
        # Level A & AA checks
        'images_missing_alt': check_images(soup),
        'inputs_missing_label': check_inputs(soup),
        'low_contrast': check_contrast(soup, level=level),
        'heading_issues': check_headings(soup),
    }
    
    # Add AAA-specific checks
    if level == 'AAA':
        issues.update({
            'language_attributes': check_language_attributes(soup),
            'link_context': check_link_context(soup),
            'section_headings': check_section_headings(soup),
            'abbreviations': check_abbreviations(soup),
            'unusual_words': check_unusual_words(soup),
        })
    
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
# CSV handling
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
