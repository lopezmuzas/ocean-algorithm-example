"""Integration tests for the algorithm entry point."""

import pytest
from algorithm import algorithm


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
