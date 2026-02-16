"""Unit tests for UserAgeMapper."""

import pytest
from typing import List

from age_average.infrastructure.user_age_mapper import UserAgeMapper
from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.user_age import UserAge
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError


class TestUserAgeMapper:
    """Test suite for UserAgeMapper."""

    @pytest.fixture
    def mapper(self):
        """Create a UserAgeMapper instance for testing."""
        return UserAgeMapper()

    @pytest.fixture
    def valid_age_requests(self) -> List[AgeRequestDTO]:
        """Create valid AgeRequestDTO objects for testing."""
        return [
            AgeRequestDTO(user_id=1, age=25),
            AgeRequestDTO(user_id=2, age=30),
            AgeRequestDTO(user_id=3, age=35),
        ]

    @pytest.fixture
    def single_age_request(self) -> List[AgeRequestDTO]:
        """Create a single AgeRequestDTO for testing."""
        return [AgeRequestDTO(user_id=1, age=25)]

    def test_map_to_entities_with_valid_data(self, mapper, valid_age_requests):
        """Test mapping valid AgeRequestDTO objects to UserAge entities."""
        result = mapper.map_to_entities(valid_age_requests)

        assert len(result) == 3
        assert all(isinstance(user_age, UserAge) for user_age in result)

        # Check first entity
        assert result[0].user_id == 1
        assert result[0].age == 25

        # Check second entity
        assert result[1].user_id == 2
        assert result[1].age == 30

        # Check third entity
        assert result[2].user_id == 3
        assert result[2].age == 35

    def test_map_to_entities_with_single_item(self, mapper, single_age_request):
        """Test mapping a single AgeRequestDTO to UserAge entity."""
        result = mapper.map_to_entities(single_age_request)

        assert len(result) == 1
        assert isinstance(result[0], UserAge)
        assert result[0].user_id == 1
        assert result[0].age == 25

    def test_map_to_entities_with_empty_list(self, mapper):
        """Test mapping an empty list returns empty list."""
        result = mapper.map_to_entities([])

        assert result == []

    def test_map_to_entities_with_none_raises_validation_error(self, mapper):
        """Test that passing None raises ValidationError."""
        with pytest.raises(ValidationError, match="Requests list cannot be None"):
            mapper.map_to_entities(None)

    def test_map_to_entities_with_non_list_raises_validation_error(self, mapper):
        """Test that passing non-list raises ValidationError."""
        with pytest.raises(ValidationError, match="Requests must be a list"):
            mapper.map_to_entities("not a list")

    def test_map_to_entities_with_missing_num_field(self, mapper):
        """Test that missing 'user_id' field raises ValidationError."""
        # Create a mock object without user_id field
        class MockRequest:
            age = 25

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="missing required field 'user_id'"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_missing_age_field(self, mapper):
        """Test that missing 'age' field raises ValidationError."""
        # Create a mock object without age field
        class MockRequest:
            user_id = 1

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="missing required field 'age'"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_none_num(self, mapper):
        """Test that None 'user_id' raises ValidationError."""
        # Create a mock object with None user_id
        class MockRequest:
            user_id = None
            age = 25

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="missing required field 'user_id'"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_none_age(self, mapper):
        """Test that None 'age' raises ValidationError."""
        # Create a mock object with None age
        class MockRequest:
            user_id = 1
            age = None

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="missing required field 'age'"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_negative_num(self, mapper):
        """Test that negative 'user_id' raises ValidationError."""
        requests = [AgeRequestDTO(user_id=-1, age=25)]

        with pytest.raises(ValidationError, match="'user_id' must be a non-negative integer"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_non_integer_num(self, mapper):
        """Test that non-integer 'user_id' raises ValidationError."""
        # Create a mock object with string user_id
        class MockRequest:
            user_id = "1"
            age = 25

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="'user_id' must be a non-negative integer"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_negative_age(self, mapper):
        """Test that negative 'age' raises ValidationError."""
        requests = [AgeRequestDTO(user_id=1, age=-5)]

        with pytest.raises(ValidationError, match="'age' must be an integer between 0 and 150"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_age_too_high(self, mapper):
        """Test that age > 150 raises ValidationError."""
        requests = [AgeRequestDTO(user_id=1, age=200)]

        with pytest.raises(ValidationError, match="'age' must be an integer between 0 and 150"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_non_integer_age(self, mapper):
        """Test that non-integer 'age' raises ValidationError."""
        # Create a mock object with string age
        class MockRequest:
            user_id = 1
            age = "25"

        requests = [MockRequest()]

        with pytest.raises(ValidationError, match="'age' must be an integer between 0 and 150"):
            mapper.map_to_entities(requests)

    def test_map_to_entities_with_mixed_valid_invalid_data(self, mapper):
        """Test that invalid data in list raises ValidationError."""
        requests = [
            AgeRequestDTO(user_id=1, age=25),  # Valid
            AgeRequestDTO(user_id=2, age=-5),  # Invalid age
        ]

        with pytest.raises(ValidationError, match="'age' must be an integer between 0 and 150"):
            mapper.map_to_entities(requests)