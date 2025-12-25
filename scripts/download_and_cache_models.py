import os
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

from transformers import (
    BertTokenizer,
    BertModel,
    VisionEncoderDecoderModel,
    ViTImageProcessor,
    AutoTokenizer
)

ROOT = Path("models")
ROOT.mkdir(exist_ok=True)

# -----------------------------
# 1) Create ML classifier
# -----------------------------
print("\n[FinAccAI] Creating ML classifier...")

X, y = make_classification(
    n_samples=1200,
    n_features=20,
    n_informative=6,
    n_redundant=2,
    random_state=42
)

clf = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

clf.fit(X, y)

joblib.dump(clf, ROOT / "ml_classifier.pkl")

print("[OK] Saved models/ml_classifier.pkl")

# -----------------------------
# 2) Cache NLP model (BERT)
# -----------------------------
NLP_DIR = ROOT / "nlp_model"
NLP_DIR.mkdir(exist_ok=True)

print("\n[FinAccAI] Downloading BERT NLP model (bert-base-uncased)...")

bert_model = BertModel.from_pretrained("bert-base-uncased")
bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

bert_model.save_pretrained(NLP_DIR)
bert_tokenizer.save_pretrained(NLP_DIR)

print("[OK] Saved NLP model to models/nlp_model/")

# -----------------------------
# 3) Cache Vision Caption Model
# -----------------------------
VISION_DIR = ROOT / "vision_caption_model"
VISION_DIR.mkdir(exist_ok=True)

print("\n[FinAccAI] Downloading ViT-GPT2 Caption Model (nlpconnect/vit-gpt2-image-captioning)...")

vision_model = VisionEncoderDecoderModel.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
)

vision_processor = ViTImageProcessor.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
)

vision_tokenizer = AutoTokenizer.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
)

vision_model.save_pretrained(VISION_DIR)
vision_processor.save_pretrained(VISION_DIR)
vision_tokenizer.save_pretrained(VISION_DIR)

print("[OK] Saved Vision Caption Model to models/vision_caption_model/")

print("\n[FinAccAI] All models downloaded & cached successfully.")
