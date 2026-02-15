"""Unit tests for InputParser service."""

import json
import logging
import pytest
from age_average.services.input_parser import InputParser
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.validation_error import ValidationError


class TestInputParser:
    """Test suite for InputParser service."""
    
    @pytest.fixture
    def logger(self):
        """Create a logger for testing."""
        return logging.getLogger("test")
    
    @pytest.fixture
    def parser(self, logger):
        """Create an InputParser instance for testing."""
        return InputParser(logger)
    
    def test_extract_ages_from_array_format(self, parser):
        """Test extracting ages from array of objects format."""
        json_text = json.dumps([
            {"user_id": 1, "age": 25},
            {"user_id": 2, "age": 30},
            {"user_id": 3, "age": 35}
        ])
        
        ages = parser.extract_ages(json_text, "test.json")
        
        assert ages == [25, 30, 35]
    
    def test_extract_ages_from_ages_field_format(self, parser):
        """Test extracting ages from object with ages field."""
        json_text = json.dumps({
            "ages": [20, 25, 30, 35, 40]
        })
        
        ages = parser.extract_ages(json_text, "test.json")
        
        assert ages == [20, 25, 30, 35, 40]
    
    def test_extract_ages_from_mixed_array(self, parser):
        """Test extracting ages from array with some missing age fields."""
        json_text = json.dumps([
            {"user_id": 1, "age": 25},
            {"user_id": 2, "name": "John"},  # No age field
            {"user_id": 3, "age": 35}
        ])
        
        ages = parser.extract_ages(json_text, "test.json")
        
        assert ages == [25, 35]
    
    def test_extract_ages_invalid_json(self, parser):
        """Test that invalid JSON raises ParsingError."""
        invalid_json = "not valid json {"
        
        with pytest.raises(ParsingError):
            parser.extract_ages(invalid_json, "test.json")
    
    def test_extract_ages_empty_data(self, parser):
        """Test that empty data structures raise ValidationError."""
        # Empty array
        json_text = json.dumps([])
        with pytest.raises(ValidationError):
            parser.extract_ages(json_text, "test.json")
        
        # Empty ages field
        json_text = json.dumps({"ages": []})
        with pytest.raises(ValidationError):
            parser.extract_ages(json_text, "test.json")
    
    def test_extract_ages_no_age_field(self, parser):
        """Test that data without age fields raises ValidationError."""
        json_text = json.dumps({
            "data": "some data",
            "count": 5
        })
        
        with pytest.raises(ValidationError):
            parser.extract_ages(json_text, "test.json")
    
    def test_extract_ages_with_non_integer_ages(self, parser):
        """Test that non-integer ages raise ValidationError."""
        json_text = json.dumps([
            {"user_id": 1, "age": 25},
            {"user_id": 2, "age": "thirty"}  # String instead of int
        ])
        
        with pytest.raises(ValidationError):
            parser.extract_ages(json_text, "test.json")
