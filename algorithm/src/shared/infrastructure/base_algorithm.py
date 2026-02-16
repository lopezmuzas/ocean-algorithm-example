"""
Base algorithm implementation providing common functionality for Ocean Protocol algorithms.

This module provides a base class that implements common algorithm functionality
like performance monitoring, while maintaining the interface contract.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from ocean_runner import Algorithm

from shared.domain.algorithm_interface import AlgorithmInterface
from shared.domain.response_dto import ResponseDTO
from shared.infrastructure.performance.performance_monitor import PerformanceMonitor


class BaseAlgorithm(AlgorithmInterface, ABC):
    """
    Base implementation of AlgorithmInterface providing common functionality.
    
    This abstract base class implements the AlgorithmInterface and provides
    common functionality like performance monitoring that all algorithms can use.
    Concrete algorithm implementations should inherit from this class and
    implement the abstract methods: validate, run, and save.
    """
    
    def __init__(self):
        """Initialize the base algorithm."""
        self.performance_monitor = None
        self.request = None  # Will be set by concrete algorithms
    
    # Note: `_create_common_dependencies` removed. Bounded contexts should create
    # their own dependencies (e.g. `AlgorithmDependencies` in each context) or
    # use a central composition root. This keeps `shared` minimal and avoids
    # coupling infrastructure wiring into the shared package.
    
    def register_callbacks(self, algorithm: Algorithm) -> None:
        """
        Register algorithm callbacks with the Ocean Protocol framework.
        
        Args:
            algorithm: Ocean Protocol algorithm instance
        """
        algorithm.validate(self.validate)
        algorithm.run(self.run)
        algorithm.save_results(self.save_results)
    
    def validate(self, algo: Algorithm) -> None:
        """
        Validate input data before processing.
        
        This method automatically:
        1. Starts performance monitoring
        2. Performs generic input validations (infrastructure level)
        3. Delegates to concrete algorithm's specific validations
        
        Args:
            algo: Algorithm instance with job details
        """
        # Start performance monitoring automatically
        self.start_performance_monitoring(algo)
        
        # Perform generic input validations at infrastructure level
        if self.request is not None:
            self.request.validate_inputs()
        
        # Delegate to concrete algorithm implementation for business-specific validations
        self.validate_input(algo)
    
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
        
        This method should be implemented by concrete algorithms to perform
        their specific saving logic. Performance monitoring is automatically
        stopped after the concrete implementation completes.
        
        Args:
            algo: Algorithm instance with logger
            results: ResponseDTO object to save
            base_path: Base directory for output files
            
        Raises:
            FileOperationError: If saving fails
        """
        pass
    
    def save_results(self, algo: Algorithm, results: ResponseDTO, base_path: Path) -> None:
        """
        Template method that wraps the concrete save implementation.
        
        Automatically stops performance monitoring after saving completes.
        
        Args:
            algo: Algorithm instance with logger
            results: ResponseDTO object to save
            base_path: Base directory for output files
        """
        try:
            # Delegate to concrete algorithm implementation
            self.save(algo, results, base_path)
        finally:
            # Always stop performance monitoring, even if save fails
            self.stop_performance_monitoring(algo)
    
    def start_performance_monitoring(self, algo: Algorithm) -> None:
        """
        Start performance monitoring for the algorithm execution.
        
        Args:
            algo: Algorithm instance with logger
        """
        # PerformanceMonitor starts monitoring automatically in its constructor
        self.performance_monitor = PerformanceMonitor(algo.logger)
    
    def stop_performance_monitoring(self, algo: Algorithm) -> None:
        """
        Stop performance monitoring and log final metrics.
        
        Args:
            algo: Algorithm instance with logger
        """
        if self.performance_monitor is not None:
            self.performance_monitor.log_final_metrics()