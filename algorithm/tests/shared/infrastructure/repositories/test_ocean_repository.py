"""Unit tests for OceanRepository base class."""

import pytest
from unittest.mock import Mock

from shared.infrastructure.repositories.ocean_repository import OceanRepository
from shared.infrastructure.request import Request


class TestOceanRepository:
    """Test suite for OceanRepository base class."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request instance."""
        mock_request = Mock(spec=Request)
        mock_request.logger = Mock()
        return mock_request

    def test_ocean_repository_initialization(self, mock_request):
        """Test that OceanRepository initializes correctly with Request dependency."""
        # Create a concrete implementation for testing
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)

        assert repo.request == mock_request
        assert repo.logger == mock_request.logger

    def test_find_all_default_implementation(self, mock_request):
        """Test that find_all returns empty list by default."""
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)
        result = repo.find_all()

        assert result == []

    def test_find_by_id_default_implementation(self, mock_request):
        """Test that find_by_id returns None by default."""
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)
        result = repo.find_by_id(123)

        assert result is None

    def test_save_raises_not_implemented_error(self, mock_request):
        """Test that save operation raises NotImplementedError (read-only repository)."""
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)
        entity = "test_entity"
        
        with pytest.raises(NotImplementedError, match="Ocean Protocol repositories are READ-ONLY"):
            repo.save(entity)

    def test_delete_raises_not_implemented_error(self, mock_request):
        """Test that delete operation raises NotImplementedError (read-only repository)."""
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)
        
        with pytest.raises(NotImplementedError, match="Ocean Protocol repositories are READ-ONLY"):
            repo.delete(123)

    def test_exists_by_id_default_implementation(self, mock_request):
        """Test that exists_by_id returns False by default."""
        class ConcreteOceanRepository(OceanRepository[str, int]):
            pass

        repo = ConcreteOceanRepository(mock_request)
        result = repo.exists_by_id(123)

        assert result is False