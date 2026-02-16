"""Tests for shared domain models."""

import pytest
from pydantic import ValidationError
from shared.domain.request_dto import RequestDTO
from shared.domain.response_dto import ResponseDTO


class TestRequestDTO:
    """Test suite for base RequestDTO model."""
    
    def test_create_base_input_parameters(self):
        """Test creating base RequestDTO."""
        params = RequestDTO()
        assert params is not None


class TestResponseDTO:
    """Test suite for base ResponseDTO model."""
    
    def test_create_base_response_dto(self):
        """Test creating base ResponseDTO with status and message."""
        response = ResponseDTO(
            status="success",
            message="Test message"
        )
        
        assert response.status == "success"
        assert response.message == "Test message"
    
    def test_base_results_json_serialization(self):
        """Test JSON serialization of base Results."""
        import json
        
        results = ResponseDTO(
            status="success",
            message="Test message"
        )
        
        json_str = results.model_dump_json()
        assert "success" in json_str
        assert "Test message" in json_str
        
        parsed = json.loads(json_str)
        assert parsed["status"] == "success"
        assert parsed["message"] == "Test message"
