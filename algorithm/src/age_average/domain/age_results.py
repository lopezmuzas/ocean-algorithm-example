"""Age-specific results."""

from src.shared.domain.results import Results


class AgeResults(Results):
    """Results for the age statistics algorithm."""
    min_age: int
    max_age: int
    avg_age: float
