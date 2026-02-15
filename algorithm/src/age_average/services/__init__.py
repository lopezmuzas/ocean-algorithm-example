"""Services for Age Average functionality."""

from .input_parser import InputParser
from .age_statistics_calculator import AgeStatisticsCalculator
from .age_extractor import AgeExtractor

__all__ = [
    "InputParser",
    "AgeStatisticsCalculator",
    "AgeExtractor",
]
