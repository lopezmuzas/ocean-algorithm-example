"""Age statistics data model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AgeStatistics:
    """Container for age statistics results."""
    min_age: int
    max_age: int
    avg_age: float
    count: int
