# finaccai/report_generator.py
from jinja2 import Template
from datetime import datetime

def generate_html_report(issues, output_path="report.html", page_url="", page_title="", ai_ml_results=None, full_page_screenshot=None):
    """
    Generate a comprehensive HTML report with full-page screenshot and numbered issues.
    
    Args:
        issues: Dict of detected accessibility issues
        output_path: Path to save the HTML report
        page_url: URL of the analyzed page
        page_title: Title of the analyzed page
        ai_ml_results: Results from AI/ML analysis
        full_page_screenshot: Base64-encoded full page screenshot with highlighted issues
    """
    
    # Calculate statistics
    total_issues = sum(len(v) if isinstance(v, list) else 0 for v in issues.values())
    critical = 0
    high = sum([len(issues.get('images', [])), len(issues.get('inputs', [])), len(issues.get('contrast', []))])
    medium = len(issues.get('headings', []))
    low = total_issues - high - medium
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FinACCAI Accessibility Report - {{ page_title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .info-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .info-card h2 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stat-card .number {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .stat-card.critical .number { color: #e53e3e; }
        .stat-card.high .number { color: #dd6b20; }
        .stat-card.medium .number { color: #d69e2e; }
        .stat-card.low .number { color: #48bb78; }
        
        .screenshot-section {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .screenshot-section h2 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }
        
        .screenshot-info {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 4px;
        }
        
        .full-page-screenshot {
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            max-width: 100%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: zoom-in;
        }
        
        .full-page-screenshot:hover {
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        }
        
        .issue-section {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .issue-item {
            border-left: 4px solid #dd6b20;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            background: #f7fafc;
            border-radius: 4px;
        }
        
        .issue-item.critical { border-left-color: #e53e3e; }
        .issue-item.high { border-left-color: #dd6b20; }
        .issue-item.medium { border-left-color: #d69e2e; }
        .issue-item.low { border-left-color: #48bb78; }
        
        .issue-number {
            display: inline-block;
            background: #667eea;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            text-align: center;
            line-height: 32px;
            font-weight: bold;
            margin-right: 0.5rem;
        }
        
        .issue-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #2d3748;
        }
        
        .issue-description {
            color: #4a5568;
            margin-bottom: 1rem;
            line-height: 1.8;
        }
        
        .issue-example {
            background: #2d3748;
            color: #68d391;
            padding: 1rem;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-x: auto;
            margin-top: 1rem;
        }
        
        .wcag-badge {
            display: inline-block;
            background: #edf2f7;
            color: #4a5568;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            margin-top: 0.5rem;
        }
        
        .ai-section {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 2px solid #667eea40;
        }
        
        .ai-section h2 {
            color: #667eea;
            margin-bottom: 1rem;
            font-size: 1.8rem;
        }
        
        .ai-insight {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .recommendation-card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid #48bb78;
        }
        
        .recommendation-card.high { border-left-color: #dd6b20; }
        .recommendation-card.medium { border-left-color: #d69e2e; }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: #718096;
            font-size: 0.9rem;
        }
        
        @media print {
            .screenshot-section { page-break-inside: avoid; }
            .issue-section { page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 FinACCAI Accessibility Report</h1>
        <p>AI-Enhanced Web Accessibility Analysis</p>
    </div>
    
    <div class="container">
        <!-- Page Info -->
        <div class="info-card">
            <h2>📄 Analyzed Page</h2>
            <p><strong>URL:</strong> <a href="{{ page_url }}" target="_blank">{{ page_url }}</a></p>
            <p><strong>Title:</strong> {{ page_title }}</p>
            <p><strong>Analysis Date:</strong> {{ timestamp }}</p>
        </div>
        
        <!-- Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="number">{{ total_issues }}</div>
                <div class="label">Total Issues</div>
            </div>
            <div class="stat-card critical">
                <div class="number">{{ critical }}</div>
                <div class="label">Critical</div>
            </div>
            <div class="stat-card high">
                <div class="number">{{ high }}</div>
                <div class="label">High Priority</div>
            </div>
            <div class="stat-card medium">
                <div class="number">{{ medium }}</div>
                <div class="label">Medium Priority</div>
            </div>
        </div>
        
        <!-- Full Page Screenshot with Highlights -->
        {% if full_page_screenshot %}
        <div class="screenshot-section">
            <h2>📸 Full Page Screenshot with Issue Highlights</h2>
            <div class="screenshot-info">
                <p><strong>ℹ️ How to read this screenshot:</strong></p>
                <ul style="margin-left: 2rem; margin-top: 0.5rem;">
                    <li>Issues are marked with <strong>red borders</strong> and <strong>numbered badges</strong></li>
                    <li>Numbers correspond to the detailed issues listed below</li>
                    <li>Screenshot shows the ENTIRE page from top to bottom</li>
                    <li>Click image to zoom in for better detail</li>
                </ul>
            </div>
            <img src="{{ full_page_screenshot }}" alt="Full page screenshot showing all accessibility issues highlighted with red borders and numbered badges" class="full-page-screenshot" onclick="window.open(this.src)">
        </div>
        {% endif %}
        
        <!-- AI/ML Analysis -->
        {% if ai_ml_results %}
        <div class="ai-section">
            <h2>🤖 AI & Machine Learning Insights</h2>
            
            {% if ai_ml_results.ml_predictions %}
            <div class="ai-insight">
                <h3 style="color: #667eea; margin-bottom: 0.5rem;">🧠 Machine Learning Analysis</h3>
                {% for prediction in ai_ml_results.ml_predictions %}
                    {% if prediction.type != 'system_info' and prediction.type != 'feature_analysis' %}
                        <p style="margin: 0.5rem 0;">{{ prediction.message }}</p>
                    {% endif %}
                {% endfor %}
            </div>
            {% endif %}
            
            {% if ai_ml_results.nlp_findings %}
            <div class="ai-insight">
                <h3 style="color: #667eea; margin-bottom: 0.5rem;">📝 Natural Language Analysis (BERT AI)</h3>
                {% for finding in ai_ml_results.nlp_findings %}
                    <p style="margin: 0.5rem 0;">{{ finding }}</p>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if ai_ml_results.vision_analysis %}
            <div class="ai-insight">
                <h3 style="color: #667eea; margin-bottom: 0.5rem;">👁️ Computer Vision Analysis (BLIP AI)</h3>
                {% for item in ai_ml_results.vision_analysis %}
                    <p style="margin: 0.5rem 0;"><strong>{{ item.element }}:</strong> {{ item.caption }}</p>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- Detailed Issues -->
        <div class="issue-section">
            <h2>🔍 Detailed Issues</h2>
            
            {% set issue_number = 1 %}
            
            {% if issues.images %}
            {% for issue in issues.images %}
            <div class="issue-item high">
                <div class="issue-title">
                    <span class="issue-number">{{ issue_number }}</span>
                    🖼️ Missing Image Description
                </div>
                <div class="issue-description">
                    <strong>Element:</strong> &lt;img src="{{ issue.src }}"&gt;<br>
                    <strong>Problem:</strong> This image has no description. People who are blind cannot see images, so their screen reader software needs a text description to tell them what the image shows.<br>
                    <strong>Who's affected:</strong> Blind users, users with images disabled, search engines
                </div>
                <div class="issue-example">
                    &lt;!-- Before (❌ Not Accessible) --&gt;<br>
                    &lt;img src="{{ issue.src }}"&gt;<br><br>
                    &lt;!-- After (✅ Accessible) --&gt;<br>
                    &lt;img src="{{ issue.src }}" alt="Description of what the image shows"&gt;
                </div>
                <span class="wcag-badge">WCAG 2.1 Level A - 1.1.1 Non-text Content</span>
            </div>
            {% set issue_number = issue_number + 1 %}
            {% endfor %}
            {% endif %}
            
            {% if issues.inputs %}
            {% for issue in issues.inputs %}
            <div class="issue-item high">
                <div class="issue-title">
                    <span class="issue-number">{{ issue_number }}</span>
                    📝 Unlabeled Form Field
                </div>
                <div class="issue-description">
                    <strong>Element:</strong> &lt;input name="{{ issue.name or issue.id }}"&gt;<br>
                    <strong>Problem:</strong> This input field doesn't have a label. Users can't tell what information they're supposed to type into this field. Screen readers will just say "edit text" without explaining what it's for.<br>
                    <strong>Who's affected:</strong> Blind users, keyboard users, mobile users, everyone
                </div>
                <div class="issue-example">
                    &lt;!-- Before (❌ Not Accessible) --&gt;<br>
                    &lt;input name="{{ issue.name or issue.id }}" type="text"&gt;<br><br>
                    &lt;!-- After (✅ Accessible) --&gt;<br>
                    &lt;label for="{{ issue.name or issue.id }}"&gt;Field Name:&lt;/label&gt;<br>
                    &lt;input id="{{ issue.name or issue.id }}" name="{{ issue.name or issue.id }}" type="text"&gt;
                </div>
                <span class="wcag-badge">WCAG 2.1 Level A - 1.3.1 Info and Relationships</span>
            </div>
            {% set issue_number = issue_number + 1 %}
            {% endfor %}
            {% endif %}
            
            {% if issues.headings %}
            {% for issue in issues.headings %}
            <div class="issue-item medium">
                <div class="issue-title">
                    <span class="issue-number">{{ issue_number }}</span>
                    📑 Incorrect Heading Order
                </div>
                <div class="issue-description">
                    <strong>Problem:</strong> {{ issue.message }}<br>
                    <strong>Why it matters:</strong> Screen reader users press the "H" key to jump between headings to navigate your page quickly. When you skip heading levels (like going from h2 to h4), it's confusing - like having a book with chapters numbered 1, 2, 5, 6.<br>
                    <strong>Who's affected:</strong> Screen reader users who navigate by headings
                </div>
                <div class="issue-example">
                    &lt;!-- Before (❌ Not Accessible) --&gt;<br>
                    &lt;h2&gt;Section&lt;/h2&gt;<br>
                    &lt;h4&gt;Subsection&lt;/h4&gt;  &lt;!-- Skipped h3! --&gt;<br><br>
                    &lt;!-- After (✅ Accessible) --&gt;<br>
                    &lt;h2&gt;Section&lt;/h2&gt;<br>
                    &lt;h3&gt;Subsection&lt;/h3&gt;  &lt;!-- Proper order --&gt;
                </div>
                <span class="wcag-badge">WCAG 2.1 Level A - 2.4.6 Headings and Labels</span>
            </div>
            {% set issue_number = issue_number + 1 %}
            {% endfor %}
            {% endif %}
            
            {% if issue_number == 1 %}
            <div class="ai-insight">
                <p>✅ <strong>Excellent!</strong> No accessibility issues detected on this page. Your page is accessible to everyone.</p>
            </div>
            {% endif %}
        </div>
        
        <!-- Recommendations -->
        {% if ai_ml_results and ai_ml_results.xai_explanations %}
        <div class="issue-section">
            <h2>💡 AI Recommendations</h2>
            
            <div class="ai-insight">
                <h3>Summary</h3>
                <p>{{ ai_ml_results.xai_explanations.summary }}</p>
            </div>
            
            {% for rec in ai_ml_results.xai_explanations.recommendations %}
            <div class="recommendation-card {{ rec.priority|lower }}">
                <h3 style="color: #2d3748; margin-bottom: 0.5rem;">{{ rec.category }}</h3>
                <p><strong>Priority:</strong> <span style="color: {% if rec.priority == 'HIGH' %}#dd6b20{% elif rec.priority == 'MEDIUM' %}#d69e2e{% else %}#48bb78{% endif %};">{{ rec.priority }}</span></p>
                <p style="margin: 0.5rem 0;"><strong>What to do:</strong> {{ rec.recommendation }}</p>
                {% if rec.example %}
                <p style="margin: 0.5rem 0;"><strong>Example:</strong> {{ rec.example }}</p>
                {% endif %}
                {% if rec.why %}
                <p style="margin: 0.5rem 0;"><strong>Why:</strong> {{ rec.why }}</p>
                {% endif %}
                <span class="wcag-badge">{{ rec.wcag }}</span>
            </div>
            {% endfor %}
            
            {% if ai_ml_results.xai_explanations.impact_assessment %}
            <div class="ai-insight">
                <h3>🎯 Who's Affected by These Issues</h3>
                {% for user_group, impact in ai_ml_results.xai_explanations.impact_assessment.items() %}
                    <p style="margin: 0.5rem 0;"><strong>{{ user_group.replace('_', ' ').title() }}:</strong> {{ impact }}</p>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}
    </div>
    
    <div class="footer">
        <p>Report generated by <strong>FinACCAI v1.0</strong> with AI/ML Enhancement</p>
        <p>Powered by BERT (NLP), BLIP (Computer Vision), and scikit-learn (Machine Learning)</p>
        <p>{{ timestamp }}</p>
    </div>
    
    <script>
        // Add smooth scrolling for issue links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    </script>
</body>
</html>
    """
    
    template = Template(html_template)
    html_content = template.render(
        issues=issues,
        page_url=page_url,
        page_title=page_title,
        timestamp=timestamp,
        total_issues=total_issues,
        critical=critical,
        high=high,
        medium=medium,
        low=low,
        ai_ml_results=ai_ml_results,
        full_page_screenshot=full_page_screenshot
    )
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return output_path
