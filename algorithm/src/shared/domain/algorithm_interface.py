"""Algorithm interface definition."""

from abc import ABC, abstractmethod
from pathlib import Path

from ocean_runner import Algorithm
from shared.domain.response_dto import ResponseDTO
class AlgorithmInterface(ABC):
    """
    Interface that all Ocean Protocol algorithms must implement.
    
    This interface defines the contract that any algorithm must follow,
    enabling polymorphism and dependency inversion. All algorithms return
    ResponseDTO objects for consistent handling.
    """
    
    @abstractmethod
    def validate_input(self, algo: Algorithm) -> None:
        """
        Validate input data before processing.
        
        This method should be implemented by concrete algorithms to perform
        their specific input validation logic.
        
        Args:
            algo: Algorithm instance with job details
            
        Raises:
            ValidationError: If validation fails
        """
        pass
    
    @abstractmethod
    def run(self, algo: Algorithm) -> ResponseDTO:
        """
        Execute the main algorithm logic.
        
        Args:
            algo: Algorithm instance with job details and logger
            
        Returns:
            ResponseDTO of the algorithm execution
        """
        pass
    
    @abstractmethod
    def save(self, algo: Algorithm, results: ResponseDTO, base_path: Path) -> None:
        """
        Save algorithm results to storage.
        
        Args:
            algo: Algorithm instance with logger
            results: ResponseDTO object to save
            base_path: Base directory for output files
            
        Raises:
            FileOperationError: If saving fails
        """
        pass