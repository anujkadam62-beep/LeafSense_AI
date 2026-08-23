"""
Model architecture used for both training and inference.

This MUST match the architecture used to create
coffee_leaf_model.pth.
"""

from __future__ import annotations

import timm


def create_model(num_classes: int = 2):
    """
    Creates the EfficientNet-B0 classifier used during training.
    """

    model = timm.create_model(
        "efficientnet_b0",
        pretrained=False,
        num_classes=num_classes,
    )

    return model