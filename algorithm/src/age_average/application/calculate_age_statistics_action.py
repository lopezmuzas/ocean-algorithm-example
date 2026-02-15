"""Action for calculating age statistics from input files."""

from pathlib import Path
from typing import List

from age_average.domain.age_results import AgeResults
from age_average.application.input_parser import InputParser
from age_average.application.age_statistics_calculator import AgeStatisticsCalculator
from shared.infrastructure.request import Request
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.calculation_error import CalculationError
from shared.domain.exceptions.file_operation_error import FileOperationError


class CalculateAgeStatisticsAction:
    """
    Action that orchestrates the calculation of age statistics from input files.
    
    This action encapsulates the business logic for:
    1. Reading and parsing input files
    2. Extracting age data
    3. Calculating statistics
    4. Returning results
    
    Follows SOLID DIP: all dependencies injected via constructor.
    """
    
    def __init__(
        self,
        request: Request,
        input_parser: InputParser,
        stats_calculator: AgeStatisticsCalculator,
    ):
        """
        Initialize action with required dependencies.
        
        Args:
            request: Request instance for accessing input files
            input_parser: Parser for extracting ages from text
            stats_calculator: Calculator for computing age statistics
        """
        self.request = request
        self.input_parser = input_parser
        self.stats_calculator = stats_calculator
    
    def execute(self) -> AgeResults:
        """
        Execute the age statistics calculation.
        
        Returns:
            AgeResults with calculated statistics or error status
            
        Note:
            This method handles all exceptions internally and returns
            appropriate error results instead of raising exceptions.
        """
        try:
            # Extract ages from all input files
            all_ages: List[int] = []
            
            for idx, path in self.request.iter_files():
                text = self.request.file_reader.read_text(path)
                ages = self.input_parser.extract_ages(text, path.name)
                all_ages.extend(ages)
            
            # Calculate statistics
            stats = self.stats_calculator.calculate(all_ages)
            
            # Return results
            return AgeResults(
                status="success",
                message="Algorithm executed successfully",
                min_age=stats.min_age,
                max_age=stats.max_age,
                avg_age=stats.avg_age,
            )
            
        except ValidationError as e:
            return AgeResults(
                status="error",
                message=f"Validation failed: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except ParsingError as e:
            return AgeResults(
                status="error",
                message=f"Failed to parse input data: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except CalculationError as e:
            return AgeResults(
                status="error",
                message=f"Failed to calculate statistics: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except FileOperationError as e:
            return AgeResults(
                status="error",
                message=f"File operation failed: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except Exception as e:
            return AgeResults(
                status="error",
                message=f"Unexpected error: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )