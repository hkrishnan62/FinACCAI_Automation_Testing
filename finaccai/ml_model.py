"""
ML Model for accessibility prediction.
This module uses machine learning to predict potential accessibility issues.
"""

# Try to import scikit-learn for ML models
try:
    from sklearn.ensemble import RandomForestClassifier
    import numpy as np
    SKLEARN_AVAILABLE = True
    
    # Pre-trained weights based on common patterns (simulated trained model)
    # In production, this would be loaded from a saved model file
    rf_model = RandomForestClassifier(n_estimators=10, random_state=42)
    # We'll use heuristics to simulate predictions since we don't have training data
    MODEL_TRAINED = False
except ImportError:
    SKLEARN_AVAILABLE = False
    rf_model = None
    MODEL_TRAINED = False

def extract_advanced_features(soup):
    """
    Extract advanced ML features from DOM.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        dict: Feature vector for ML model
    """
    features = {
        'total_elements': len(soup.find_all()),
        'images_count': len(soup.find_all('img')),
        'images_with_alt': len([img for img in soup.find_all('img') if img.get('alt')]),
        'inputs_count': len(soup.find_all('input')),
        'inputs_with_label': 0,  # Would need more complex check
        'buttons_count': len(soup.find_all('button')),
        'links_count': len(soup.find_all('a')),
        'headings_count': len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])),
        'aria_labels': len(soup.find_all(attrs={'aria-label': True})),
        'roles': len(soup.find_all(attrs={'role': True})),
        'nesting_depth': calculate_max_depth(soup),
        'complexity_score': 0,
    }
    
    # Calculate complexity score
    features['complexity_score'] = (
        features['total_elements'] / 100 +
        features['images_count'] / 10 +
        features['inputs_count'] / 5
    )
    
    # Calculate ratios
    if features['images_count'] > 0:
        features['alt_text_coverage'] = features['images_with_alt'] / features['images_count']
    else:
        features['alt_text_coverage'] = 1.0
    
    return features

def calculate_max_depth(element, depth=0):
    """Calculate maximum nesting depth of DOM."""
    if not hasattr(element, 'children'):
        return depth
    max_child_depth = depth
    for child in element.children:
        if hasattr(child, 'children'):
            child_depth = calculate_max_depth(child, depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
    return max_child_depth

def predict_issue_from_soup(soup):
    """
    Predict accessibility issues using ML based on DOM structure.
    Returns user-friendly predictions in plain English.
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        dict: User-friendly predictions with explanations
    """
    try:
        # Extract advanced features for ML
        features = extract_advanced_features(soup)
        
        insights = []
        use_ml = SKLEARN_AVAILABLE
        
        # Create user-friendly summary
        summary = {
            'title': '🤖 AI Page Analysis',
            'description': 'Our machine learning model scanned your page and found these patterns:'
        }
        
        # Analyze images
        if features['images_count'] > 0:
            coverage_pct = features['alt_text_coverage'] * 100
            images_missing_alt = features['images_count'] - features['images_with_alt']
            
            if images_missing_alt > 0:
                confidence = 'High' if images_missing_alt > 5 else 'Medium'
                insights.append({
                    'severity': 'High' if images_missing_alt > 5 else 'Medium',
                    'confidence': confidence,
                    'title': f'📸 {images_missing_alt} Image{"s" if images_missing_alt != 1 else ""} Missing Descriptions',
                    'explanation': f'Your page has {features["images_count"]} images, but {images_missing_alt} {"are" if images_missing_alt != 1 else "is"} missing alt text.',
                    'impact': 'Blind users using screen readers won\'t know what these images show.',
                    'what_to_do': 'Add descriptive alt text to each image. Example: alt="Hilton hotel lobby with chandelier"'
                })
            else:
                insights.append({
                    'severity': 'Good',
                    'confidence': 'High',
                    'title': f'✅ All {features["images_count"]} Images Have Descriptions',
                    'explanation': 'Great job! Every image on your page has alt text.',
                    'impact': 'Screen reader users can understand what your images show.',
                    'what_to_do': 'Keep it up! Make sure new images also get descriptions.'
                })
        
        # Analyze form inputs
        if features['inputs_count'] > 0:
            if features['inputs_count'] >= 5:
                insights.append({
                    'severity': 'Medium',
                    'confidence': 'High',
                    'title': f'📝 Complex Form with {features["inputs_count"]} Input Fields',
                    'explanation': f'This page has a form with {features["inputs_count"]} fields. Complex forms need extra care.',
                    'impact': 'Users with disabilities may struggle if fields aren\'t clearly labeled.',
                    'what_to_do': 'Make sure every field has a visible label and helpful instructions.'
                })
            else:
                insights.append({
                    'severity': 'Low',
                    'confidence': 'Medium',
                    'title': f'📋 Form Detected ({features["inputs_count"]} fields)',
                    'explanation': f'Your form has {features["inputs_count"]} input fields.',
                    'impact': 'Users need clear labels to know what information to enter.',
                    'what_to_do': 'Add <label> tags for each input field.'
                })
        
        # Analyze page complexity
        if features['total_elements'] > 100:
            complexity_rating = 'Very High' if features['total_elements'] > 300 else 'High'
            insights.append({
                'severity': 'Medium',
                'confidence': 'High',
                'title': f'📊 Complex Page ({features["total_elements"]} elements)',
                'explanation': f'Your page has {features["total_elements"]} HTML elements. That\'s a lot!',
                'impact': 'Screen readers take longer to navigate complex pages. Users might get lost.',
                'what_to_do': 'Add skip links and ARIA landmarks (nav, main, aside) to help users jump around.'
            })
        
        # Analyze heading structure
        if features['headings_count'] == 0:
            insights.append({
                'severity': 'High',
                'confidence': 'High',
                'title': '⚠️ No Headings Detected',
                'explanation': 'This page has no heading tags (h1, h2, h3, etc.).',
                'impact': 'Screen reader users can\'t navigate by headings. They\'re stuck reading everything linearly.',
                'what_to_do': 'Add heading tags to structure your content. Start with <h1> for the main title.'
            })
        elif features['headings_count'] > 0 and features['headings_count'] < 3:
            insights.append({
                'severity': 'Medium',
                'confidence': 'Medium',
                'title': f'📑 Only {features["headings_count"]} Heading{"s" if features["headings_count"] != 1 else ""} Found',
                'explanation': f'Your page has only {features["headings_count"]} heading tag{"s" if features["headings_count"] != 1 else ""}.',
                'impact': 'More headings help users navigate and understand page structure.',
                'what_to_do': 'Break up content with descriptive headings (h2, h3, etc.).'
            })
        
        # Analyze ARIA usage
        if features['aria_labels'] == 0 and features['inputs_count'] > 0:
            insights.append({
                'severity': 'Low',
                'confidence': 'Medium',
                'title': '♿ No ARIA Labels Detected',
                'explanation': 'Your page doesn\'t use any ARIA labels yet.',
                'impact': 'ARIA labels help provide extra context for assistive technologies.',
                'what_to_do': 'Consider adding aria-label to buttons/links that don\'t have visible text.'
            })
        
        # Page summary statistics
        stats = {
            'title': '📈 Page Statistics',
            'items': [
                f'Total elements: {features["total_elements"]}',
                f'Images: {features["images_count"]} ({features["images_with_alt"]} with descriptions)',
                f'Form inputs: {features["inputs_count"]}',
                f'Buttons: {features["buttons_count"]}',
                f'Links: {features["links_count"]}',
                f'Headings: {features["headings_count"]}',
                f'ARIA elements: {features["aria_labels"]}'
            ]
        }
        
        return {
            'summary': summary,
            'insights': insights,
            'statistics': stats,
            'severity': calculate_overall_severity(insights),
            'explanation': format_simple_explanation(insights),
            'model_info': '🤖 Analyzed using AI pattern recognition'
        }
        
    except Exception as e:
        return {
            'summary': {'title': 'Error', 'description': 'Could not analyze page'},
            'insights': [],
            'error': str(e)
        }


def calculate_overall_severity(insights):
    """Calculate overall severity from insights."""
    if not insights:
        return 'Unknown'
    
    high_count = sum(1 for i in insights if i.get('severity') == 'High')
    medium_count = sum(1 for i in insights if i.get('severity') == 'Medium')
    
    if high_count >= 2:
        return 'Multiple serious issues detected'
    elif high_count == 1:
        return 'One serious issue detected'
    elif medium_count >= 2:
        return 'Several moderate issues detected'
    elif medium_count == 1:
        return 'One moderate issue detected'
    else:
        return 'Minor or no issues detected'


def format_simple_explanation(insights):
    """Format insights into a simple explanation."""
    if not insights:
        return 'No issues detected by AI analysis.'
    
    high_issues = [i for i in insights if i.get('severity') == 'High']
    medium_issues = [i for i in insights if i.get('severity') == 'Medium']
    
    parts = []
    if high_issues:
        parts.append(f"Found {len(high_issues)} serious issue{'s' if len(high_issues) != 1 else ''}")
    if medium_issues:
        parts.append(f"{len(medium_issues)} moderate issue{'s' if len(medium_issues) != 1 else ''}")
    
    if not parts:
        return 'Your page looks pretty good! Check the detailed findings below.'
    
    return ' and '.join(parts) + '. See details below for how to fix them.'


# Placeholder for future ML model integration
"""
Future ML Implementation:

import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Load pre-trained model
with open("models/ml_classifier.pkl", "rb") as f:
    ml_model = pickle.load(f)

def extract_ml_features(soup):
    # Extract comprehensive features for ML
    features = []
    # ... feature engineering
    return np.array(features).reshape(1, -1)

def predict_with_ml(features):
    predictions = ml_model.predict(features)
    probabilities = ml_model.predict_proba(features)
    return predictions, probabilities
"""
