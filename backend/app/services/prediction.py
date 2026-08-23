"""
Prediction service.

Pipeline:
1. Preprocess image.
2. Load model lazily (first request only).
3. Run PyTorch inference.
4. Segment the leaf.
5. Extract HSV, Shape, Texture and Edge features.
6. Return a dashboard-ready response.

Optimized for Render Free:
- Torch is imported only when needed.
- Model is loaded only on the first prediction.
"""

from __future__ import annotations

import base64
import logging
import time

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
    """Estimate disease severity from prediction confidence."""

    if disease.lower() == HEALTHY_LABEL:
        return "None"

    if confidence >= SEVERITY_HIGH_THRESHOLD:
        return "High"

    if confidence >= SEVERITY_MODERATE_THRESHOLD:
        return "Moderate"

    return "Low"


def _to_base64(image_bytes: bytes) -> str:
    """Convert PNG bytes to Base64 for frontend display."""
    return base64.b64encode(image_bytes).decode("utf-8")


def run_prediction(image_bytes: bytes) -> dict:
    """
    Execute the complete prediction pipeline.

    Returns:
        Dictionary containing prediction, confidence,
        severity, affected area, extracted features,
        and processed images.
    """

    # Lazy import keeps startup lighter on Render.
    import torch
    import torch.nn.functional as F

    start = time.perf_counter()

    # ---------------------------------------
    # Preprocess image
    # ---------------------------------------

    tensor = preprocess_image(image_bytes)

    # ---------------------------------------
    # Load model (only on first request)
    # ---------------------------------------

    model = model_loader.get_model()
    device = model_loader.get_device()
    labels = model_loader.load_labels()

    tensor = tensor.to(device)

    logger.info(
        "Prediction started (device=%s, shape=%s)",
        device,
        tuple(tensor.shape),
    )

    # ---------------------------------------
    # Model inference
    # ---------------------------------------

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

    # ---------------------------------------
    # Leaf segmentation
    # ---------------------------------------

    (
        original,
        segmented,
        affected,
        leaf_mask,
        affected_mask,
        area_stats,
    ) = segment_leaf(image_bytes)

    # ---------------------------------------
    # Feature extraction
    # ---------------------------------------

    features = extract_features(segmented, leaf_mask)

    # ---------------------------------------
    # Encode images
    # ---------------------------------------

    segmented_b64 = _to_base64(encode_png(segmented))
    affected_b64 = _to_base64(encode_png(affected))

    elapsed_ms = round((time.perf_counter() - start) * 1000)

    logger.info(
        "Prediction completed: %s (%.1f%%) in %d ms",
        disease,
        confidence,
        elapsed_ms,
    )

    # ---------------------------------------
    # Response
    # ---------------------------------------

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