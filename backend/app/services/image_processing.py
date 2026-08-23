"""
Image preprocessing + leaf segmentation.

Responsibilities:
- Validate uploaded image
- Prepare tensor for the AI model
- Generate leaf mask
- Generate segmented leaf image
- Generate affected-region image
- Calculate affected area percentage

The preprocessing (224x224 + ImageNet normalization) matches the
training pipeline used for coffee_leaf_model.pth.
"""

from __future__ import annotations

import io

import cv2
import numpy as np
import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

from app.utils.exceptions import InvalidImageError

IMAGE_SIZE = 224

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

_transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
])

SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

def _validate_decodable(file_bytes: bytes):
    arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if img is None:
        raise InvalidImageError("Uploaded file is not a valid image.")


def _open_image(file_bytes: bytes):

    try:
        probe = Image.open(io.BytesIO(file_bytes))
        probe.verify()
    except (UnidentifiedImageError, OSError, ValueError) as e:
        raise InvalidImageError(f"Corrupted image: {e}") from e

    image = Image.open(io.BytesIO(file_bytes))

    fmt = (image.format or "").upper()

    if fmt not in SUPPORTED_FORMATS:
        raise InvalidImageError(
            f"Unsupported format '{fmt}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    return image.convert("RGB")


# -------------------------------------------------------
# Model preprocessing
# -------------------------------------------------------

def preprocess_image(file_bytes: bytes) -> torch.Tensor:
    """
    Returns:
        Tensor shape (1,3,224,224)
    """

    if not file_bytes:
        raise InvalidImageError("Empty file uploaded.")

    _validate_decodable(file_bytes)

    image = _open_image(file_bytes)

    tensor = _transform(image)

    return tensor.unsqueeze(0)


# -------------------------------------------------------
# Leaf segmentation
# -------------------------------------------------------

def segment_leaf(file_bytes: bytes):
    """
    Returns:
        original_bgr
        segmented_bgr
        affected_bgr
        leaf_mask
        affected_mask
        stats
    """

    arr = np.frombuffer(file_bytes, np.uint8)
    original = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    hsv = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)

    # Green leaf mask
    lower_green = np.array([25, 30, 30])
    upper_green = np.array([95, 255, 255])

    leaf_mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((7, 7), np.uint8)

    leaf_mask = cv2.morphologyEx(
        leaf_mask,
        cv2.MORPH_OPEN,
        kernel
    )

    leaf_mask = cv2.morphologyEx(
        leaf_mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        leaf_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        largest = max(contours, key=cv2.contourArea)

        leaf_mask = np.zeros_like(leaf_mask)

        cv2.drawContours(
            leaf_mask,
            [largest],
            -1,
            255,
            thickness=-1
        )

    segmented = cv2.bitwise_and(original, original, mask=leaf_mask)

    # Disease colors (yellow/brown)
    lower_disease = np.array([5, 40, 40])
    upper_disease = np.array([35, 255, 255])

    disease_mask = cv2.inRange(hsv, lower_disease, upper_disease)

    affected_mask = cv2.bitwise_and(disease_mask, leaf_mask)

    affected = original.copy()

    affected[affected_mask > 0] = (0, 0, 255)

    leaf_pixels = int(cv2.countNonZero(leaf_mask))
    affected_pixels = int(cv2.countNonZero(affected_mask))

    percentage = (
        round((affected_pixels / leaf_pixels) * 100, 2)
        if leaf_pixels else 0
    )

    stats = {
        "leaf_pixels": leaf_pixels,
        "affected_pixels": affected_pixels,
        "percentage": percentage,
    }

    return (
        original,
        segmented,
        affected,
        leaf_mask,
        affected_mask,
        stats,
    )


# -------------------------------------------------------
# Encoding helper
# -------------------------------------------------------

def encode_png(image):
    ok, buffer = cv2.imencode(".png", image)

    if not ok:
        raise RuntimeError("Failed to encode image.")

    return buffer.tobytes()