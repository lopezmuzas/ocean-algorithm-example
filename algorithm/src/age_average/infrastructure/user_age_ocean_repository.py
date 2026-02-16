"""Repository for Age Average calculations."""

from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.user_age import UserAge
from age_average.infrastructure.user_age_mapper import UserAgeMapper
from shared.infrastructure.request import Request
from shared.infrastructure.repositories.ocean_in_memory_repository import OceanInMemoryRepository


class UserAgeOceanRepository(OceanInMemoryRepository[UserAge, int]):
    """
    Repository for UserAge entities with Ocean Protocol integration and in-memory storage.

    This repository extends OceanInMemoryRepository to provide operations for
    UserAge entities while inheriting Ocean Protocol data access and in-memory
    storage capabilities.

    Follows SOLID DIP: all dependencies injected via constructor.
    """

    def __init__(
        self,
        request: Request,
        mapper: UserAgeMapper,
    ):
        """
        Initialize repository with required dependencies.

        Args:
            request: Request instance for accessing input files
            mapper: UserAgeMapper instance for transforming DTOs to entities
        """
        super().__init__(request, mapper, AgeRequestDTO)

    # All functionality inherited from OceanInMemoryRepository:
    # - get_entities_from_input(AgeRequestDTO) automatically called in constructor
    # - find_all() for retrieving loaded entities
    # - clear(), count() for entity management
    # - save(), delete() blocked (READ-ONLY)
