"""
Feature extraction for Coffee Leaf AI.

Calculates:
- Color (HSV)
- Shape
- Texture (GLCM)
- Edge
"""

from __future__ import annotations

import cv2
import numpy as np

from skimage.feature import graycomatrix, graycoprops


def extract_features(segmented_bgr, leaf_mask):
    """
    Returns a dictionary containing all dashboard features.
    """

    hsv = cv2.cvtColor(segmented_bgr, cv2.COLOR_BGR2HSV)

    mask = leaf_mask > 0

    # -----------------------------
    # Color Features
    # -----------------------------
    if np.any(mask):
        mean_h = float(np.mean(hsv[:, :, 0][mask]))
        mean_s = float(np.mean(hsv[:, :, 1][mask]) / 255)
        mean_v = float(np.mean(hsv[:, :, 2][mask]) / 255)
    else:
        mean_h = mean_s = mean_v = 0.0

    # -----------------------------
    # Shape Features
    # -----------------------------
    contours, _ = cv2.findContours(
        leaf_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    area = perimeter = aspect_ratio = 0

    if contours:
        c = max(contours, key=cv2.contourArea)

        area = float(cv2.contourArea(c))
        perimeter = float(cv2.arcLength(c, True))

        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = float(w / h) if h else 0

    # -----------------------------
    # Texture Features
    # -----------------------------
    gray = cv2.cvtColor(segmented_bgr, cv2.COLOR_BGR2GRAY)

    gray_masked = gray.copy()
    gray_masked[~mask] = 0

    glcm = graycomatrix(
        gray_masked,
        distances=[1],
        angles=[0],
        levels=256,
        symmetric=True,
        normed=True,
    )

    contrast = float(graycoprops(glcm, "contrast")[0, 0])
    correlation = float(graycoprops(glcm, "correlation")[0, 0])
    homogeneity = float(graycoprops(glcm, "homogeneity")[0, 0])

    # -----------------------------
    # Edge Features
    # -----------------------------
    edges = cv2.Canny(gray_masked, 100, 200)

    total_edges = int(np.count_nonzero(edges))

    edge_density = (
        float(total_edges / np.count_nonzero(mask))
        if np.count_nonzero(mask)
        else 0
    )

    gradient = cv2.Laplacian(gray_masked, cv2.CV_64F)
    mean_gradient = float(np.mean(np.abs(gradient)))

    return {
        "color": {
            "mean_hue": round(mean_h, 2),
            "mean_saturation": round(mean_s, 2),
            "mean_value": round(mean_v, 2),
        },
        "shape": {
            "leaf_area": round(area, 2),
            "perimeter": round(perimeter, 2),
            "aspect_ratio": round(aspect_ratio, 2),
        },
        "texture": {
            "contrast": round(contrast, 3),
            "correlation": round(correlation, 3),
            "homogeneity": round(homogeneity, 3),
        },
        "edge": {
            "edge_density": round(edge_density, 3),
            "total_edges": total_edges,
            "mean_gradient": round(mean_gradient, 3),
        },
    }