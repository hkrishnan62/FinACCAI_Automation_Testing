"""CLI entrypoint for the finaccai package."""
import argparse
import os
import sys
from . import script


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="FinAccAI Accessibility Checker - CSV to HTML report"
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV file containing a 'url' column"
    )
    args = parser.parse_args(argv)

    try:
        urls = script.read_urls_from_csv(args.csv)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    if not urls:
        print("No URLs found in CSV.", file=sys.stderr)
        sys.exit(1)

    results_by_site = []
    for url in urls:
        print(f"Scanning: {url}")
        html, error = script.get_html(url)

        if error:
            results_by_site.append({
                "url": url,
                "title": None,
                "error": error,
                "issues": {}
            })
            continue

        # derive title and run checks
        title = None
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else None
        except Exception:
            pass

        issues = script.run_checks(html)

        results_by_site.append({
            "url": url,
            "title": title,
            "error": None,
            "issues": issues
        })

    # Ensure log folder exists
    os.makedirs("log", exist_ok=True)
    timestamp = script.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_path = os.path.join("log", f"accessibility_report_{timestamp}.html")

    script.generate_html_report(results_by_site, output_path)
    print(f"\nReport generated: {output_path}")


if __name__ == "__main__":
    main()
