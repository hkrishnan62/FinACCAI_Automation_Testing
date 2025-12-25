from transformers import pipeline
from PIL import Image

# Load an image-to-text model (e.g. a ViT+Transformer captioner)
caption_pipeline = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning")

def generate_image_caption(image_path):
    """Generate a caption for the given image."""
    image = Image.open(image_path).convert("RGB")
    captions = caption_pipeline(image)[0]['generated_text']
    return captions

def analyze_images(dom, screenshot):
    """Run vision analysis on images from the page."""
    issues = []
    for img in dom.find_all("img"):
        src = img.get("src", "")
        if img.get("alt") == "":
            # Missing alt: try to generate one
            alt_suggestion = generate_image_caption(src)
            issues.append({"type": "MissingAltWithCaption", "node": img.name, "suggestion": alt_suggestion})
    return issues
