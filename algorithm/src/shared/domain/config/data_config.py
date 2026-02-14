"""Data processing configuration model."""

from typing import List
from pydantic import BaseModel, Field, field_validator


class DataConfig(BaseModel):
    """Data processing configuration."""
    supported_formats: List[str] = Field(default_factory=lambda: ["json"])
    max_file_size_mb: int = Field(default=100, gt=0)
    age_range: dict = Field(default_factory=lambda: {"min": 0, "max": 150})

    @field_validator('supported_formats')
    @classmethod
    def validate_formats(cls, v):
        allowed = ["json", "csv", "xml"]
        for fmt in v:
            if fmt not in allowed:
                raise ValueError(f"Unsupported format: {fmt}. Allowed: {allowed}")
        return v

    @field_validator('age_range')
    @classmethod
    def validate_age_range(cls, v):
        if 'min' not in v or 'max' not in v:
            raise ValueError("age_range must contain 'min' and 'max' keys")
        if v['min'] >= v['max']:
            raise ValueError("age_range min must be less than max")
        return v