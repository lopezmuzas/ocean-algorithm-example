"""Generic Repository Interface for any bounded context."""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')  # Type for entities
ID = TypeVar('ID')  # Type for identifiers


class RepositoryInterface(Generic[T, ID], ABC):
    """
    Generic repository interface for any bounded context.

    This interface defines the standard CRUD operations that any repository
    should implement, following Domain-Driven Design principles.

    Type parameters:
        T: The entity type this repository manages
        ID: The type of the entity's identifier
    """

    @abstractmethod
    def find_all(self) -> List[T]:
        """
        Find all entities.

        Returns:
            List of all entities in the repository
        """
        pass

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """
        Find an entity by its identifier.

        Args:
            id: The identifier of the entity to find

        Returns:
            The entity if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Save an entity (create or update).

        Args:
            entity: The entity to save

        Returns:
            The saved entity (with any generated identifiers)
        """
        pass

    @abstractmethod
    def delete(self, id: ID) -> bool:
        """
        Delete an entity by its identifier.

        Args:
            id: The identifier of the entity to delete

        Returns:
            True if the entity was deleted, False if it wasn't found
        """
        pass

    @abstractmethod
    def exists_by_id(self, id: ID) -> bool:
        """
        Check if an entity exists by its identifier.

        Args:
            id: The identifier to check

        Returns:
            True if the entity exists, False otherwise
        """
        pass