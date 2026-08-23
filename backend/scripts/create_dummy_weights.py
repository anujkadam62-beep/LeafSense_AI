"""
Generate a random-initialized coffee_leaf_model.pth for local testing.

This is NOT a trained model — predictions from it are meaningless. It
exists purely so you can run the full upload -> preprocess -> inference
-> JSON pipeline end-to-end (including the /analyze route and the
frontend) before your real model has finished training.

Usage:
    cd backend
    python scripts/create_dummy_weights.py

Replace the generated file with your real trained weights when ready
(see backend/README.md, "Placing your trained model").
"""

import json
from pathlib import Path

import torch
from torch import nn
from torchvision import models

MODELS_DIR = Path(__file__).resolve().parent.parent / "app" / "models"
LABELS_PATH = MODELS_DIR / "labels.json"
OUTPUT_PATH = MODELS_DIR / "coffee_leaf_model.pth"


def main() -> None:
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        labels = json.load(f)

    num_classes = len(labels)
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)

    torch.save(model.state_dict(), OUTPUT_PATH)
    print(f"Wrote random-initialized weights for {num_classes} classes to {OUTPUT_PATH}")
    print("Reminder: this is for pipeline testing only, not a trained model.")


if __name__ == "__main__":
    main()
