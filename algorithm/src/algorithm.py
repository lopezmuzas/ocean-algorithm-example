"""
Algorithm entry point.

This module coordinates the algorithm execution using services and following SOLID principles:
- Single Responsibility: Each service has one clear purpose
- Open/Closed: Services can be extended without modifying this code
- Dependency Inversion: Depends on abstractions (services), not implementations
"""

from pathlib import Path
from ocean_runner import Algorithm, Config

from src.age_average.domain import AgeInputParameters, AgeResults
from src.age_average.services import InputParser, AgeStatisticsCalculator
from src.age_average.infrastructure import FileReader, ResultWriter
from src.shared.domain import AppConfig
from src.shared.domain.exceptions import AlgorithmError, ValidationError, ParsingError, CalculationError, FileOperationError
from src.shared.infrastructure import PerformanceMonitor


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
        
        self.algorithm.validate(self._create_validate_callback())
        self.algorithm.run(self._create_run_callback())
        self.algorithm.save_results(self._create_save_callback())
    
    def _create_validate_callback(self):
        """Create a callback function for validation."""
        def validate_callback(algo: Algorithm) -> None:
            self.validate(algo)
        return validate_callback
    
    def _create_run_callback(self):
        """Create a callback function for running the algorithm."""
        def run_callback(algo: Algorithm) -> AgeResults:
            return self.run(algo)
        return run_callback
    
    def _create_save_callback(self):
        """Create a callback function for saving results."""
        def save_callback(algo: Algorithm, results: AgeResults, base_path: Path) -> None:
            self.save(algo, results, base_path)
        return save_callback
    
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
            algo.logger.error(f"Input validation error: {e}")
            return AgeResults(
                status="error",
                message=f"Validation failed: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except ParsingError as e:
            algo.logger.error(f"Data parsing error: {e}")
            return AgeResults(
                status="error",
                message=f"Failed to parse input data: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except CalculationError as e:
            algo.logger.error(f"Statistics calculation error: {e}")
            return AgeResults(
                status="error",
                message=f"Failed to calculate statistics: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except FileOperationError as e:
            algo.logger.error(f"File operation error: {e}")
            return AgeResults(
                status="error",
                message=f"File operation failed: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        except Exception as e:
            algo.logger.error(f"Unexpected error during execution: {e}")
            return AgeResults(
                status="error",
                message=f"Unexpected error: {e}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
    
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
            metrics = self.performance_monitor.get_metrics()
            algo.logger.info(
                f"Total execution time: {metrics.execution_time_seconds:.3f}s | "
                f"Memory: {metrics.memory_usage_mb:.2f}MB | "
                f"Peak: {metrics.peak_memory_usage_mb:.2f}MB | "
                f"CPU: {metrics.cpu_percent:.2f}%"
            )

        except FileOperationError as e:
            algo.logger.error(f"Failed to save results: {e}")
            raise
        except Exception as e:
            algo.logger.error(f"Unexpected error during save: {e}")
            raise FileOperationError(f"Failed to save results: {e}")


# Create algorithm instance
algorithm = AgeAlgorithm().algorithm


if __name__ == "__main__":
    algorithm()
