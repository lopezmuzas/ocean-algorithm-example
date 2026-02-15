"""
Base algorithm implementation providing common functionality for Ocean Protocol algorithms.

This module provides a base class that implements common algorithm functionality
like performance monitoring, while maintaining the interface contract.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from ocean_runner import Algorithm

from shared.domain.algorithm_interface import AlgorithmInterface
from shared.domain.results import Results
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
    
    def register_callbacks(self, algorithm: Algorithm) -> None:
        """
        Register algorithm callbacks with the Ocean Protocol framework.
        
        Args:
            algorithm: Ocean Protocol algorithm instance
        """
        algorithm.validate(self.validate)
        algorithm.run(self.run)
        algorithm.save_results(self.save)
    
    def validate(self, algo: Algorithm) -> None:
        """
        Validate input data before processing.
        
        This method automatically starts performance monitoring and then
        delegates to the concrete algorithm's validate_input method.
        
        Args:
            algo: Algorithm instance with job details
        """
        # Start performance monitoring automatically
        self.start_performance_monitoring(algo)
        
        # Delegate to concrete algorithm implementation
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
    def run(self, algo: Algorithm) -> Results:
        """
        Execute the main algorithm logic.
        
        Args:
            algo: Algorithm instance with job details and logger
            
        Returns:
            Results of the algorithm execution
        """
        pass
    
    @abstractmethod
    def save(self, algo: Algorithm, results: Results, base_path: Path) -> None:
        """
        Save algorithm results to storage.
        
        Args:
            algo: Algorithm instance with logger
            results: Results object to save
            base_path: Base directory for output files
            
        Raises:
            FileOperationError: If saving fails
        """
        pass
    
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