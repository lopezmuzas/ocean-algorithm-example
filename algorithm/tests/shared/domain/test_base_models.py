"""Tests for shared domain models."""

import pytest
from pydantic import ValidationError
from src.shared.domain import InputParameters, Results


class TestInputParameters:
    """Test suite for base InputParameters model."""
    
    def test_create_base_input_parameters(self):
        """Test creating base InputParameters."""
        params = InputParameters()
        assert params is not None


class TestResults:
    """Test suite for base Results model."""
    
    def test_create_base_results(self):
        """Test creating base Results with status and message."""
        results = Results(
            status="success",
            message="Test message"
        )
        
        assert results.status == "success"
        assert results.message == "Test message"
    
    def test_base_results_json_serialization(self):
        """Test JSON serialization of base Results."""
        import json
        
        results = Results(
            status="success",
            message="Test message"
        )
        
        json_str = results.model_dump_json()
        assert "success" in json_str
        assert "Test message" in json_str
        
        parsed = json.loads(json_str)
        assert parsed["status"] == "success"
        assert parsed["message"] == "Test message"
