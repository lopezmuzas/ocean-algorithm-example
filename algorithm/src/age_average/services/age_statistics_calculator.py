"""Service for calculating age statistics."""

from logging import Logger
from ..domain.age_statistics import AgeStatistics
from src.shared.domain.exceptions.validation_error import ValidationError
from src.shared.domain.exceptions.calculation_error import CalculationError


class AgeStatisticsCalculator:
    """
    Calculates statistical metrics for age data.
    
    Follows Single Responsibility Principle - only handles age statistics.
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def calculate(self, ages: list[int]) -> AgeStatistics:
        """
        Calculate age statistics from a list of ages.
        
        Args:
            ages: List of age values
            
        Returns:
            AgeStatistics object with calculated metrics
            
        Raises:
            ValidationError: If ages list is None or contains invalid values
            CalculationError: If statistical calculation fails
        """
        if ages is None:
            raise ValidationError("Ages list cannot be None")
        
        if not isinstance(ages, list):
            raise ValidationError("Ages must be provided as a list")
        
        if not ages:
            raise ValidationError("Cannot calculate statistics for empty ages list")
        
        # Validate all ages are integers and within reasonable range
        for age in ages:
            if not isinstance(age, int):
                raise ValidationError(f"All ages must be integers, got {type(age)}: {age}")
            if age < 0 or age > 150:
                raise ValidationError(f"Age {age} is outside valid range (0-150)")
        
        try:
            min_age = min(ages)
            max_age = max(ages)
            avg_age = sum(ages) / len(ages)
            
            self.logger.info(
                f"Calculated statistics for {len(ages)} ages: "
                f"Min={min_age}, Max={max_age}, Avg={avg_age:.2f}"
            )
            
            return AgeStatistics(
                min_age=min_age,
                max_age=max_age,
                avg_age=avg_age,
                count=len(ages)
            )
        except Exception as e:
            raise CalculationError(f"Failed to calculate age statistics: {e}")
