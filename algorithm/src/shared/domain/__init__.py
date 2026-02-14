"""Shared domain models."""

from .input_parameters import InputParameters
from .results import Results
from .exceptions import AlgorithmError, ValidationError, ParsingError, CalculationError, FileOperationError

__all__ = [
    "InputParameters",
    "Results",
    "AlgorithmError",
    "ValidationError",
    "ParsingError",
    "CalculationError",
    "FileOperationError"
]
