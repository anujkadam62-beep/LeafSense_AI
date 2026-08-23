"""
Coffee Leaf AI — FastAPI backend entrypoint.

Loads the trained model once on startup and exposes:

- /health
- /analyze
- /evaluate
- /evaluate/latest
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import model_loader
from app.routes import analyze, evaluate, health
from app.services.evaluation import run_default_evaluation
from app.utils.logger import configure_logging

# -------------------------------------------------------
# Configure logging
# -------------------------------------------------------

configure_logging()
logger = logging.getLogger(__name__)

# -------------------------------------------------------
# FastAPI app
# -------------------------------------------------------

app = FastAPI(
    title="Coffee Leaf AI API",
    description="Coffee Leaf Disease Detection & Severity Estimation Backend",
    version="0.2.0",
)

# -------------------------------------------------------
# CORS (GitHub Codespaces Frontend)
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*-3000\.app\.github\.dev",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Routes
# -------------------------------------------------------

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(evaluate.router)

# -------------------------------------------------------
# Startup
# -------------------------------------------------------

@app.on_event("startup")
def load_model_on_startup() -> None:
    """
    Load the trained model once when FastAPI starts and
    automatically evaluate the bundled validation dataset.
    """

    loaded = model_loader.try_preload()

    if loaded:
        logger.info("Startup: model preloaded successfully.")

        try:
            run_default_evaluation()
            logger.info("Automatic validation evaluation completed.")
        except Exception as exc:
            logger.warning("Automatic evaluation skipped: %s", exc)

    else:
        logger.warning(
            "Startup: model weights not loaded. "
            "/analyze and /evaluate will not work until "
            "backend/app/models/coffee_leaf_model.pth is available."
        )


# -------------------------------------------------------
# Root endpoint
# -------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "Coffee Leaf AI API",
        "status": "running",
        "model_loaded": model_loader.is_model_loaded(),
        "docs": "/docs",
    }