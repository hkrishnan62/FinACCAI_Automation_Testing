# finaccai/report_generator.py
from jinja2 import Template

def generate_html_report(issues, output_path="report.html"):
    """Generate an HTML report of accessibility issues."""
    html_template = """
    <html><head><title>FinAccAI Accessibility Report</title></head><body>
    <h1>Accessibility Issues</h1>
    {% for issue in issues %}
      <div>
        <h2>{{ issue.type }}</h2>
        <p>Details: {{ issue.details }}</p>
        {% if issue.suggestion %}
          <p>Suggested fix: {{ issue.suggestion }}</p>
        {% endif %}
      </div>
    {% endfor %}
    </body></html>
    """
    template = Template(html_template)
    with open(output_path, "w") as f:
        f.write(template.render(issues=issues))
