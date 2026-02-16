"""Unit tests for UserAgeOceanRepository."""

import json
import pytest
from unittest.mock import Mock, patch

from age_average.infrastructure.user_age_ocean_repository import UserAgeOceanRepository
from age_average.infrastructure.user_age_mapper import UserAgeMapper
from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.user_age import UserAge
from shared.infrastructure.request import Request
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError


class TestUserAgeOceanRepository:
    """Test suite for UserAgeOceanRepository."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request instance."""
        mock_request = Mock(spec=Request)
        mock_request.logger = Mock()
        return mock_request

    @pytest.fixture
    def mapper(self):
        """Create a UserAgeMapper instance."""
        return UserAgeMapper()

    @pytest.fixture
    def repository(self, mock_request, mapper):
        """Create a UserAgeOceanRepository instance for testing."""
        return UserAgeOceanRepository(
            request=mock_request,
            mapper=mapper,
        )

    @pytest.fixture
    def sample_json_data(self):
        """Create sample JSON data for testing."""
        return json.dumps([
            {"user_id": 1, "age": 25},
            {"user_id": 2, "age": 30},
            {"user_id": 3, "age": 35},
        ])

    def test_get_entities_from_input_success(self, repository, mock_request, sample_json_data):
        """Test successful retrieval and mapping of user ages from input."""
        # Setup mock
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = sample_json_data

        # Execute
        repository.get_entities_from_input(AgeRequestDTO)
        result = repository.find_all()

        # Verify
        assert len(result) == 3
        assert all(isinstance(user_age, UserAge) for user_age in result)

        assert result[0].user_id == 1
        assert result[0].age == 25

        assert result[1].user_id == 2
        assert result[1].age == 30

        assert result[2].user_id == 3
        assert result[2].age == 35

        # Verify mock calls
        mock_request.validate_inputs.assert_called_once()
        mock_request.get_content.assert_called_once_with(0)

    def test_get_entities_from_input_with_empty_data(self, repository, mock_request):
        """Test handling of empty input data."""
        # Setup mock
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = "[]"

        # Execute
        repository.get_entities_from_input(AgeRequestDTO)
        result = repository.find_all()

        # Verify
        assert result == []

    def test_get_entities_from_input_validation_error(self, repository, mock_request):
        """Test that validation errors are propagated."""
        # Setup mock to raise ValidationError
        mock_request.validate_inputs.side_effect = ValidationError("No input files")

        # Execute and verify
        with pytest.raises(ValidationError, match="No input files"):
            repository.get_entities_from_input(AgeRequestDTO)

    def test_get_entities_from_input_invalid_json(self, repository, mock_request):
        """Test handling of invalid JSON data."""
        # Setup mock
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = "invalid json"

        # Execute and verify
        with pytest.raises(ParsingError, match="Failed to parse input as JSON"):
            repository.get_entities_from_input(AgeRequestDTO)

    def test_get_entities_from_input_non_array_json(self, repository, mock_request):
        """Test handling of JSON that is not an array."""
        # Setup mock
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = '{"num": 1, "age": 25}'

        # Execute and verify
        with pytest.raises(ParsingError, match="Input data must be a JSON array"):
            repository.get_entities_from_input(AgeRequestDTO)

    def test_get_entities_from_input_invalid_dto_data(self, repository, mock_request):
        """Test handling of invalid AgeRequestDTO data."""
        # Setup mock with invalid data
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = json.dumps([
            {"user_id": 1, "age": 25},
            {"user_id": "invalid", "age": 30},  # Invalid user_id
        ])

        # Execute and verify
        with pytest.raises(ValidationError, match="Invalid AgeRequestDTO data"):
            repository.get_entities_from_input(AgeRequestDTO)

    def test_find_all_returns_empty_list_initially(self, repository):
        """Test that find_all() returns empty list when no data is loaded."""
        # Execute without loading data
        result = repository.find_all()

        # Verify
        assert result == []
        assert isinstance(result, list)