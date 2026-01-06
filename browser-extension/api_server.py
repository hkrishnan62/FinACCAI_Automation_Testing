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

# Try to import AI/ML modules (optional dependencies)
AI_ML_AVAILABLE = False
try:
    from finaccai import nlp_analysis, ml_model, vision_analysis, xai_explanations
    AI_ML_AVAILABLE = True
    print("✓ AI/ML modules loaded successfully")
except ImportError as e:
    print(f"⚠ AI/ML modules not available: {e}")
    print("  Running in basic mode (rule-based checks only)")
    print("  To enable AI/ML: pip install transformers torch scikit-learn pillow")

app = Flask(__name__)
CORS(app)  # Enable CORS for browser extension

# Directory to store generated reports - use the root reports directory
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
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
        level = data.get('level', 'AAA')  # Default to AAA level
        screenshot = data.get('screenshot', None)  # Base64 encoded screenshot
        
        # Debug: Check if screenshot was received
        with open('/tmp/screenshot_debug.log', 'a') as f:
            f.write(f"[{datetime.now()}] Screenshot received: {screenshot is not None}\n")
            if screenshot:
                f.write(f"  Screenshot length: {len(screenshot)}\n")
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Run basic rule-based accessibility checks with AAA level
        issues = {}
        issues['images'] = script.check_images(soup)
        issues['inputs'] = script.check_inputs(soup)
        issues['contrast'] = script.check_contrast(soup, level=level)
        issues['headings'] = script.check_headings(soup)
        
        # AAA-specific checks
        if level == 'AAA':
            issues['language_attributes'] = script.check_language_attributes(soup)
            issues['link_context'] = script.check_link_context(soup)
            issues['section_headings'] = script.check_section_headings(soup)
            issues['abbreviations'] = script.check_abbreviations(soup)
            issues['unusual_words'] = script.check_unusual_words(soup)
        
        # AI/ML Analysis (if available)
        ai_ml_results = {}
        if AI_ML_AVAILABLE:
            try:
                # NLP Analysis - analyze text content and labels
                ai_ml_results['nlp_analysis'] = nlp_analysis.analyze_text(soup)
                
                # ML Model - predict potential issues based on patterns
                ai_ml_results['ml_predictions'] = ml_model.predict_issue_from_soup(soup)
                
                # Vision Analysis - analyze images (if applicable)
                ai_ml_results['vision_analysis'] = vision_analysis.analyze_images(soup, None)
                
                # XAI - Generate explanations for predictions
                ai_ml_results['xai_explanations'] = xai_explanations.generate_explanations(
                    issues, ai_ml_results
                )
                
                ai_ml_results['status'] = 'AI/ML analysis completed'
                ai_ml_results['level'] = level
            except Exception as e:
                ai_ml_results['status'] = f'AI/ML analysis failed: {str(e)}'
                ai_ml_results['error'] = str(e)
        else:
            ai_ml_results['status'] = 'AI/ML modules not installed'
            ai_ml_results['message'] = 'Install: pip install transformers torch scikit-learn'
        
        # Generate HTML report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f'accessibility_report_{timestamp}.html'
        report_path = os.path.join(REPORTS_DIR, report_filename)
        
        report_html = generate_simple_report(url, title, issues, ai_ml_results, level=level, screenshot=screenshot)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_html)
        
        return jsonify({
            'success': True,
            'data': {
                'issues': issues,
                'ai_ml_results': ai_ml_results,
                'ai_ml_enabled': AI_ML_AVAILABLE,
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


def generate_simple_report(url, title, issues, ai_ml_results=None, level='AAA', screenshot=None):
    """Generate a simple HTML report with optional screenshot."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_issues = sum(len(v) if isinstance(v, list) else 0 for v in issues.values())
    
    # Determine analysis mode
    analysis_mode = f"WCAG 2.1 Level {level} Validation"
    if ai_ml_results and ai_ml_results.get('status') == 'AI/ML analysis completed':
        analysis_mode = f"WCAG 2.1 Level {level} with AI/ML Enhancement"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }}
        .summary-item:last-child {{ border-bottom: none; }}
        .count {{
            font-weight: bold;
            font-size: 24px;
            color: #dc3545;
        }}
        .count.success {{ color: #28a745; }}
        .category {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category h2 {{
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #333;
        }}
        .issue {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
        }}
        .issue-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 8px;
        }}
        .issue-detail {{
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }}
        .code {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 10px;
        }}
        .no-issues {{
            color: #28a745;
            font-style: italic;
            padding: 20px;
            text-align: center;
        }}
        .screenshot-section {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .screenshot-section h2 {{
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #333;
        }}
        .screenshot-section img {{
            max-width: 100%;
            border: 2px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .screenshot-caption {{
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 10px;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 FinACCAI Accessibility Report</h1>
        <p><strong>Page:</strong> {title}</p>
        <p><strong>URL:</strong> {url}</p>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Analysis Mode:</strong> {analysis_mode}</p>
    </div>
"""
    
    # Add screenshot section if provided
    with open('/tmp/screenshot_debug.log', 'a') as f:
        f.write(f"[{datetime.now()}] In generate_simple_report: screenshot is {screenshot is not None}\n")
        if screenshot:
            f.write(f"  Screenshot type: {type(screenshot)}, Length: {len(screenshot)}\n")
            f.write(f"  First 50 chars: {screenshot[:50]}\n")
        
    if screenshot:
        html += f"""
    <div class="screenshot-section">
        <h2>📸 Page Screenshot with Highlighted Issues</h2>
        <img src="data:image/png;base64,{screenshot}" alt="Page screenshot with {total_issues} issues highlighted and numbered">
        <div class="screenshot-caption">
            {total_issues} issue{"s" if total_issues != 1 else ""} highlighted with numbered badges
        </div>
    </div>
"""
        with open('/tmp/screenshot_debug.log', 'a') as f:
            f.write(f"  Screenshot section added to HTML\n")
    
    html += f"""
    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item">
            <span>Total Issues Found:</span>
            <span class="count {'success' if total_issues == 0 else ''}">{total_issues}</span>
        </div>
        <div class="summary-item">
            <span>🖼️ Missing Alt Text:</span>
            <span class="count {'success' if len(issues.get('images', [])) == 0 else ''}">{len(issues.get('images', []))}</span>
        </div>
        <div class="summary-item">
            <span>📝 Unlabeled Inputs:</span>
            <span class="count {'success' if len(issues.get('inputs', [])) == 0 else ''}">{len(issues.get('inputs', []))}</span>
        </div>
        <div class="summary-item">
            <span>🎨 Contrast Issues:</span>
            <span class="count {'success' if len(issues.get('contrast', [])) == 0 else ''}">{len(issues.get('contrast', []))}</span>
        </div>
        <div class="summary-item">
            <span>📑 Heading Hierarchy:</span>
            <span class="count {'success' if len(issues.get('headings', [])) == 0 else ''}">{len(issues.get('headings', []))}</span>
        </div>
    </div>
"""
    
    # Images section
    images = issues.get('images', [])
    html += f"""
    <div class="category">
        <h2>🖼️ Missing Alt Text ({len(images)} issues)</h2>
"""
    if images:
        for i, issue in enumerate(images, 1):
            html += f"""
        <div class="issue">
            <div class="issue-title">Issue #{i}: Image without alt text</div>
            <div class="issue-detail">{issue}</div>
        </div>
"""
    else:
        html += '<div class="no-issues">✓ No issues found - all images have alt text</div>'
    html += '    </div>\n'
    
    # Inputs section
    inputs = issues.get('inputs', [])
    html += f"""
    <div class="category">
        <h2>📝 Unlabeled Input Fields ({len(inputs)} issues)</h2>
"""
    if inputs:
        for i, issue in enumerate(inputs, 1):
            html += f"""
        <div class="issue">
            <div class="issue-title">Issue #{i}: Input without proper label</div>
            <div class="issue-detail">{issue}</div>
        </div>
"""
    else:
        html += '<div class="no-issues">✓ No issues found - all inputs are properly labeled</div>'
    html += '    </div>\n'
    
    # Contrast section
    contrast = issues.get('contrast', [])
    html += f"""
    <div class="category">
        <h2>🎨 Color Contrast Issues ({len(contrast)} issues)</h2>
"""
    if contrast:
        for i, issue in enumerate(contrast, 1):
            html += f"""
        <div class="issue">
            <div class="issue-title">Issue #{i}: Insufficient color contrast</div>
            <div class="issue-detail">{issue}</div>
        </div>
"""
    else:
        html += '<div class="no-issues">✓ No issues found - color contrast is adequate</div>'
    html += '    </div>\n'
    
    # Headings section
    headings = issues.get('headings', [])
    html += f"""
    <div class="category">
        <h2>📑 Heading Hierarchy Issues ({len(headings)} issues)</h2>
"""
    if headings:
        for i, issue in enumerate(headings, 1):
            html += f"""
        <div class="issue">
            <div class="issue-title">Issue #{i}: Heading hierarchy problem</div>
            <div class="issue-detail">{issue}</div>
        </div>
"""
    else:
        html += '<div class="no-issues">✓ No issues found - heading hierarchy is correct</div>'
    html += '    </div>\n'
    
    # AI/ML Results section (if available)
    if ai_ml_results:
        html += """
    <div class="category" style="border-left: 4px solid #667eea;">
        <h2>🤖 AI/ML Analysis Results</h2>
"""
        if ai_ml_results.get('status') == 'AI/ML analysis completed':
            html += """
        <div class="issue" style="border-left: 4px solid #28a745; background: #d4edda;">
            <div class="issue-title" style="color: #155724;">✓ AI/ML Analysis Completed</div>
            <div class="issue-detail" style="color: #155724;">Advanced analysis using machine learning and natural language processing</div>
        </div>
"""
            
            # NLP Analysis Results
            nlp = ai_ml_results.get('nlp_analysis', [])
            if nlp:
                html += f"""
        <div class="issue">
            <div class="issue-title">📝 NLP Analysis ({len(nlp)} findings)</div>
"""
                for finding in nlp:
                    html += f"""
            <div class="issue-detail">• {finding}</div>
"""
                html += """
        </div>
"""
            
            # ML Predictions - User Friendly Format
            ml_pred = ai_ml_results.get('ml_predictions', {})
            if ml_pred and isinstance(ml_pred, dict):
                # Show ML summary
                summary = ml_pred.get('summary', {})
                if summary:
                    html += f"""
        <div class="issue" style="border-left: 4px solid #17a2b8; background: #d1ecf1;">
            <div class="issue-title" style="color: #0c5460;">{summary.get('title', '🤖 AI Analysis')}</div>
            <div class="issue-detail" style="color: #0c5460;">{summary.get('description', '')}</div>
        </div>
"""
                
                # Show overall severity
                severity = ml_pred.get('severity', '')
                explanation = ml_pred.get('explanation', '')
                if severity or explanation:
                    html += f"""
        <div class="issue">
            <div class="issue-title">📊 Overall Assessment</div>
            <div class="issue-detail"><strong>{severity}</strong></div>
            <div class="issue-detail">{explanation}</div>
        </div>
"""
                
                # Show each insight
                insights = ml_pred.get('insights', [])
                for insight in insights:
                    severity_color = {
                        'High': '#dc3545',
                        'Medium': '#ffc107',
                        'Low': '#17a2b8',
                        'Good': '#28a745'
                    }.get(insight.get('severity'), '#6c757d')
                    
                    html += f"""
        <div class="issue" style="border-left: 4px solid {severity_color};">
            <div class="issue-title">{insight.get('title', 'Insight')}</div>
            <div class="issue-detail"><strong>What we found:</strong> {insight.get('explanation', '')}</div>
            <div class="issue-detail"><strong>Why it matters:</strong> {insight.get('impact', '')}</div>
            <div class="issue-detail"><strong>How to fix:</strong> {insight.get('what_to_do', '')}</div>
            <div class="issue-detail" style="margin-top: 5px; font-size: 12px; color: #666;">
                Confidence: {insight.get('confidence', 'Unknown')} | Severity: {insight.get('severity', 'Unknown')}
            </div>
        </div>
"""
                
                # Show statistics
                stats = ml_pred.get('statistics', {})
                if stats:
                    html += f"""
        <div class="issue" style="border-left: 4px solid #6c757d; background: #f8f9fa;">
            <div class="issue-title">{stats.get('title', '📈 Statistics')}</div>
"""
                    for item in stats.get('items', []):
                        html += f'            <div class="issue-detail">• {item}</div>\n'
                    html += """
        </div>
"""
                
                # Show model info
                model_info = ml_pred.get('model_info', '')
                if model_info:
                    html += f"""
        <div class="issue-detail" style="text-align: center; color: #6c757d; margin-top: 10px;">
            {model_info}
        </div>
"""
            
            # XAI Explanations
            xai = ai_ml_results.get('xai_explanations', {})
            if xai and isinstance(xai, dict):
                recommendations = xai.get('recommendations', [])
                if recommendations:
                    html += f"""
        <div class="issue">
            <div class="issue-title">💡 Explainable AI Recommendations ({len(recommendations)} suggestions)</div>
"""
                    for i, rec in enumerate(recommendations, 1):
                        if isinstance(rec, dict):
                            # Extract recommendation content
                            title = rec.get('recommendation', '')
                            category = rec.get('category', 'General')
                            
                            # Build the recommendation text
                            if title:
                                html += f"""
            <div class="issue-detail" style="margin-top: 15px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                <strong>{i}. {title}</strong> <span style="color: #666; font-size: 12px;">({category})</span>
            </div>
"""
                        else:
                            html += f"""
            <div class="issue-detail">• {rec}</div>
"""
                    html += """
        </div>
"""
                else:
                    html += """
        <div class="issue">
            <div class="issue-title">💡 Explainable AI Insights</div>
            <div class="issue-detail">AI analysis completed. No additional recommendations at this time.</div>
        </div>
"""
        else:
            html += f"""
        <div class="issue" style="border-left: 4px solid #ffc107; background: #fff3cd;">
            <div class="issue-title" style="color: #856404;">⚠ AI/ML Not Available</div>
            <div class="issue-detail" style="color: #856404;">{ai_ml_results.get('status', 'Unknown status')}</div>
            <div class="issue-detail" style="color: #856404; margin-top: 10px;">
                <strong>To enable AI/ML features:</strong><br>
                <code style="background: #2d2d2d; color: #f8f8f2; padding: 5px; display: block; margin-top: 5px;">
                pip install transformers torch scikit-learn pillow
                </code>
            </div>
        </div>
"""
        html += '    </div>\n'
    
    html += """
</body>
</html>
"""
    return html


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
    app.run(host='0.0.0.0', port=5000, debug=False)

