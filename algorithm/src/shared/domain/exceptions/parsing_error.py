"""Parsing error exception."""

from .algorithm_error import AlgorithmError


class ParsingError(AlgorithmError):
    """Raised when data parsing fails."""
    pass