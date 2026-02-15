"""Age-specific input parameters."""

from shared.domain.input_parameters import InputParameters


class AgeInputParameters(InputParameters):
    """Custom input parameters for the age statistics algorithm."""
    num: int
    age: int
