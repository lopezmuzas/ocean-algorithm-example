"""Algorithm configuration model."""

from pydantic import BaseModel, Field


class AlgorithmConfig(BaseModel):
    """Algorithm configuration settings."""
    name: str = Field(..., description="Algorithm name")
    version: str = Field(..., description="Algorithm version")
    description: str = Field(..., description="Algorithm description")