# finaccai/xai_explanations.py
import shap
from lime.lime_tabular import LimeTabularExplainer
import numpy as np

def explain_ml_with_shap(model, background_data, instance):
    """Explain ML prediction using SHAP."""
    explainer = shap.Explainer(model.predict, background_data)
    shap_values = explainer(instance)
    shap_summary = shap_values.values[0]
    return shap_summary  # feature contributions

def explain_ml_with_lime(model, train_data, feature_names, instance):
    """Explain ML prediction using LIME."""
    explainer = LimeTabularExplainer(train_data, feature_names=feature_names, verbose=False)
    exp = explainer.explain_instance(instance, model.predict_proba)
    return exp.as_list()

# Grad-CAM for an example CNN (assuming PyTorch model)
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
import torch

def explain_image_with_gradcam(torch_model, input_tensor, target_layer, original_image):
    """Generate a Grad-CAM heatmap for the input image."""
    cam = GradCAM(model=torch_model, target_layer=target_layer, use_cuda=False)
    grayscale_cam = cam(input_tensor)
    visualization = show_cam_on_image(np.array(original_image)/255.0, grayscale_cam[0], use_rgb=True)
    return visualization  # an image with heatmap overlay
