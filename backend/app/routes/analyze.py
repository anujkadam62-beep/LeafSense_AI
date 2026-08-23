"""
/analyze route.

Flow: upload -> validate content-type -> save a copy to disk (for
audit/debugging) -> preprocess -> run inference -> return JSON.

Status codes:
    200 - success
    400 - invalid/corrupted/unsupported image
    500 - model not available or unexpected internal error
"""

import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.services.prediction import run_prediction
from app.utils.exceptions import InvalidImageError, ModelNotAvailableError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB, matches the frontend's stated limit


@router.post("/analyze")
async def analyze_leaf(file: UploadFile = File(...)):
    """
    Accepts a coffee leaf image and returns disease detection,
    confidence, severity, and the full class probability distribution.
    """
    # --- 1. Validate up front (cheap checks before touching the model) ---
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{file.content_type}'. "
            "Upload a JPG, PNG, or WEBP image.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # --- 2. Archive the upload (best-effort; failure here shouldn't block analysis) ---
    try:
        file_id = uuid.uuid4().hex
        destination = UPLOAD_DIR / f"{file_id}_{file.filename}"
        destination.write_bytes(contents)
    except OSError:
        logger.warning("Could not save uploaded file to disk; continuing with in-memory bytes.")

    # --- 3. Preprocess + run inference ---
    try:
        result = run_prediction(image_bytes=contents)
        return result

    except InvalidImageError as exc:
        logger.info("Rejected invalid image upload: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    except ModelNotAvailableError as exc:
        logger.error("Model unavailable during /analyze: %s", exc)
        return JSONResponse(status_code=500, content={"error": str(exc)})

    except Exception as exc:  # noqa: BLE001 - last line of defense
        logger.exception("Unexpected error during analysis")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal error during analysis: {exc}"},
        )
