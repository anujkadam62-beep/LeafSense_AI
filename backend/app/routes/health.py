from fastapi import APIRouter

from app.models import model_loader

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    """
    Liveness probe used by the frontend and deployment platform.

    `model_loaded` lets the frontend (or a curl check) distinguish
    "server is up" from "server is up and can actually run /analyze".
    """
    return {
        "status": "healthy",
        "model_loaded": model_loader.is_model_loaded(),
    }
