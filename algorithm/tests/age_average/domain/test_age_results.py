"""Unit tests for AgeResults model."""

import json
import pytest
from pydantic import ValidationError
from src.shared.domain.results import Results
from src.age_average.domain.age_results import AgeResults


class TestAgeResults:
    """Test suite for AgeResults model."""
    
    def test_create_valid_results(self):
        """Test creating AgeResults with valid data."""
        results = AgeResults(
            status="success",
            message="Test message",
            min_age=20,
            max_age=50,
            avg_age=35.5
        )
        
        assert results.status == "success"
        assert results.message == "Test message"
        assert results.min_age == 20
        assert results.max_age == 50
        assert results.avg_age == 35.5
    
    def test_results_with_different_values(self):
        """Test AgeResults with boundary values."""
        results = AgeResults(
            status="error",
            message="",
            min_age=0,
            max_age=100,
            avg_age=50.0
        )
        
        assert results.status == "error"
        assert results.message == ""
        assert results.min_age == 0
        assert results.max_age == 100
        assert results.avg_age == 50.0
    
    def test_results_json_serialization(self):
        """Test JSON serialization of AgeResults."""
        results = AgeResults(
            status="success",
            message="Test message",
            min_age=25,
            max_age=45,
            avg_age=33.5
        )
        
        json_str = results.model_dump_json()
        assert "success" in json_str
        assert "Test message" in json_str
        
        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert parsed["status"] == "success"
        assert parsed["min_age"] == 25
        assert parsed["max_age"] == 45
        assert parsed["avg_age"] == 33.5
    
    def test_results_json_with_indent(self):
        """Test JSON serialization with indentation."""
        results = AgeResults(
            status="success",
            message="Test",
            min_age=20,
            max_age=30,
            avg_age=25.0
        )
        
        json_str = results.model_dump_json(indent=2)
        assert "\n" in json_str  # Should have newlines with indent
        assert "  " in json_str  # Should have spaces for indentation
    
    def test_invalid_results(self):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            AgeResults(
                status="success",
                message="Test",
                min_age="invalid",  # Should be int
                max_age=50,
                avg_age=35.5
            )
    
    def test_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError):
            AgeResults(status="success")  # Missing other required fields
    
    def test_age_results_inherits_from_base(self):
        """Test that AgeResults inherits from Results."""
        results = AgeResults(
            status="success",
            message="Test",
            min_age=20,
            max_age=30,
            avg_age=25.0
        )
        assert isinstance(results, Results)
