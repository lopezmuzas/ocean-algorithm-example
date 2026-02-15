from pathlib import Path
from ocean_runner import Algorithm, Config

from age_average.application.calculate_age_statistics_action import CalculateAgeStatisticsAction
from age_average.domain.age_input_parameters import AgeInputParameters
from age_average.domain.age_results import AgeResults
from age_average.application.input_parser import InputParser
from age_average.application.age_statistics_calculator import AgeStatisticsCalculator
from shared.domain.config.app_config import AppConfig
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.calculation_error import CalculationError
from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.domain.results import Results
from shared.infrastructure.request import Request
from shared.infrastructure.response import Response
from shared.infrastructure.file_reader import FileReader
from shared.infrastructure.result_writer import ResultWriter
from shared.infrastructure.base_algorithm import BaseAlgorithm


class AgeAlgorithm(BaseAlgorithm):
    """
    Object-oriented implementation of the age averaging algorithm.
    
    Implements the AlgorithmInterface through BaseAlgorithm to provide a contract
    for Ocean Protocol algorithms, following SOLID principles and enabling polymorphism.
    Returns AgeResults that extend the base Results class.
    """
    
    def __init__(
        self,
        config: AppConfig,
        ocean_algorithm: Algorithm,
        request: Request,
        response: Response,
        calculate_action: CalculateAgeStatisticsAction,
    ):
        super().__init__()  # Initialize base algorithm
        self.config = config
        self.algorithm = ocean_algorithm
        self.request = request  # Set for base class generic validations
        self.response = response
        self.calculate_action = calculate_action
        
        # Register callbacks with the ocean_runner framework
        self.register_callbacks(ocean_algorithm)
    
    @classmethod
    def create(cls, config: AppConfig) -> "AgeAlgorithm":
        """
        Factory method to create an AgeAlgorithm instance with default dependencies.
        
        Args:
            config: AppConfig instance (required).
        
        Returns:
            AgeAlgorithm instance with all dependencies properly initialized
        """
        ocean_algorithm = Algorithm(config=Config(custom_input=AgeInputParameters))
        file_reader = FileReader(ocean_algorithm.logger)
        result_writer = ResultWriter(ocean_algorithm.logger)
        request = Request(ocean_algorithm, file_reader)
        response = Response(result_writer)
        
        # Create domain services
        input_parser = InputParser(ocean_algorithm.logger)
        stats_calculator = AgeStatisticsCalculator(ocean_algorithm.logger)
        
        # Create action with injected dependencies
        calculate_action = CalculateAgeStatisticsAction(
            request=request,
            input_parser=input_parser,
            stats_calculator=stats_calculator,
        )
        
        return cls(
            config=config,
            ocean_algorithm=ocean_algorithm,
            request=request,
            response=response,
            calculate_action=calculate_action,
        )
    
    def validate_input(self, algo: Algorithm) -> None:
        algo.logger.info("validate: starting")
        try:
            input_count = self.request.count()
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

        This method delegates to the CalculateAgeStatisticsAction to perform
        the actual business logic of calculating age statistics. The action
        handles all exceptions internally and returns appropriate results.

        Args:
            algo: Algorithm instance with job details and logger

        Returns:
            AgeResults with calculated statistics or error status
        """
        algo.logger.info("run: starting")
        
        # Delegate business logic to the action (handles all exceptions internally)
        return self.calculate_action.execute()
    
    def save(
        self,
        algo: Algorithm,
        results: Results,
        base_path: Path,
    ) -> None:
        """
        Save algorithm results to outputs folder.

        Args:
            algo: Algorithm instance with logger
            results: Results object to save
            base_path: Base directory for output files
        """
        algo.logger.info("save: starting")

        try:
            # Write results to configured output file
            output_filename = self.config.output.filename
            output_file = base_path / output_filename
            self.response.write_results(results, output_file)

        except FileOperationError as e:
            algo.logger.error(f"Failed to save results: {e}")
            raise
        except Exception as e:
            algo.logger.error(f"Unexpected error during save: {e}")
            raise
    
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


# Create algorithm instance using factory method
algorithm = AgeAlgorithm.create(AppConfig.load()).algorithm


if __name__ == "__main__":
    algorithm()
