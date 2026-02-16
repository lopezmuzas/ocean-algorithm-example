"""Base ResponseDTO model."""

from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class ResponseDTO(BaseModel, Generic[T]):
    """Generic base class for algorithm execution response DTOs."""
    status: str
    message: str
    data: T = None
