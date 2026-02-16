"""Unit tests for MapperInterface."""

import pytest
from typing import List
from abc import ABC

from shared.domain.mapper_interface import MapperInterface
from shared.domain.request_dto import RequestDTO


class TestMapperInterface:
    """Test suite for MapperInterface."""

    def test_mapper_interface_is_abstract(self):
        """Test that MapperInterface is an abstract class."""
        assert issubclass(MapperInterface, ABC)

    def test_mapper_interface_requires_map_to_entities_implementation(self):
        """Test that implementing classes must define map_to_entities."""
        
        # This should raise TypeError because map_to_entities is not implemented
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            class IncompleteMapper(MapperInterface):
                pass
            
            IncompleteMapper()

    def test_mapper_interface_can_be_implemented(self):
        """Test that MapperInterface can be properly implemented."""
        
        class SimpleEntity:
            def __init__(self, value: int):
                self.value = value
        
        class ConcreteMapper(MapperInterface[SimpleEntity]):
            def map_to_entities(self, requests: List[RequestDTO]) -> List[SimpleEntity]:
                return [SimpleEntity(value=1) for _ in requests]
        
        # Should not raise any errors
        mapper = ConcreteMapper()
        assert mapper is not None
        
        # Test the implementation
        result = mapper.map_to_entities([])
        assert result == []
