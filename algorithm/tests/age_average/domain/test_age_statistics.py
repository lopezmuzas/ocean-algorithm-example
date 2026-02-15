"""Unit tests for AgeStatistics model."""

import pytest
from age_average.domain.age_statistics import AgeStatistics


class TestAgeStatistics:
    """Test suite for AgeStatistics model."""
    
    def test_create_age_statistics(self):
        """Test creating AgeStatistics with valid data."""
        stats = AgeStatistics(min_age=20, max_age=50, avg_age=35.5, count=10)
        
        assert stats.min_age == 20
        assert stats.max_age == 50
        assert stats.avg_age == 35.5
        assert stats.count == 10
    
    def test_age_statistics_with_zero_values(self):
        """Test AgeStatistics with zero values."""
        stats = AgeStatistics(min_age=0, max_age=0, avg_age=0.0, count=0)
        
        assert stats.min_age == 0
        assert stats.max_age == 0
        assert stats.avg_age == 0.0
        assert stats.count == 0
    
    def test_age_statistics_equality(self):
        """Test that AgeStatistics instances can be compared."""
        stats1 = AgeStatistics(min_age=20, max_age=50, avg_age=35.5, count=10)
        stats2 = AgeStatistics(min_age=20, max_age=50, avg_age=35.5, count=10)
        stats3 = AgeStatistics(min_age=10, max_age=30, avg_age=20.0, count=5)
        
        assert stats1 == stats2
        assert stats1 != stats3
    
    def test_age_statistics_immutability(self):
        """Test that AgeStatistics is frozen (immutable)."""
        stats = AgeStatistics(min_age=20, max_age=50, avg_age=35.5, count=10)
        
        with pytest.raises(Exception):
            stats.min_age = 30
