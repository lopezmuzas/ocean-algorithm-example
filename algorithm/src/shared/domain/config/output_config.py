"""Output configuration model."""

from pydantic import BaseModel, Field, field_validator


class OutputConfig(BaseModel):
    """Output configuration."""
    format: str = Field(default="json")
    indent: int = Field(default=2, ge=0)
    encoding: str = Field(default="utf-8")

    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        allowed = ["json", "xml", "csv"]
        if v.lower() not in allowed:
            raise ValueError(f"Unsupported output format: {v}. Allowed: {allowed}")
        return v.lower()