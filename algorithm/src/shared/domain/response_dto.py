"""Base ResponseDTO model."""

from pydantic import BaseModel


class ResponseDTO(BaseModel):
    """Generic base class for algorithm execution response DTOs."""
    status: str
    message: str
