"""Flask API server for FinACCAI browser extension.

This module provides a REST API endpoint that the browser extension
can call to analyze HTML content with the full FinACCAI pipeline.
"""

import os
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bs4 import BeautifulSoup

# Add parent directory to path to import finaccai modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from finaccai import script
from finaccai import rule_checks, nlp_analysis, vision_analysis, xai_explanations
from finaccai import ml_model, report_generator

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Directory to store generated reports
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)


@app.route('/api/analyze', methods=['POST'])
def analyze_page():
    """Analyze HTML content sent from the browser extension."""
    try:
        data = request.get_json()
        
        if not data or 'html' not in data:
            return jsonify({
                'success': False,
                'error': 'No HTML content provided'
            }), 400
        
        html_content = data['html']
        url = data.get('url', 'unknown')
        title = data.get('title', 'Untitled Page')
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Run all accessibility checks
        issues = {}
        issues['images'] = script.check_images(soup)
        issues['inputs'] = script.check_inputs(soup)
        issues['contrast'] = script.check_contrast(soup)
        issues['headings'] = script.check_headings(soup)
        
        # Additional rule-based checks
        rule_results = rule_checks.run_all_checks(html_content, url)
        
        # NLP Analysis
        nlp_results = nlp_analysis.analyze_content(html_content)
        
        # Vision Analysis (take screenshot would need to be handled differently)
        # For browser extension, we'll skip screenshot analysis or use a different approach
        vision_results = {"note": "Vision analysis requires screenshot capture"}
        
        # ML Model predictions
        ml_predictions = ml_model.predict_issues(html_content, soup)
        
        # Generate XAI explanations
        xai_results = xai_explanations.generate_explanations(
            issues, rule_results, nlp_results
        )
        
        # Combine results
        result_data = {
            "url": url,
            "title": title,
            "error": None,
            "issues": issues,
            "rule_checks": rule_results,
            "nlp_analysis": nlp_results,
            "ml_predictions": ml_predictions,
            "xai_explanations": xai_results
        }
        
        # Generate HTML report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'accessibility_report_{timestamp}.html'
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        report_html = report_generator.generate_html_report([result_data])
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return jsonify({
            'success': True,
            'data': {
                'issues': issues,
                'totalIssues': sum(len(v) if isinstance(v, list) else 0 for v in issues.values()),
                'reportPath': report_filename,
                'reportUrl': f'/reports/{report_filename}'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/reports/<filename>')
def serve_report(filename):
    """Serve generated HTML reports."""
    return send_from_directory(REPORTS_DIR, filename)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'FinACCAI API',
        'version': '1.0.0'
    })


if __name__ == '__main__':
    print("Starting FinACCAI API server on http://localhost:5000")
    print("This server enables the browser extension to analyze pages")
    app.run(host='0.0.0.0', port=5000, debug=True)
