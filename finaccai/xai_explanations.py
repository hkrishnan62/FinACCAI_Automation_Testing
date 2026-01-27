"""
Explainable AI (XAI) for accessibility analysis.
Provides human-readable explanations for ML predictions.
"""

def generate_explanations(issues, ai_ml_results):
    """
    Generate human-readable explanations for accessibility findings.
    
    This provides context and reasoning for detected issues,
    making the analysis more transparent and actionable.
    
    Args:
        issues: Dict of detected accessibility issues
        ai_ml_results: Results from AI/ML analysis
        
    Returns:
        dict: Explanations and recommendations
    """
    try:
        explanations = {
            'summary': generate_summary_explanation(issues),
            'recommendations': generate_recommendations(issues),
            'severity_analysis': analyze_severity(issues),
            'impact_assessment': assess_impact(issues)
        }
        
        return explanations
        
    except Exception as e:
        return {'error': str(e)}


def generate_summary_explanation(issues):
    """Generate overall summary of findings in plain language."""
    total = sum(len(v) if isinstance(v, list) else 0 for v in issues.values())
    
    if total == 0:
        return "✅ Great job! Your page is accessible and easy for everyone to use."
    elif total < 5:
        return f"Your page has {total} small issues. They're easy to fix and will help people with disabilities use your site better."
    elif total < 15:
        return f"Your page has {total} issues that need attention. Fixing these will make your site usable for people who are blind, have low vision, or use keyboards instead of a mouse."
    else:
        return f"Your page has {total} issues that create barriers for people with disabilities. Let's fix these to make your site accessible to everyone."


def generate_recommendations(issues):
    """Generate specific recommendations in plain language."""
    recommendations = []
    
    if issues.get('images'):
        count = len(issues['images'])
        recommendations.append({
            'category': 'Images',
            'priority': 'HIGH',
            'recommendation': f'🖼️ {count} images need descriptions. Blind people use special software that reads text aloud. This software can\'t see images, so you need to add a short description so they know what the image shows. Add a description like: alt="picture of a cat"',
            'example': '<img src="logo.png" alt="Company Logo">',
            'why': 'People who are blind hear your site read aloud. They need text descriptions to understand images.',
            'wcag': 'WCAG 2.1 Level A'
        })
    
    if issues.get('inputs'):
        count = len(issues['inputs'])
        recommendations.append({
            'category': 'Form Fields',
            'priority': 'HIGH',
            'recommendation': f'📝 {count} form fields don\'t have labels. People don\'t know what information to put in each box. Add text above each field explaining what to type. For example, put "Email Address" above an email box.',
            'example': '<label for="email">Your Email:</label>\n<input id="email" type="email">',
            'why': 'Everyone - including blind and keyboard users - needs to know what each form field is asking for',
            'wcag': 'WCAG 2.1 Level A'
        })
    
    if issues.get('headings'):
        count = len(issues['headings'])
        recommendations.append({
            'category': 'Page Structure',
            'priority': 'MEDIUM',
            'recommendation': f'📑 {count} section headings are in the wrong order. Think of headings like an outline: use Level 1 for your main title, Level 2 for big sections, Level 3 for smaller parts within those sections. Don\'t skip levels - go 1, 2, 3 in order. This helps people using screen readers navigate your page easily.',
            'example': 'Use Heading 1 for title, Heading 2 for sections, Heading 3 for subsections',
            'why': 'People using screen readers navigate by jumping between headings. Wrong order confuses them.',
            'wcag': 'WCAG 2.1 Level A'
        })
    
    if issues.get('contrast'):
        count = len(issues['contrast'])
        recommendations.append({
            'category': 'Colors',
            'priority': 'HIGH',
            'recommendation': f'🎨 {count} areas have text that\'s hard to read because the color is too light or too close to the background color. People with vision problems can\'t read light gray text on white background, for example. Use dark text on light backgrounds or light text on dark backgrounds.',
            'example': 'Black text on white background is easiest to read. Avoid light gray on white.',
            'why': 'Many people can\'t read text that doesn\'t have enough color difference from the background',
            'wcag': 'WCAG 2.1 Level AAA'
        })
    
    # AAA-specific recommendations
    if issues.get('link_context'):
        count = len(issues['link_context'])
        recommendations.append({
            'category': 'Link Text (AAA)',
            'priority': 'MEDIUM',
            'recommendation': f'🔗 {count} links say vague things like "Click here" or "Learn more". People using screen readers can\'t tell where these links go. Make link text describe what they\'ll find. For example, instead of "Click here", say "Read our privacy policy".',
            'example': 'Instead of "Click here", use "Download our PDF report" so people know what they\'ll get',
            'why': 'Screen reader users listen to links to decide where to go. Vague link text makes your site confusing.',
            'wcag': 'WCAG 2.1 Level AAA'
        })
    
    if issues.get('section_headings'):
        count = len(issues['section_headings'])
        recommendations.append({
            'category': 'Content Organization (AAA)',
            'priority': 'MEDIUM',
            'recommendation': f'📚 {count} sections of content need headings to organize them. Long blocks of text are hard to read and navigate. Break up your content with headings that describe what each section is about.',
            'example': 'Put a heading before each topic: "Pricing", "Features", "Support", etc.',
            'why': 'Headings help everyone - including screen reader users - quickly scan and find what they need',
            'wcag': 'WCAG 2.1 Level AAA'
        })
    
    if issues.get('abbreviations'):
        count = len(issues['abbreviations'])
        recommendations.append({
            'category': 'Abbreviations (AAA)',
            'priority': 'LOW',
            'recommendation': f'🔤 {count} abbreviations appear without explanations. Abbreviations like "HTML", "API", or "GDPR" mean nothing to people who aren\'t familiar with them. Explain what abbreviations mean the first time you use them. For example: "HTML (HyperText Markup Language)".',
            'example': 'Instead of "Use our API", say "Use our API (Application Programming Interface)"',
            'why': 'Many people don\'t know what abbreviations mean, especially people from different fields',
            'wcag': 'WCAG 2.1 Level AAA'
        })
    
    if issues.get('unusual_words'):
        count = len(issues['unusual_words'])
        recommendations.append({
            'category': 'Unusual Words (AAA)',
            'priority': 'LOW',
            'recommendation': f'📖 Page uses complicated or unusual words. Not everyone understands words like "quintessential", "magnanimous", or "sojourn". Use simple, everyday language. Instead of "quintessential" say "perfect". Instead of "sojourn" say "visit".',
            'example': 'Change "These establishments provide quintessential accommodations" to "These hotels provide great rooms"',
            'why': 'Complicated words confuse people, especially those learning English or with reading difficulties',
            'wcag': 'WCAG 2.1 Level AAA'
        })
    
    if issues.get('language_attributes'):
        count = len(issues['language_attributes'])
        if count > 0:
            recommendations.append({
                'category': 'Language (AAA)',
                'priority': 'MEDIUM',
                'recommendation': f'🌍 Tell the browser what language your page is in. If you have text in different languages (like English and Spanish on the same page), mark each section. This helps screen readers pronounce words correctly.',
                'example': 'Tell the browser your page is English: <html lang="en">',
                'why': 'Screen reading software needs to know what language to use so it pronounces words correctly',
                'wcag': 'WCAG 2.1 Level AAA'
            })
    
    if not recommendations:
        recommendations.append({
            'category': 'Overall',
            'priority': 'LOW',
            'recommendation': '✅ Keep up the good work! Test your page regularly as you add new features.',
            'why': 'Accessibility is an ongoing process',
            'wcag': 'General Best Practices'
        })
    
    return recommendations


def analyze_severity(issues):
    """Analyze severity of issues found."""
    severity = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0
    }
    
    # Images and inputs are high priority
    severity['high'] += len(issues.get('images', []))
    severity['high'] += len(issues.get('inputs', []))
    severity['high'] += len(issues.get('contrast', []))
    
    # Headings are medium priority
    severity['medium'] += len(issues.get('headings', []))
    
    return severity


def assess_impact(issues):
    """Explain who is affected by these issues in plain language."""
    impact = {}
    
    if issues.get('images'):
        impact['blind_users'] = '🚫 BLOCKED: People who are blind can\'t access your images at all because there are no descriptions. Their screen reader just says "image" without explaining what it shows.'
    
    if issues.get('inputs'):
        impact['blind_users'] = '🚫 BLOCKED: People who are blind can\'t fill out your forms because they don\'t know what each field is asking for.'
        impact['keyboard_users'] = '⚠️ DIFFICULT: People who navigate with Tab key may have trouble figuring out what to type in each field.'
    
    if issues.get('contrast'):
        impact['low_vision_users'] = '🚫 BLOCKED: People with low vision or who are color blind cannot read the text because it blends into the background.'
        impact['older_adults'] = '⚠️ DIFFICULT: Many older adults struggle to read low-contrast text, especially on mobile devices in bright sunlight.'
    
    if issues.get('headings'):
        impact['blind_users'] = '⚠️ DIFFICULT: Screen reader users press "H" to jump between headings to navigate your page. Skipped heading levels make this confusing.'
    
    if not impact:
        impact['all_users'] = '✅ GOOD: Your page is accessible. Everyone can use it equally, regardless of disabilities.'
    
    return impact


# Placeholder for future SHAP/LIME integration
"""
Future XAI Implementation:

import shap
from lime.lime_tabular import LimeTabularExplainer

def explain_ml_with_shap(model, background_data, instance):
    explainer = shap.Explainer(model.predict, background_data)
    shap_values = explainer(instance)
    return shap_values

def explain_ml_with_lime(model, train_data, feature_names, instance):
    explainer = LimeTabularExplainer(train_data, feature_names=feature_names)
    exp = explainer.explain_instance(instance, model.predict_proba)
    return exp.as_list()
"""
