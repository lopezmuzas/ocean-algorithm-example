"""Base Results model."""

from pydantic import BaseModel


class Results(BaseModel):
    """Base class for algorithm execution results."""
    status: str
    message: str
