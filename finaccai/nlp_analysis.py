from transformers import pipeline

# Load a BERT-based classifier (e.g. for text clarity or error detection)
text_classifier = pipeline("text-classification", model="bert-base-uncased")

def analyze_text(dom):
    """Analyze page text and form labels using NLP model."""
    issues = []
    # Example: check each form label for meaningfulness
    for label in dom.find_all("label"):
        text = label.get_text().strip()
        if text:
            result = text_classifier(text)[0]
            # If classifier predicts negative (score < threshold), flag it
            if result['label'] == 'LABEL_0' and result['score'] < 0.5:
                issues.append({"type": "PoorLabelText", "node": "label", "details": text})
    return issues
