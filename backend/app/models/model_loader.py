"""
Loads the trained EfficientNet-B0 model once and reuses it for all
predictions.

Compatible with the RoCoLe 2-class model:
- Healthy
- Unhealthy
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Optional

import torch
from torch import nn

from app.models.model import create_model
from app.utils.exceptions import ModelNotAvailableError

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent
WEIGHTS_PATH = MODELS_DIR / "coffee_leaf_model.pth"
LABELS_PATH = MODELS_DIR / "labels.json"

# Used by image_processing.py
IMAGE_SIZE = 224

_model: Optional[nn.Module] = None
_labels: Optional[Dict[int, str]] = None
_device: Optional[torch.device] = None
_lock = threading.Lock()


def get_device() -> torch.device:
    global _device

    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Using device: %s", _device)

    return _device


def load_labels() -> Dict[int, str]:
    global _labels

    if _labels is not None:
        return _labels

    if not LABELS_PATH.exists():
        raise ModelNotAvailableError(f"Missing labels file: {LABELS_PATH}")

    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)

    _labels = {int(k): v for k, v in raw.items()}

    logger.info("Loaded labels: %s", list(_labels.values()))

    return _labels


def get_model() -> nn.Module:
    global _model

    if _model is not None:
        return _model

    with _lock:

        if _model is not None:
            return _model

        device = get_device()
        labels = load_labels()

        model = create_model(num_classes=len(labels))

        if not WEIGHTS_PATH.exists():
            raise ModelNotAvailableError(f"Missing model weights: {WEIGHTS_PATH}")

        checkpoint = torch.load(WEIGHTS_PATH, map_location=device)

        if isinstance(checkpoint, dict):
            if "model_state_dict" in checkpoint:
                checkpoint = checkpoint["model_state_dict"]
            elif "state_dict" in checkpoint:
                checkpoint = checkpoint["state_dict"]

        checkpoint = {
            (k[7:] if k.startswith("module.") else k): v
            for k, v in checkpoint.items()
        }

        model.load_state_dict(checkpoint)
        model.to(device)
        model.eval()

        _model = model

        logger.info("Model loaded successfully.")

        return _model


def try_preload() -> bool:
    try:
        get_model()
        return True
    except Exception as exc:
        logger.warning("Model preload failed: %s", exc)
        return False


def is_model_loaded() -> bool:
    return _model is not None