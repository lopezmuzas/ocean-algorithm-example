"""Unit tests for OceanInMemoryRepository."""

import json
import pytest
from unittest.mock import Mock
from dataclasses import dataclass

from shared.infrastructure.repositories.ocean_in_memory_repository import OceanInMemoryRepository
from shared.infrastructure.request import Request
from shared.domain.mapper_interface import MapperInterface
from shared.domain.request_dto import RequestDTO
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError


@dataclass
class SampleEntity:
    """Sample entity for testing."""
    id: int
    name: str


class SampleDTO(RequestDTO):
    """Sample DTO for testing."""
    id: int
    name: str


class ConcreteSampleRepository(OceanInMemoryRepository[SampleEntity, int]):
    """Concrete implementation for testing purposes."""
    def __init__(self, request: Request, mapper: MapperInterface[SampleEntity]):
        super().__init__(request, mapper, SampleDTO)


class TestOceanInMemoryRepository:
    """Test suite for OceanInMemoryRepository."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request instance."""
        mock_request = Mock(spec=Request)
        mock_request.logger = Mock()
        # Default behavior to avoid failure in constructor
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = "[]"
        return mock_request

    @pytest.fixture
    def mock_mapper(self):
        """Create a mock Mapper instance."""
        mock_mapper = Mock(spec=MapperInterface)
        mock_mapper.map_to_entities.return_value = []
        return mock_mapper

    @pytest.fixture
    def repository(self, mock_request, mock_mapper):
        """Create a concrete repository instance for testing."""
        return ConcreteSampleRepository(request=mock_request, mapper=mock_mapper)

    def test_initialization(self, repository, mock_request):
        """Test that repository initializes and loads data from input."""
        assert repository.find_all() == []
        assert repository.count() == 0
        mock_request.validate_inputs.assert_called_once()
        mock_request.get_content.assert_called_once_with(0)

    def test_initialization_with_data(self, mock_request, mock_mapper):
        """Test initialization with data in input files."""
        input_data = [{"id": 1, "name": "Test"}]
        mock_request.get_content.return_value = json.dumps(input_data)
        mock_mapper.map_to_entities.return_value = [SampleEntity(id=1, name="Test")]

        repo = ConcreteSampleRepository(request=mock_request, mapper=mock_mapper)
        
        assert repo.count() == 1
        assert repo.find_all()[0].name == "Test"

    def test_find_all_returns_empty_list_initially(self, repository):
        """Test that find_all() returns empty list when no entities are loaded."""
        result = repository.find_all()
        assert result == []
        assert isinstance(result, list)

    def test_save_raises_not_implemented_error(self, repository):
        """Test that save operation raises NotImplementedError (read-only repository)."""
        entity = SampleEntity(id=1, name="Test")
        
        with pytest.raises(NotImplementedError, match="Ocean Protocol repositories are READ-ONLY"):
            repository.save(entity)

    def test_delete_raises_not_implemented_error(self, repository):
        """Test that delete operation raises NotImplementedError (read-only repository)."""
        with pytest.raises(NotImplementedError, match="Ocean Protocol repositories are READ-ONLY"):
            repository.delete(1)

    def test_clear_entities(self, mock_request, mock_mapper):
        """Test clearing all entities from storage."""
        # Setup data for initialization
        input_data = [{"id": 1, "name": "First"}, {"id": 2, "name": "Second"}]
        mock_request.get_content.return_value = json.dumps(input_data)
        mock_mapper.map_to_entities.return_value = [
            SampleEntity(id=1, name="First"),
            SampleEntity(id=2, name="Second"),
        ]
        
        repository = ConcreteSampleRepository(request=mock_request, mapper=mock_mapper)
        assert repository.count() == 2
        
        repository.clear()
        
        assert repository.count() == 0
        assert repository.find_all() == []

    def test_count_method(self, mock_request, mock_mapper):
        """Test count method returns correct number of entities."""
        # Start with empty list via initialization
        mock_request.get_content.return_value = "[]"
        mock_mapper.map_to_entities.return_value = []
        repository = ConcreteSampleRepository(request=mock_request, mapper=mock_mapper)
        assert repository.count() == 0
        
        # Manually trigger reload if needed (though typically happens in init)
        input_data = [{"id": 1, "name": "First"}]
        mock_request.get_content.return_value = json.dumps(input_data)
        mock_mapper.map_to_entities.return_value = [SampleEntity(id=1, name="First")]
        
        repository.get_entities_from_input(SampleDTO)
        assert repository.count() == 1
        
        repository.clear()
        assert repository.count() == 0

    def test_find_by_id_default_implementation(self, repository):
        """Test that find_by_id returns None by default."""
        # Default implementation returns None
        result = repository.find_by_id(1)
        assert result is None

    def test_exists_by_id_default_implementation(self, repository):
        """Test that exists_by_id returns False by default."""
        # Default implementation returns False
        result = repository.exists_by_id(1)
        assert result is False
    def test_exists_by_id_default_implementation(self, repository):
        """Test that exists_by_id returns False by default."""
        # Default implementation returns False
        result = repository.exists_by_id(1)
        assert result is False

    def test_inherits_from_ocean_repository(self, repository, mock_request, mock_mapper):
        """Test that OceanInMemoryRepository has access to Ocean Protocol features."""
        # Should have access to request from parent OceanRepository
        assert repository.request == mock_request
        assert repository.logger == mock_request.logger
        assert repository.mapper == mock_mapper

    def test_get_entities_from_input_success(self, repository, mock_request, mock_mapper):
        """Test successful loading of entities from input."""
        # Setup mock data
        input_data = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = json.dumps(input_data)
        
        # Setup mapper to return entities
        expected_entities = [
            SampleEntity(id=1, name="First"),
            SampleEntity(id=2, name="Second"),
        ]
        mock_mapper.map_to_entities.return_value = expected_entities
        
        # Execute
        repository.get_entities_from_input(SampleDTO)
        
        # Verify
        assert repository.count() == 2
        assert repository.find_all() == expected_entities
        mock_request.validate_inputs.assert_called_once()
        mock_request.get_content.assert_called_once_with(0)
        mock_mapper.map_to_entities.assert_called_once()

    def test_get_entities_from_input_with_empty_data(self, repository, mock_request, mock_mapper):
        """Test handling of empty input data."""
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = "[]"
        mock_mapper.map_to_entities.return_value = []
        
        repository.get_entities_from_input(SampleDTO)
        
        assert repository.count() == 0
        assert repository.find_all() == []

    def test_get_entities_from_input_validation_error(self, repository, mock_request):
        """Test that validation errors are propagated."""
        mock_request.validate_inputs.side_effect = ValidationError("No input files")
        
        with pytest.raises(ValidationError, match="No input files"):
            repository.get_entities_from_input(SampleDTO)

    def test_get_entities_from_input_invalid_json(self, repository, mock_request):
        """Test handling of invalid JSON data."""
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = "invalid json"
        
        with pytest.raises(ParsingError, match="Failed to parse input as JSON"):
            repository.get_entities_from_input(SampleDTO)

    def test_get_entities_from_input_non_array_json(self, repository, mock_request):
        """Test handling of JSON that is not an array."""
        mock_request.validate_inputs.return_value = None
        mock_request.get_content.return_value = '{"id": 1, "name": "Test"}'
        
        with pytest.raises(ParsingError, match="Input data must be a JSON array"):
            repository.get_entities_from_input(SampleDTO)
