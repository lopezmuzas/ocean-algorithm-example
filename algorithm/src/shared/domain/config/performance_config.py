"""Performance configuration model."""

from pydantic import BaseModel, Field


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    batch_size: int = Field(default=1000, gt=0)
    timeout_seconds: int = Field(default=300, gt=0)