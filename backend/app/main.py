"""
LeafSense AI — FastAPI backend entrypoint.

Provides:
- /health
- /analyze
- /evaluate
- /evaluate/latest

Optimized for Render Free:
- No model preloading at startup.
- Model loads automatically on the first prediction request.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import model_loader
from app.routes import analyze, evaluate, health
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
    title="LeafSense AI API",
    description="Universal Plant Leaf Disease Detection & Severity Estimation Backend",
    version="0.2.0",
)

# -------------------------------------------------------
# CORS
# -------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://leafsense-ai-spz7.onrender.com",
    ],
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
def startup() -> None:
    """
    Keep startup lightweight for Render Free.

    The model will be loaded automatically on the first
    prediction request through model_loader.get_model().
    """
    logger.info("LeafSense AI backend started successfully.")
    logger.info("Model will be loaded on the first prediction request.")

# -------------------------------------------------------
# Root endpoint
# -------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "LeafSense AI API",
        "status": "running",
        "model_loaded": model_loader.is_model_loaded(),
        "docs": "/docs",
    }