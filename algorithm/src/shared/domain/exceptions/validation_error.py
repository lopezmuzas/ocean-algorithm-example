"""Validation error exception."""

from .algorithm_error import AlgorithmError


class ValidationError(AlgorithmError):
    """Raised when input validation fails."""
    pass