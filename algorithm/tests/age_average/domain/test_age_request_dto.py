"""Unit tests for AgeRequestDTO model."""

import pytest
from pydantic import ValidationError
from shared.domain.request_dto import RequestDTO
from age_average.domain.age_request_dto import AgeRequestDTO


class TestAgeRequestDTO:
    """Test suite for AgeRequestDTO model."""
    
    def test_create_valid_input_parameters(self):
        """Test creating AgeRequestDTO with valid data."""
        params = AgeRequestDTO(user_id=5, age=25)
        
        assert params.user_id == 5
        assert params.age == 25
    
    def test_input_parameters_validation(self):
        """Test that AgeRequestDTO validates types correctly."""
        # Should accept integers
        params = AgeRequestDTO(user_id=10, age=30)
        assert isinstance(params.user_id, int)
        assert isinstance(params.age, int)
    
    def test_invalid_input_parameters(self):
        """Test that invalid data raises ValidationError."""
        with pytest.raises(ValidationError):
            AgeRequestDTO(user_id="invalid", age=25)
    
    def test_input_parameters_serialization(self):
        """Test JSON serialization of AgeRequestDTO."""
        params = AgeRequestDTO(user_id=5, age=25)
        json_data = params.model_dump_json()
        
        assert "5" in json_data
        assert "25" in json_data
    
    def test_age_input_parameters_inherits_from_base(self):
        """Test that AgeRequestDTO inherits from RequestDTO."""
        params = AgeRequestDTO(user_id=5, age=25)
        assert isinstance(params, RequestDTO)
