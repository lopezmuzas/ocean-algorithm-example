from pathlib import Path
import traceback
from typing import Optional
from ocean_runner import Algorithm

from age_average.application.calculate_age_statistics_action import CalculateAgeStatisticsAction
from age_average.infrastructure.user_age_ocean_repository import UserAgeOceanRepository
from age_average.infrastructure.user_age_mapper import UserAgeMapper
from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.age_response_dto import AgeResponseDTO
from shared.domain.config.app_config import AppConfig
from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.domain.exceptions.validation_error import ValidationError
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
        self._validation_error: Optional[Exception] = None  # Store validation errors
        
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
        Validate custom parameters from Ocean Protocol.
        
        Captures validation errors without raising exceptions. Errors are stored
        in _validation_error and will be converted to error ResponseDTO in run().
        
        Args:
            algo: Ocean Protocol algorithm instance
        """
        try:
            algo.logger.info("validate: starting - validating custom parameters")
            
            # Get custom parameters from both sources
            params = self.request.get_custom_parameters()        
            age = params.get('age')
            
            if age is None:
                algo.logger.error("Validation failed: Missing required parameter 'age'")
                raise ValidationError("Missing required parameter: age")
            
            algo.logger.info(f"Validation successful - age parameter: {age}")
            
        except Exception as e:
            # Capture error and log traceback
            algo.logger.error(f"Validation error: {e}")
            algo.logger.error(f"Validation error traceback:\n{traceback.format_exc()}")
            self._validation_error = e
    
    def run(self, algo: Algorithm) -> AgeResponseDTO:
        """
        Execute the main algorithm logic with comprehensive error handling.

        This method ensures that a ResponseDTO is ALWAYS returned:
        - Validation error: Returns error DTO from validation failure
        - Success: AgeResponseDTO with calculated statistics
        - Runtime error: AgeResponseDTO with error status and message
        
        All exceptions are caught, logged with full traceback, and converted
        to error response DTOs.

        Args:
            algo: Algorithm instance with job details and logger

        Returns:
            AgeResponseDTO: Always returns a DTO (success or error)
        """
        algo.logger.info("run: starting")
        
        # Check if validation failed
        if self._validation_error:
            algo.logger.info("Returning error response due to validation failure")
            return AgeResponseDTO(
                status="error",
                message=f"Validation error: {str(self._validation_error)}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
        
        try:
            # Delegate business logic to the action
            result = self.calculate_action.execute()
            algo.logger.info(f"Algorithm completed successfully: {result.status}")
            return result
            
        except Exception as e:
            # Catch-all for any unexpected errors
            algo.logger.error(f"Unexpected error in algorithm execution: {e}")
            algo.logger.error(f"Full traceback:\n{traceback.format_exc()}")
            return AgeResponseDTO(
                status="error",
                message=f"Algorithm error: {str(e)}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )
    
    def save(
        self,
        algo: Algorithm,
        results: ResponseDTO,
        base_path: Path,
    ) -> None:
        """
        Save algorithm results to outputs folder with error handling.
        
        Writes the ResponseDTO (success or error) to the output file.
        If saving fails, logs the error with full traceback but doesn't
        crash the algorithm.

        Args:
            algo: Algorithm instance with logger
            results: ResponseDTO object to save (can be success or error)
            base_path: Base directory for output files
        """
        algo.logger.info("save: starting")

        try:
            # Write results to configured output file
            output_filename = self.config.output.filename
            output_file = base_path / output_filename
            self.response.write_results(results, output_file)
            algo.logger.info(f"Results saved successfully to {output_file}")

        except FileOperationError as e:
            algo.logger.error(f"Failed to save results: {e}")
            algo.logger.error(f"File operation error traceback:\n{traceback.format_exc()}")
            raise
            
        except Exception as e:
            algo.logger.error(f"Unexpected error during save: {e}")
            algo.logger.error(f"Full traceback:\n{traceback.format_exc()}")
            raise
