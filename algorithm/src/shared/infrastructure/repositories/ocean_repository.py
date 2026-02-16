"""Base Ocean Repository for accessing Ocean Protocol data."""

from abc import ABC
from typing import List, Optional, TypeVar, Generic

from shared.domain.repository_interface import RepositoryInterface
from shared.infrastructure.request import Request

T = TypeVar('T')  # Type for entities
ID = TypeVar('ID')  # Type for identifiers


class OceanRepository(RepositoryInterface[T, ID], ABC):
    """
    Base repository for accessing Ocean Protocol data (READ-ONLY).

    This abstract base class implements the RepositoryInterface and provides
    READ-ONLY access to Ocean Protocol input data through the Request dependency.

    IMPORTANT: Ocean Protocol repositories are READ-ONLY. Write operations
    (save, delete) are not supported and will raise NotImplementedError.
    Data can only be loaded from Ocean Protocol inputs.

    Subclasses should implement domain-specific read operations while inheriting
    the basic read operations and Ocean Protocol data access.

    Follows SOLID DIP: Request dependency is injected via constructor.
    """

    def __init__(self, request: Request):
        """
        Initialize repository with Ocean Protocol request access.

        Args:
            request: Request instance for accessing Ocean Protocol input data
        """
        self.request = request
        self.logger = request.logger

    # Default implementations of RepositoryInterface methods
    # Subclasses can override these if they manage persistent entities

    def find_all(self) -> List[T]:
        """
        Find all entities.

        Default implementation returns empty list.
        Subclasses should override if they manage persistent entities.

        Returns:
            List of all entities in the repository
        """
        return []

    def find_by_id(self, id: ID) -> Optional[T]:
        """
        Find an entity by its identifier.

        Default implementation returns None.
        Subclasses should override if they manage persistent entities.

        Args:
            id: The identifier of the entity to find

        Returns:
            The entity if found, None otherwise
        """
        return None

    def save(self, entity: T) -> T:
        """
        Save operation is NOT SUPPORTED for Ocean Protocol repositories.

        Ocean Protocol repositories are READ-ONLY. Data can only be loaded
        from Ocean Protocol inputs, not modified.

        Args:
            entity: The entity to save

        Raises:
            NotImplementedError: Always, as write operations are not supported
        """
        raise NotImplementedError(
            "Ocean Protocol repositories are READ-ONLY. "
            "Save operations are not supported. "
            "Data can only be loaded from Ocean Protocol inputs."
        )

    def delete(self, id: ID) -> bool:
        """
        Delete operation is NOT SUPPORTED for Ocean Protocol repositories.

        Ocean Protocol repositories are READ-ONLY. Data can only be loaded
        from Ocean Protocol inputs, not modified.

        Args:
            id: The identifier of the entity to delete

        Raises:
            NotImplementedError: Always, as write operations are not supported
        """
        raise NotImplementedError(
            "Ocean Protocol repositories are READ-ONLY. "
            "Delete operations are not supported. "
            "Data can only be loaded from Ocean Protocol inputs."
        )

    def exists_by_id(self, id: ID) -> bool:
        """
        Check if an entity exists by its identifier.

        Default implementation always returns False.
        Subclasses should override if they manage persistent entities.

        Args:
            id: The identifier of the entity to check

        Returns:
            True if the entity exists, False otherwise
        """
        return False