"""
Algorithm entry point.

This module coordinates the algorithm execution using services and following SOLID principles:
- Single Responsibility: Each service has one clear purpose
- Open/Closed: Services can be extended without modifying this code
- Dependency Inversion: Depends on abstractions (services), not implementations
"""

from pathlib import Path
from ocean_runner import Algorithm, Config

from age_average.domain.age_input_parameters import AgeInputParameters
from age_average.domain.age_results import AgeResults
from age_average.services.input_parser import InputParser
from age_average.services.age_statistics_calculator import AgeStatisticsCalculator
from age_average.infrastructure.file_reader import FileReader
from age_average.infrastructure.result_writer import ResultWriter
from shared.domain.config.app_config import AppConfig
from shared.domain.exceptions.algorithm_error import AlgorithmError
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.calculation_error import CalculationError
from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.infrastructure.performance.performance_monitor import PerformanceMonitor


class AgeAlgorithm:
    """
    Object-oriented implementation of the age averaging algorithm.
    
    Encapsulates the algorithm logic with proper initialization and method organization.
    """
    
    def __init__(self):
        """Initialize the algorithm with configuration and services."""
        self.config = AppConfig.load()
        self.algorithm = Algorithm(config=Config(custom_input=AgeInputParameters))
        self.performance_monitor = PerformanceMonitor(self.algorithm.logger)
        
        # Register callbacks with the ocean_runner framework
        self.algorithm.validate(self.validate)
        self.algorithm.run(self.run)
        self.algorithm.save_results(self.save)
    
    def validate(self, algo: Algorithm) -> None:
        """
        Validate input data before processing.
        
        Args:
            algo: Algorithm instance with job details
        """
        algo.logger.info("validate: starting")
        try:
            # Check if we have input files
            input_count = len(list(algo.job_details.inputs()))
            if input_count == 0:
                raise ValidationError("No input files provided")
            
            algo.logger.info(f"Found {input_count} input files to process")
            
        except ValidationError as e:
            algo.logger.error(f"Validation failed: {e}")
            raise
        except Exception as e:
            algo.logger.error(f"Unexpected validation error: {e}")
            raise
    
    def run(self, algo: Algorithm) -> AgeResults:
        """
        Execute the main algorithm logic.

        This function coordinates services to:
        1. Read input files
        2. Parse and extract age data
        3. Calculate statistics
        4. Return results

        Args:
            algo: Algorithm instance with job details and logger

        Returns:
            AgeResults object with calculated statistics
        """
        algo.logger.info("run: starting")

        try:
            # Initialize services (Dependency Injection)
            file_reader = FileReader(algo.logger)
            input_parser = InputParser(algo.logger)
            stats_calculator = AgeStatisticsCalculator(algo.logger)

            # Extract ages from all input files
            all_ages = []
            for idx, path in algo.job_details.inputs():
                algo.logger.info(f"Processing input {idx}: {path.name}")
                text = file_reader.read_text(path)
                ages = input_parser.extract_ages(text, path.name)
                all_ages.extend(ages)

            # Calculate statistics
            stats = stats_calculator.calculate(all_ages)

            # Build and return results
            return AgeResults(
                status="success",
                message="Algorithm executed successfully",
                min_age=stats.min_age,
                max_age=stats.max_age,
                avg_age=stats.avg_age,
            )
            
        except ValidationError as e:
            return self._handle_error(algo, e, "Validation failed")
        except ParsingError as e:
            return self._handle_error(algo, e, "Failed to parse input data")
        except CalculationError as e:
            return self._handle_error(algo, e, "Failed to calculate statistics")
        except FileOperationError as e:
            return self._handle_error(algo, e, "File operation failed")
        except Exception as e:
            return self._handle_error(algo, e, "Unexpected error")
    
    def save(
        self,
        algo: Algorithm,
        results: AgeResults,
        base_path: Path,
    ) -> None:
        """
        Save algorithm results to storage.

        Args:
            algo: Algorithm instance with logger
            results: AgeResults object to save
            base_path: Base directory for output files
        """
        algo.logger.info("save: starting")

        try:
            # Initialize writer service
            writer = ResultWriter(algo.logger)

            # Write results to JSON file
            output_file = base_path / "results.json"
            writer.write_json(results, output_file)

            # Log final performance metrics
            self.performance_monitor.log_final_metrics()

        except FileOperationError as e:
            algo.logger.error(f"Failed to save results: {e}")
            raise
        except Exception as e:
            algo.logger.error(f"Unexpected error during save: {e}")
            raise FileOperationError(f"Failed to save results: {e}")
    
    def _handle_error(self, algo: Algorithm, error: Exception, context: str) -> AgeResults:
        """
        Centralized error handling for the run method.
        
        Args:
            algo: Algorithm instance with logger
            error: The exception that was raised
            context: Context description for the error
            
        Returns:
            AgeResults object with error status
        """
        algo.logger.error(f"{context}: {error}")
        return AgeResults(
            status="error",
            message=f"{context}: {error}",
            min_age=0,
            max_age=0,
            avg_age=0.0,
        )


# Create algorithm instance
algorithm = AgeAlgorithm().algorithm


if __name__ == "__main__":
    algorithm()
