from pathlib import Path
from ocean_runner import Algorithm

from age_average.application.calculate_age_statistics_action import CalculateAgeStatisticsAction
from age_average.infrastructure.user_age_ocean_repository import UserAgeOceanRepository
from age_average.infrastructure.user_age_mapper import UserAgeMapper
from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.age_response_dto import AgeResponseDTO
from shared.domain.config.app_config import AppConfig
from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.domain.response_dto import ResponseDTO
from shared.infrastructure.algorithm_dependencies import AlgorithmDependencies
from shared.infrastructure.base_algorithm import BaseAlgorithm


class AgeAverageAlgorithm(BaseAlgorithm):
    """
    Object-oriented implementation of the age averaging algorithm.
    
    Implements the AlgorithmInterface through BaseAlgorithm to provide a contract
    for Ocean Protocol algorithms, following SOLID principles and enabling polymorphism.
    Returns AgeResponseDTO that extend the base ResponseDTO class.
    """
    
    def __init__(
        self,
        deps: AlgorithmDependencies,
        calculate_action: CalculateAgeStatisticsAction,
        config: AppConfig,
    ):
        super().__init__()  # Initialize base algorithm
        self.config = config
        self.algorithm = deps.ocean_algorithm
        self.request = deps.request  # Set for base class generic validations
        self.response = deps.response
        self.calculate_action = calculate_action
        
        # Register callbacks with the ocean_runner framework
        self.register_callbacks(deps.ocean_algorithm)
    
    @classmethod
    def create(cls, config: AppConfig) -> "AgeAverageAlgorithm":
        """
        Factory method to create an AgeAverageAlgorithm instance with default dependencies.
        
        This method serves as the Composition Root for the age_average bounded context,
        wiring together all dependencies (infrastructure, application, domain layers).
        
        Design Pattern: Factory Method + Dependency Injection
        - Creates all infrastructure dependencies (Ocean Protocol adapters)
        - Assembles application layer (Actions/Use Cases)
        - Injects everything through constructor
        
        Args:
            config: AppConfig instance (required).
        
        Returns:
            AgeAverageAlgorithm instance with all dependencies properly initialized
        
        Note:
            This is the composition root for this bounded context. Entry point
            (algorithm.py) delegates to this method to maintain separation of concerns.
        """
        # Create common infrastructure dependencies
        deps = AlgorithmDependencies.create(AgeRequestDTO)
        
        # Chain de construcción de dependencias específicas
        mapper = UserAgeMapper()
        repository = UserAgeOceanRepository(deps.request, mapper)
        action = CalculateAgeStatisticsAction(repository)
        
        return cls(deps, action, config)
    
    def validate_input(self, algo: Algorithm) -> None:
        """
        Placeholder for input validation.
        
        As a test algorithm, no actual validation is performed.
        Use self.request to access input files and metadata for validation if needed.
        
        Args:
            algo: Ocean Protocol algorithm instance
        """
        algo.logger.info("validate: starting - use self.request to validate inputs/metadata")
        # Placeholder: Add input/metadata validation logic here using self.request
    
    def run(self, algo: Algorithm) -> AgeResponseDTO:
        """
        Execute the main algorithm logic.

        This method delegates to the CalculateAgeStatisticsAction to perform
        the actual business logic of calculating age statistics. The action
        handles all exceptions internally and returns appropriate results.

        Args:
            algo: Algorithm instance with job details and logger

        Returns:
            AgeResponseDTO with calculated statistics or error status
        """
        algo.logger.info("run: starting")
        
        # Delegate business logic to the action (handles all exceptions internally)
        return self.calculate_action.execute()
    
    def save(
        self,
        algo: Algorithm,
        results: ResponseDTO,
        base_path: Path,
    ) -> None:
        """
        Save algorithm results to outputs folder.

        Args:
            algo: Algorithm instance with logger
            results: ResponseDTO object to save
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
    
    def _handle_error(self, algo: Algorithm, error: Exception, context: str) -> AgeResponseDTO:
        """
        Centralized error handling for the run method.
        
        Args:
            algo: Algorithm instance with logger
            error: The exception that was raised
            context: Context description for the error
            
        Returns:
            AgeResponseDTO object with error status
        """
        algo.logger.error(f"{context}: {error}")
        return AgeResponseDTO(
            status="error",
            message=f"{context}: {error}",
            min_age=0,
            max_age=0,
            avg_age=0.0,
        )
