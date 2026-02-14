"""Calculation error exception."""

from .algorithm_error import AlgorithmError


class CalculationError(AlgorithmError):
    """Raised when statistical calculations fail."""
    pass