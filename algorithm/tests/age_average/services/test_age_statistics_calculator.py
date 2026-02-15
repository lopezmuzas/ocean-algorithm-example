"""Unit tests for AgeStatisticsCalculator service."""

import logging
import pytest
from age_average.services.age_statistics_calculator import AgeStatisticsCalculator
from age_average.domain.age_statistics import AgeStatistics
from shared.domain.exceptions.validation_error import ValidationError


class TestAgeStatisticsCalculator:
    """Test suite for AgeStatisticsCalculator service."""
    
    @pytest.fixture
    def logger(self):
        """Create a logger for testing."""
        return logging.getLogger("test")
    
    @pytest.fixture
    def calculator(self, logger):
        """Create an AgeStatisticsCalculator instance for testing."""
        return AgeStatisticsCalculator(logger)
    
    def test_calculate_with_valid_ages(self, calculator):
        """Test calculating statistics with valid age data."""
        ages = [20, 25, 30, 35, 40]
        
        stats = calculator.calculate(ages)
        
        assert stats.min_age == 20
        assert stats.max_age == 40
        assert stats.avg_age == 30.0
        assert stats.count == 5
    
    def test_calculate_with_single_age(self, calculator):
        """Test calculating statistics with a single age."""
        ages = [25]
        
        stats = calculator.calculate(ages)
        
        assert stats.min_age == 25
        assert stats.max_age == 25
        assert stats.avg_age == 25.0
        assert stats.count == 1
    
    def test_calculate_with_empty_list(self, calculator):
        """Test that empty age list raises ValidationError."""
        ages = []
        
        with pytest.raises(ValidationError):
            calculator.calculate(ages)
    
    def test_calculate_with_same_ages(self, calculator):
        """Test calculating statistics when all ages are the same."""
        ages = [30, 30, 30, 30]
        
        stats = calculator.calculate(ages)
        
        assert stats.min_age == 30
        assert stats.max_age == 30
        assert stats.avg_age == 30.0
        assert stats.count == 4
    
    def test_calculate_with_decimal_average(self, calculator):
        """Test that average is calculated as float with decimals."""
        ages = [10, 20, 25]
        
        stats = calculator.calculate(ages)
        
        assert stats.min_age == 10
        assert stats.max_age == 25
        assert stats.avg_age == pytest.approx(18.333, rel=1e-2)
        assert stats.count == 3
    
    def test_calculate_with_large_dataset(self, calculator):
        """Test calculating statistics with a large dataset."""
        ages = list(range(1, 101))  # Ages from 1 to 100
        
        stats = calculator.calculate(ages)
        
        assert stats.min_age == 1
        assert stats.max_age == 100
        assert stats.avg_age == 50.5
        assert stats.count == 100
    
    def test_age_statistics_dataclass(self):
        """Test AgeStatistics dataclass creation."""
        stats = AgeStatistics(
            min_age=20,
            max_age=50,
            avg_age=35.5,
            count=10
        )
        
        assert stats.min_age == 20
        assert stats.max_age == 50
        assert stats.avg_age == 35.5
        assert stats.count == 10
