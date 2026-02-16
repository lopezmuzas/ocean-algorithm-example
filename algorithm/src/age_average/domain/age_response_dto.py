"""Age-specific results."""

from shared.domain.response_dto import ResponseDTO


class AgeResponseDTO(ResponseDTO[dict]):
    """Results for the age statistics algorithm."""
    min_age: int
    max_age: int
    avg_age: float
