"""Unit tests for AgeInputParameters model."""

import pytest
from pydantic import ValidationError
from shared.domain.input_parameters import InputParameters
from age_average.domain.age_input_parameters import AgeInputParameters


class TestAgeInputParameters:
    """Test suite for AgeInputParameters model."""
    
    def test_create_valid_input_parameters(self):
        """Test creating AgeInputParameters with valid data."""
        params = AgeInputParameters(num=5, age=25)
        
        assert params.num == 5
        assert params.age == 25
    
    def test_input_parameters_validation(self):
        """Test that AgeInputParameters validates types correctly."""
        # Should accept integers
        params = AgeInputParameters(num=10, age=30)
        assert isinstance(params.num, int)
        assert isinstance(params.age, int)
    
    def test_invalid_input_parameters(self):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            AgeInputParameters(num="invalid", age=25)
    
    def test_input_parameters_serialization(self):
        """Test JSON serialization of AgeInputParameters."""
        params = AgeInputParameters(num=5, age=25)
        json_data = params.model_dump_json()
        
        assert "5" in json_data
        assert "25" in json_data
    
    def test_age_input_parameters_inherits_from_base(self):
        """Test that AgeInputParameters inherits from InputParameters."""
        params = AgeInputParameters(num=5, age=25)
        assert isinstance(params, InputParameters)
