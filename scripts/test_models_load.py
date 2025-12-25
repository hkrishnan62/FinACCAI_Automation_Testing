from pathlib import Path

print("\n[FinAccAI] Running model load verification...\n")

# --------------------------
# Test ML Classifier
# --------------------------
try:
    import joblib
    clf = joblib.load("models/ml_classifier.pkl")
    print("✓ ML Classifier loaded successfully")
except Exception as e:
    print("❌ ML Classifier failed:", e)

# --------------------------
# Test NLP Model (BERT)
# --------------------------
try:
    from transformers import BertModel
    bert = BertModel.from_pretrained("models/nlp_model")
    print("✓ BERT NLP model loaded successfully")
except Exception as e:
    print("❌ NLP Model failed:", e)

# --------------------------
# Test Vision Caption Model
# --------------------------
try:
    from transformers import VisionEncoderDecoderModel
    vision = VisionEncoderDecoderModel.from_pretrained(
        "models/vision_caption_model"
    )
    print("✓ Vision Caption model loaded successfully")
except Exception as e:
    print("❌ Vision Caption Model failed:", e)

print("\n[FinAccAI] Model load validation complete.\n")
