"""In-Memory Ocean Repository for managing entities in memory."""

import json
from typing import List, Optional, TypeVar, Type
from pydantic import ValidationError as PydanticValidationError

from shared.infrastructure.repositories.ocean_repository import OceanRepository
from shared.infrastructure.request import Request
from shared.domain.mapper_interface import MapperInterface
from shared.domain.request_dto import RequestDTO
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.file_operation_error import FileOperationError

T = TypeVar('T')  # Type for entities
ID = TypeVar('ID')  # Type for identifiers


class OceanInMemoryRepository(OceanRepository[T, ID]):
    """
    Base repository for managing entities in memory with Ocean Protocol integration (READ-ONLY).

    This abstract base class extends OceanRepository and adds in-memory storage
    capabilities using a List data structure. It provides implementations for
    basic read operations that work with the internal list.

    IMPORTANT: This is a READ-ONLY repository. The internal _entities list is
    populated ONLY by loading data from Ocean Protocol inputs via
    get_entities_from_input(). Direct write operations are not supported.

    Subclasses should implement domain-specific operations for loading data
    from Ocean Protocol inputs into the internal storage.

    Follows SOLID DIP: All dependencies injected via constructor.
    """

    def __init__(self, request: Request, mapper: MapperInterface[T]):
        """
        Initialize repository with Ocean Protocol request access and in-memory storage.

        Args:
            request: Request instance for accessing Ocean Protocol input data
            mapper: Mapper instance for transforming DTOs to entities
        """
        super().__init__(request)
        self.mapper = mapper
        self._entities: List[T] = []

    def find_all(self) -> List[T]:
        """
        Find all entities from in-memory storage.

        Returns:
            List of all entities currently stored in memory
        """
        return self._entities

    def find_by_id(self, id: ID) -> Optional[T]:
        """
        Find an entity by its identifier in memory.

        Default implementation returns None.
        Subclasses should override if entities have identifiers.

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
        from Ocean Protocol inputs via get_entities_from_input().

        Args:
            entity: The entity to save

        Raises:
            NotImplementedError: Always, as write operations are not supported
        """
        raise NotImplementedError(
            "Ocean Protocol repositories are READ-ONLY. "
            "Use get_entities_from_input() to load data from Ocean Protocol inputs."
        )

    def delete(self, id: ID) -> bool:
        """
        Delete operation is NOT SUPPORTED for Ocean Protocol repositories.

        Ocean Protocol repositories are READ-ONLY. Data can only be loaded
        from Ocean Protocol inputs via get_entities_from_input().

        Args:
            id: The identifier of the entity to delete

        Raises:
            NotImplementedError: Always, as write operations are not supported
        """
        raise NotImplementedError(
            "Ocean Protocol repositories are READ-ONLY. "
            "Use get_entities_from_input() to load data from Ocean Protocol inputs."
        )

    def exists_by_id(self, id: ID) -> bool:
        """
        Check if an entity exists by its identifier in memory.

        Default implementation returns False.
        Subclasses should override if entities have identifiers.

        Args:
            id: The identifier to check

        Returns:
            True if an entity with the given identifier exists, False otherwise
        """
        return False

    def clear(self) -> None:
        """
        Clear all entities from in-memory storage.

        This is useful for testing or resetting the repository state.
        """
        self._entities = []

    def count(self) -> int:
        """
        Get the total count of entities in memory.

        Returns:
            The number of entities currently stored
        """
        return len(self._entities)

    def get_entities_from_input(self, dto_class: Type[RequestDTO]) -> None:
        """
        Load entities from Ocean Protocol input files into internal storage.

        Generic method that reads the first input file, parses it as JSON containing
        DTO objects of the specified type, maps them to entities using the injected
        mapper, and stores them internally. Use find_all() to retrieve the loaded data.

        Args:
            dto_class: The DTO class to use for parsing input data

        Raises:
            ValidationError: If no input files available or invalid data
            ParsingError: If JSON parsing or mapping fails
            FileOperationError: If file reading fails
        """
        try:
            # Validate that we have input files
            self.request.validate_inputs()

            # Get content from first input file
            content = self.request.get_content(0)

            # Parse JSON content to DTO objects
            try:
                raw_data = json.loads(content)
                if not isinstance(raw_data, list):
                    raise ParsingError(f"Input data must be a JSON array of {dto_class.__name__} objects")

                # Convert raw data to DTO objects
                dto_requests = []
                for item in raw_data:
                    # Create DTO from dictionary
                    request_dto = dto_class(**item)
                    dto_requests.append(request_dto)

            except json.JSONDecodeError as e:
                raise ParsingError(f"Failed to parse input as JSON: {e}")
            except PydanticValidationError as e:
                raise ValidationError(f"Invalid {dto_class.__name__} data: {e}")
            except TypeError as e:
                raise ValidationError(f"Invalid {dto_class.__name__} data structure: {e}")

            # Map to entities and store in internal storage
            self._entities = self.mapper.map_to_entities(dto_requests)

        except (ValidationError, ParsingError, FileOperationError):
            # Re-raise known exceptions
            raise
        except Exception as e:
            raise FileOperationError(f"Unexpected error reading input files: {e}")
