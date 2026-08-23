"""
Model evaluation service.

Computes REAL metrics by running the currently-loaded model over the
bundled validation dataset or an uploaded ZIP.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support

from app.models import model_loader
from app.services.image_processing import preprocess_image
from app.utils.exceptions import EvaluationDatasetError, InvalidImageError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
RESULTS_PATH = MODELS_DIR / "evaluation_results.json"
CONFUSION_MATRIX_PATH = MODELS_DIR / "evaluation_confusion_matrix.png"

# backend/validation_dataset
VALIDATION_DATASET = Path(__file__).resolve().parents[2] / "validation_dataset"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MAX_ZIP_SIZE_BYTES = 500 * 1024 * 1024
MAX_IMAGES = 5000

# Dataset folder aliases
CLASS_ALIASES = {
    "healthy": "Healthy",
    "unhealthy": "Unhealthy",
    "coffee leaf rust": "Unhealthy",
    "rust": "Unhealthy",
}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _find_class_dirs(root: Path, labels: Dict[int, str]) -> Dict[str, Path]:
    valid_names = set(labels.values())

    def scan(base: Path):
        found = {}

        if not base.is_dir():
            return found

        for child in base.iterdir():
            if not child.is_dir():
                continue

            folder = child.name.lower().strip()

            if folder in CLASS_ALIASES:
                mapped = CLASS_ALIASES[folder]
                if mapped in valid_names:
                    found[mapped] = child

        return found

    found = scan(root)
    if found:
        return found

    for sub in root.iterdir():
        if sub.is_dir():
            found = scan(sub)
            if found:
                return found

    return {}


def _extract_zip(zip_bytes: bytes, dest: Path):
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            zf.extractall(dest)
    except zipfile.BadZipFile as exc:
        raise EvaluationDatasetError("Uploaded file is not a valid ZIP.") from exc


def _create_zip_from_folder(folder: Path) -> bytes:
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in folder.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(folder))

    buffer.seek(0)
    return buffer.read()


def _plot_confusion_matrix(matrix: np.ndarray, class_names: List[str]) -> bytes:
    fig, ax = plt.subplots(figsize=(5, 4), dpi=150)

    im = ax.imshow(matrix, cmap="Greens")

    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix")

    vmax = matrix.max() if matrix.size else 1

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(
                j,
                i,
                str(int(matrix[i, j])),
                ha="center",
                va="center",
                color="white" if matrix[i, j] > vmax / 2 else "black",
            )

    fig.colorbar(im, fraction=0.046, pad=0.04)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)

    return buf.getvalue()

# ---------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------

def run_evaluation(zip_bytes: bytes, skip_size_check: bool = False) -> dict:

    if not zip_bytes:
        raise EvaluationDatasetError("Uploaded file is empty.")

    if not skip_size_check and len(zip_bytes) > MAX_ZIP_SIZE_BYTES:
        raise EvaluationDatasetError(
            f"Dataset exceeds {MAX_ZIP_SIZE_BYTES // (1024 * 1024)} MB."
        )

    model = model_loader.get_model()
    device = model_loader.get_device()
    labels = model_loader.load_labels()

    class_names = [labels[i] for i in sorted(labels)]
    name_to_index = {name.lower(): idx for idx, name in labels.items()}

    start = time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="coffee_eval_") as tmp:

        tmp_path = Path(tmp)

        _extract_zip(zip_bytes, tmp_path)

        class_dirs = _find_class_dirs(tmp_path, labels)

        if not class_dirs:
            raise EvaluationDatasetError(
                f"Couldn't find class folders. Expected folders like: Healthy, Coffee Leaf Rust"
            )

        y_true = []
        y_pred = []

        per_class_counts = {name: 0 for name in class_names}
        skipped = 0

        for class_name, folder in class_dirs.items():

            true_index = name_to_index[class_name.lower()]

            for img_path in sorted(folder.rglob("*")):

                if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue

                if len(y_true) >= MAX_IMAGES:
                    break

                try:
                    tensor = preprocess_image(img_path.read_bytes()).to(device)
                except (InvalidImageError, OSError):
                    skipped += 1
                    continue

                with torch.no_grad():
                    logits = model(tensor)
                    pred = int(torch.argmax(F.softmax(logits, dim=1)[0]).item())

                y_true.append(true_index)
                y_pred.append(pred)
                per_class_counts[class_name] += 1

        if not y_true:
            raise EvaluationDatasetError("No readable images found.")

        indices = sorted(labels)

        matrix = confusion_matrix(y_true, y_pred, labels=indices)

        precision, recall, f1, support = precision_recall_fscore_support(
            y_true,
            y_pred,
            labels=indices,
            zero_division=0,
        )

        accuracy = float(np.trace(matrix) / matrix.sum()) if matrix.sum() else 0.0

        confusion_png = _plot_confusion_matrix(matrix, class_names)
        confusion_b64 = base64.b64encode(confusion_png).decode()

        elapsed = round((time.perf_counter() - start) * 1000)

        result = {
            "model": "EfficientNet-B0 (coffee_leaf_model.pth)",
            "class_names": class_names,
            "accuracy": round(accuracy, 4),
            "precision": round(float(np.mean(precision)), 4),
            "recall": round(float(np.mean(recall)), 4),
            "f1": round(float(np.mean(f1)), 4),
            "per_class": [
                {
                    "class_name": class_names[i],
                    "precision": round(float(precision[i]), 4),
                    "recall": round(float(recall[i]), 4),
                    "f1": round(float(f1[i]), 4),
                    "support": int(support[i]),
                }
                for i in range(len(class_names))
            ],
            "confusion_matrix": matrix.tolist(),
            "confusion_matrix_image": confusion_b64,
            "dataset": {
                "total_images_evaluated": len(y_true),
                "per_class_counts": per_class_counts,
                "skipped_unreadable": skipped,
            },
            "processing_time_ms": elapsed,
            "evaluated_at": time.time(),
        }

        try:
            MODELS_DIR.mkdir(exist_ok=True)
            RESULTS_PATH.write_text(json.dumps(result), encoding="utf-8")
            CONFUSION_MATRIX_PATH.write_bytes(confusion_png)
        except OSError:
            logger.warning("Couldn't cache evaluation files.")

        logger.info(
            "Evaluation complete: %.2f%% accuracy on %d images.",
            accuracy * 100,
            len(y_true),
        )

        return result

# ---------------------------------------------------------------------
# Automatic evaluation
# ---------------------------------------------------------------------

def run_default_evaluation():
    """Runs automatically using backend/validation_dataset."""

    if RESULTS_PATH.exists():
        logger.info("Using cached evaluation results.")
        return get_latest_evaluation()

    if not VALIDATION_DATASET.exists():
        logger.warning("Validation dataset not found: %s", VALIDATION_DATASET)
        return None

    logger.info("Running bundled validation dataset evaluation...")

    zip_bytes = _create_zip_from_folder(VALIDATION_DATASET)

    return run_evaluation(zip_bytes, skip_size_check=True)

# ---------------------------------------------------------------------
# Cached results
# ---------------------------------------------------------------------

def get_latest_evaluation():

    if not RESULTS_PATH.exists():
        return None

    try:
        return json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None