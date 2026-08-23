"""Centralized logging setup so every module logs in a consistent format."""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Call once, at app startup, before any other module logs."""
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. re-imported under uvicorn --reload).
        root.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)
