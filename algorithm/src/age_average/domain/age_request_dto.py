"""Age-specific input DTO."""

from shared.domain.request_dto import RequestDTO


class AgeRequestDTO(RequestDTO):
    """Custom input DTO for the age statistics algorithm."""
    user_id: int
    age: int
