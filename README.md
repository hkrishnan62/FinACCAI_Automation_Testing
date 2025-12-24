Accessibility Testing Automation using AI model
FinAccAI – Automated Web Accessibility Audit Prototype
Overview

FinAccAI is a Python-based accessibility auditing prototype that performs automated, rule-based checks on websites to identify common WCAG-aligned accessibility issues. The tool is designed to help QA engineers, accessibility auditors, and development teams quickly assess baseline accessibility compliance across one or multiple web applications.

FinAccAI scans HTML content, detects common violations, and generates a clear, human-readable HTML report summarizing findings at both site and issue-category levels.

This project focuses on practical, lightweight accessibility validation suitable for early testing, regression checks, and compliance readiness reviews.

Key Capabilities

FinAccAI currently performs the following automated checks:

Image Accessibility

Detects <img> elements with missing or empty alt attributes

Form Accessibility

Identifies <input> elements without associated <label>, aria-label, or aria-labelledby attributes

Color Contrast (Inline Styles)

Flags insufficient color contrast where inline CSS uses hexadecimal foreground and background colors

Uses WCAG contrast ratio thresholds for detection

Heading Structure Validation

Detects skipped heading levels (e.g., <h1> followed directly by <h3>)

Multi-Site Scanning

Supports scanning multiple URLs provided via a CSV file

Reporting

Generates a styled HTML report with:

Summary metrics

Per-site status

Categorized issue listings

Reports are saved under the log/ directory

Intended Use Cases

FinAccAI is suitable for:

Accessibility smoke testing during development

QA validation before accessibility audits

Regression checks in CI/CD pipelines

Early identification of WCAG-related risks

Educational and research-oriented accessibility analysis

⚠️ Note:
This tool is a prototype and does not replace full manual or assistive-technology testing. It is intended to complement expert accessibility reviews.

Prerequisites

Python 3.7 or higher

Required Python packages:

requests

beautifulsoup4

Install dependencies using:

pip install requests beautifulsoup4

How It Works (High-Level)

Reads a CSV file containing website URLs

Fetches HTML content for each URL

Applies rule-based accessibility checks

Aggregates findings across all sites

Generates a timestamped HTML report

Input Format

CSV file must contain a column named url:

url
https://example.com
https://another-site.com

Running the Tool
python finaccai.py --csv sites.csv


After execution, the accessibility report will be generated under:

log/accessibility_report_<timestamp>.html

Output

The HTML report includes:

Total sites scanned

Sites with accessibility issues

Sites with fetch errors

Detailed issue breakdown per site:

Images missing alt text

Inputs without labels

Low contrast elements

Heading structure issues

CI/CD Compatibility

FinAccAI is designed to be CI-friendly and can be integrated into automated pipelines.
The generated HTML reports can be archived as build artifacts for audit and review purposes.

Project Status & Scope

Rule-based checks only (no browser automation)

Inline CSS color contrast checks only

Focused on static HTML analysis

Prototype / research-oriented implementation

Future enhancements may include:

CSS file parsing

ARIA role validation

JavaScript-rendered DOM analysis

Accessibility scoring metrics

License & Usage

This project is provided for research, educational, and evaluation purposes.
Users are encouraged to adapt and extend the framework for their own accessibility workflows.
