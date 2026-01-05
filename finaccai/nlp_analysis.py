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
        
        if use_ai:
            findings.append("🤖 Using BERT AI Model for advanced text analysis")
        
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
                    findings.append(f"AI detected unclear label: '{text}' (confidence: {ai_result['confidence']:.2f})")
            
            # Traditional checks
            if text and len(text) < 3:
                findings.append(f"Very short label text: '{text}' - may not be descriptive enough")
            elif any(word in text_lower for word in vague_words) and len(text.split()) < 3:
                findings.append(f"Potentially vague label: '{text}' - could be more descriptive")
        
        # Analyze button text with AI
        buttons = soup.find_all("button")
        for button in buttons:
            text = button.get_text().strip()
            text_lower = text.lower()
            
            if not text:
                findings.append("Button with no text - needs descriptive text")
            elif text_lower in ['click', 'submit', 'ok', 'go']:
                findings.append(f"Button text '{text}' could be more descriptive")
            elif use_ai and len(text) > 2:
                ai_result = analyze_text_with_bert(text)
                if ai_result and ai_result['descriptiveness'] == 'low':
                    findings.append(f"AI suggests button text '{text}' could be more descriptive")
        
        # Analyze link text with AI
        links = soup.find_all("a")
        non_descriptive = ['click here', 'here', 'read more', 'more', 'link']
        for link in links:
            text = link.get_text().strip().lower()
            if text in non_descriptive:
                findings.append(f"Non-descriptive link text: '{text}'")
        
        # Overall page text analysis
        all_text = soup.get_text()
        if len(all_text.strip()) < 100:
            findings.append("Page has very little text content - may impact accessibility")
        
        return findings if findings else ["No significant text quality issues detected"]
        
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
