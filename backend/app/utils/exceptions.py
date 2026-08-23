"""
Custom exceptions for the inference pipeline.

Routes catch these and translate them into the correct HTTP status
codes (see app/routes/analyze.py), so services can raise a specific,
descriptive error without knowing anything about HTTP.
"""


class InvalidImageError(ValueError):
    """Raised when an uploaded file isn't a valid, decodable image."""


class ModelNotAvailableError(RuntimeError):
    """Raised when inference is requested but no trained weights are loaded."""


class EvaluationDatasetError(ValueError):
    """Raised when an uploaded validation dataset is missing, malformed,
    or doesn't contain usable images for any known class."""
