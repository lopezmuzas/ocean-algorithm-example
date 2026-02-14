"""File operation error exception."""

from .algorithm_error import AlgorithmError


class FileOperationError(AlgorithmError):
    """Raised when file operations fail."""
    pass