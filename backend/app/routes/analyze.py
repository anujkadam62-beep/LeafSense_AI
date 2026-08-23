"""
/analyze route.

Flow:
    upload -> validate -> save upload -> run prediction -> return JSON.

Status codes:
    200 - Success
    400 - Invalid or unsupported image
    500 - Model unavailable or internal server error
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.prediction import run_prediction
from app.utils.exceptions import InvalidImageError, ModelNotAvailableError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])

# Store uploaded files for debugging/audit
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/analyze")
async def analyze_leaf(file: UploadFile = File(...)):
    """
    Analyze a coffee leaf image.

    Returns:
        - predicted class
        - confidence
        - severity
        - class probabilities
    """

    # -------------------------------------------------------
    # Validate content type
    # -------------------------------------------------------

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Upload a JPG, PNG, or WEBP image."
            ),
        )

    # -------------------------------------------------------
    # Read uploaded file
    # -------------------------------------------------------

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum allowed size is 10 MB.",
        )

    # -------------------------------------------------------
    # Save upload (best effort)
    # -------------------------------------------------------

    try:
        safe_name = Path(file.filename).name if file.filename else "image"
        destination = UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_name}"
        destination.write_bytes(contents)

        logger.info("Saved upload to %s", destination)

    except OSError as exc:
        logger.warning("Could not save uploaded image: %s", exc)

    # -------------------------------------------------------
    # Run prediction
    # -------------------------------------------------------

    try:
        result = run_prediction(image_bytes=contents)
        return JSONResponse(status_code=200, content=result)

    except InvalidImageError as exc:
        logger.info("Invalid image rejected: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except ModelNotAvailableError as exc:
        logger.error("Model unavailable: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )

    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error during prediction")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {exc}"},
        )