"""Age-specific input parameters."""

from src.shared.domain import InputParameters


class AgeInputParameters(InputParameters):
    """Custom input parameters for the age statistics algorithm."""
    num: int
    age: int
