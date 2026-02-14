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
from src.shared.domain.exceptions import AlgorithmError, ValidationError, ParsingError, CalculationError, FileOperationError

algorithm = Algorithm(config=Config(custom_input=AgeInputParameters))


@algorithm.validate
def validate(algo: Algorithm) -> None:
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
        raise ValidationError(f"Validation failed: {e}")


@algorithm.run
def run(algo: Algorithm) -> AgeResults:
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
            
            # Read file content
            text = file_reader.read_text(path)
            
            # Parse and extract ages
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


@algorithm.save_results
def save(
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
        
    except FileOperationError as e:
        algo.logger.error(f"Failed to save results: {e}")
        raise
    except Exception as e:
        algo.logger.error(f"Unexpected error during save: {e}")
        raise FileOperationError(f"Failed to save results: {e}")


if __name__ == "__main__":
    algorithm()
