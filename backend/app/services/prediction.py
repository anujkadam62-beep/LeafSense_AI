"""
Prediction service.

Pipeline:
1. Preprocess image for the AI model.
2. Run PyTorch inference.
3. Segment the leaf.
4. Detect affected region.
5. Extract HSV, Shape, Texture and Edge features.
6. Return a complete dashboard-ready response.
"""

from __future__ import annotations

import base64
import logging
import time

import torch
import torch.nn.functional as F

from app.models import model_loader
from app.services.feature_extraction import extract_features
from app.services.image_processing import (
    encode_png,
    preprocess_image,
    segment_leaf,
)

logger = logging.getLogger(__name__)

# ---------------------------------------
# Severity thresholds
# ---------------------------------------

SEVERITY_HIGH_THRESHOLD = 85.0
SEVERITY_MODERATE_THRESHOLD = 60.0

HEALTHY_LABEL = "healthy"


def _estimate_severity(disease: str, confidence: float) -> str:
    """Healthy leaves have no severity."""

    if disease.lower() == HEALTHY_LABEL:
        return "None"

    if confidence >= SEVERITY_HIGH_THRESHOLD:
        return "High"

    if confidence >= SEVERITY_MODERATE_THRESHOLD:
        return "Moderate"

    return "Low"


def _to_base64(image_bytes: bytes) -> str:
    """Encode PNG bytes for frontend display."""
    return base64.b64encode(image_bytes).decode("utf-8")


def run_prediction(image_bytes: bytes) -> dict:
    """
    Complete prediction pipeline.
    """

    start = time.perf_counter()

    # -----------------------------------
    # AI preprocessing
    # -----------------------------------

    tensor = preprocess_image(image_bytes)

    model = model_loader.get_model()
    device = model_loader.get_device()
    labels = model_loader.load_labels()

    tensor = tensor.to(device)

    logger.info(
        "Prediction started (device=%s, input_shape=%s)",
        device,
        tuple(tensor.shape),
    )

    # -----------------------------------
    # Model inference
    # -----------------------------------

    with torch.no_grad():
        logits = model(tensor)
        probabilities = F.softmax(logits, dim=1)[0]

    top_index = int(torch.argmax(probabilities).item())

    disease = labels[top_index]

    confidence = round(float(probabilities[top_index].item()) * 100, 1)

    probability_breakdown = {
        labels[idx]: round(float(prob.item()) * 100, 1)
        for idx, prob in enumerate(probabilities)
    }

    severity = _estimate_severity(disease, confidence)

    # -----------------------------------
    # Segmentation
    # -----------------------------------

    (
        original,
        segmented,
        affected,
        leaf_mask,
        affected_mask,
        area_stats,
    ) = segment_leaf(image_bytes)

    # -----------------------------------
    # Feature Extraction
    # -----------------------------------

    features = extract_features(segmented, leaf_mask)

    # -----------------------------------
    # Encode images
    # -----------------------------------

    segmented_b64 = _to_base64(encode_png(segmented))
    affected_b64 = _to_base64(encode_png(affected))

    elapsed_ms = round((time.perf_counter() - start) * 1000)

    logger.info(
        "Prediction completed: %s %.1f%% (%dms)",
        disease,
        confidence,
        elapsed_ms,
    )

    # -----------------------------------
    # Final response
    # -----------------------------------

    return {
        "prediction": disease.title(),
        "confidence": confidence,
        "severity": severity,
        "processing_time_ms": elapsed_ms,

        "probabilities": probability_breakdown,

        "affected_area": {
            "pixels": area_stats["affected_pixels"],
            "leaf_pixels": area_stats["leaf_pixels"],
            "percentage": area_stats["percentage"],
        },

        "features": features,

        "images": {
            "segmented": segmented_b64,
            "affected": affected_b64,
        },
    }