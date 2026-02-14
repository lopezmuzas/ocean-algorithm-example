"""Statistics calculation configuration model."""

from pydantic import BaseModel, Field


class StatisticsConfig(BaseModel):
    """Statistics calculation configuration."""
    decimal_places: int = Field(default=2, ge=0, le=10)
    include_count: bool = Field(default=True)