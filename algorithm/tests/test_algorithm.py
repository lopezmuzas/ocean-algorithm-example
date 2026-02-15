"""Integration tests for the algorithm entry point."""

import pytest
from algorithm import algorithm, AgeAlgorithm
from shared.domain.algorithm_interface import AlgorithmInterface


class TestAlgorithm:
    """Test suite for algorithm entry point."""
    
    def test_algorithm_instance_exists(self):
        """Test that the algorithm instance is created."""
        assert algorithm is not None
    
    def test_algorithm_has_validate_decorator(self):
        """Test that algorithm has validate decorator."""
        assert hasattr(algorithm, 'validate')
    
    def test_algorithm_has_run_decorator(self):
        """Test that algorithm has run decorator."""
        assert hasattr(algorithm, 'run')
    
    def test_algorithm_has_save_results_decorator(self):
        """Test that algorithm has save_results decorator."""
        assert hasattr(algorithm, 'save_results')
    
    def test_algorithm_is_callable(self):
        """Test that algorithm instance is callable."""
        assert callable(algorithm)
    
    def test_age_algorithm_implements_interface(self):
        """Test that AgeAlgorithm implements AlgorithmInterface."""
        # Create an instance using the factory method
        age_algorithm = AgeAlgorithm.create()
        
        # Verify it implements the interface
        assert isinstance(age_algorithm, AlgorithmInterface)
        
        # Verify it has all required methods
        assert hasattr(age_algorithm, 'validate')
        assert hasattr(age_algorithm, 'run')
        assert hasattr(age_algorithm, 'save')
        
        # Verify methods are callable
        assert callable(age_algorithm.validate)
        assert callable(age_algorithm.run)
        assert callable(age_algorithm.save)
    
    def test_algorithm_interface_polymorphism(self):
        """Test that AlgorithmInterface enables polymorphism."""
        from shared.domain.algorithm_interface import AlgorithmInterface
        
        # Create an instance
        age_algorithm = AgeAlgorithm.create()
        
        # Verify it can be treated as the interface type
        algorithm_interface: AlgorithmInterface = age_algorithm
        
        # Verify the interface contract is maintained
        assert hasattr(algorithm_interface, 'validate')
        assert hasattr(algorithm_interface, 'run')
        assert hasattr(algorithm_interface, 'save')
        
        # This demonstrates that different algorithm implementations
        # could be used interchangeably through the interface
