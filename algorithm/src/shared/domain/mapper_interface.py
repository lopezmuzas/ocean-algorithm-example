"""Generic interface for mapping DTOs to domain entities."""

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

from shared.domain.request_dto import RequestDTO


# Type variable for domain entities
TEntity = TypeVar('TEntity')


class MapperInterface(ABC, Generic[TEntity]):
    """
    Generic interface for mapping RequestDTO objects to domain entities.

    This interface defines the contract for transforming input DTOs
    into domain entities, enabling clean separation between
    infrastructure and domain layers.

    Follows SOLID DIP: depends on abstractions, not concretions.

    Type Parameters:
        TEntity: The domain entity type that this mapper produces
    """

    @abstractmethod
    def map_to_entities(self, requests: List[RequestDTO]) -> List[TEntity]:
        """
        Transform a list of RequestDTO objects into domain entities.

        Args:
            requests: List of RequestDTO objects to transform

        Returns:
            List of domain entities

        Raises:
            ValidationError: If mapping fails due to invalid data
            ParsingError: If data parsing fails
        """
        pass
