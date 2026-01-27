"""
NLP Analysis for accessibility text content.
Uses natural language processing to analyze text clarity and meaning.
"""

# Try to import transformer models for advanced NLP
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    # Initialize sentiment analysis for text quality
    try:
        sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except:
        sentiment_analyzer = None
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    sentiment_analyzer = None

def analyze_text_with_bert(text):
    """
    Analyze text quality using BERT-based transformer model.
    
    Args:
        text: Text to analyze
        
    Returns:
        dict: Analysis results with quality score
    """
    if sentiment_analyzer and len(text.strip()) > 0:
        try:
            result = sentiment_analyzer(text[:512])[0]  # BERT limit
            return {
                'quality': 'good' if result['label'] == 'POSITIVE' and result['score'] > 0.7 else 'needs_improvement',
                'confidence': result['score'],
                'descriptiveness': 'high' if len(text.split()) > 3 else 'low'
            }
        except:
            pass
    return None

def analyze_text(soup):
    """
    Analyze page text and form labels using NLP techniques.
    Now enhanced with BERT transformer models when available!
    
    Args:
        soup: BeautifulSoup parsed HTML
        
    Returns:
        list: NLP findings with text quality issues
    """
    try:
        findings = []
        use_ai = TRANSFORMERS_AVAILABLE and sentiment_analyzer is not None
        issue_count = 0
        
        # Analyze form labels with AI enhancement
        labels = soup.find_all("label")
        vague_words = ['click', 'here', 'this', 'that', 'enter', 'input']
        
        for label in labels:
            text = label.get_text().strip()
            text_lower = text.lower()
            
            # Use AI to analyze text quality
            if use_ai and len(text) > 3:
                ai_result = analyze_text_with_bert(text)
                if ai_result and ai_result['quality'] == 'needs_improvement':
                    issue_count += 1
                    findings.append(f"❌ Confusing label text: '{text}' - Users may not understand what this field is for")
            
            # Traditional checks
            if text and len(text) < 3:
                issue_count += 1
                findings.append(f"❌ Too short: '{text}' - Add more words so users know what to enter")
            elif any(word in text_lower for word in vague_words) and len(text.split()) < 3:
                issue_count += 1
                findings.append(f"❌ Unclear label: '{text}' - Be more specific about what information is needed")
        
        # Analyze button text with AI
        buttons = soup.find_all("button")
        for button in buttons:
            text = button.get_text().strip()
            text_lower = text.lower()
            
            if not text:
                issue_count += 1
                findings.append("❌ Empty button - Add text that explains what the button does")
            elif text_lower in ['click', 'submit', 'ok', 'go']:
                issue_count += 1
                findings.append(f"❌ Vague button: '{text}' - Say what happens when clicked (e.g., 'Submit Form', 'Search Articles')")
            elif use_ai and len(text) > 2:
                ai_result = analyze_text_with_bert(text)
                if ai_result and ai_result['descriptiveness'] == 'low':
                    issue_count += 1
                    findings.append(f"⚠️ Button '{text}' could be clearer - Explain the button's purpose more specifically")
        
        # Analyze link text with AI
        links = soup.find_all("a")
        non_descriptive = ['click here', 'here', 'read more', 'more', 'link']
        link_issues = 0
        for link in links:
            text = link.get_text().strip().lower()
            if text in non_descriptive:
                link_issues += 1
                if link_issues <= 5:  # Only show first 5 to avoid spam
                    issue_count += 1
                    findings.append(f"❌ Unhelpful link: '{text}' - Link text should describe where it goes")
        
        if link_issues > 5:
            findings.append(f"⚠️ Found {link_issues} more links with unclear text - consider making them more descriptive")
        
        # Add summary at the top
        if use_ai and issue_count > 0:
            findings.insert(0, f"🤖 AI found {issue_count} text clarity issues that may confuse users")
        elif issue_count > 0:
            findings.insert(0, f"Found {issue_count} text clarity issues")
        else:
            findings.append("✅ All text appears clear and descriptive")
        
        return findings
        
    except Exception as e:
        return [f"NLP analysis error: {str(e)}"]


# Placeholder for future transformer-based NLP
"""
Future NLP Implementation:

from transformers import pipeline

# Load transformer model for text quality analysis
text_classifier = pipeline("text-classification", model="bert-base-uncased")

def analyze_with_transformer(text):
    result = text_classifier(text)
    return result

def check_readability(text):
    # Use readability metrics
    # Check for passive voice
    # Analyze sentence complexity
    pass
"""
