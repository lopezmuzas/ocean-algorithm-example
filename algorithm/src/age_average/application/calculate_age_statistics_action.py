"""Action for calculating age statistics from input files."""

from typing import List
from statistics import mean

from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.age_response_dto import AgeResponseDTO
from age_average.domain.user_age import UserAge
from age_average.infrastructure.user_age_ocean_repository import UserAgeOceanRepository
from shared.domain.repository_interface import RepositoryInterface
from shared.domain.exceptions.calculation_error import CalculationError


class CalculateAgeStatisticsAction:
    """
    Action that orchestrates the calculation of age statistics.

    This action encapsulates the business logic for calculating age statistics
    by delegating to the repository layer.

    Follows SOLID DIP: all dependencies injected via constructor.
    """

    def __init__(self, repository: RepositoryInterface):
        """
        Initialize action with repository dependency.

        Args:
            repository: Repository that handles age statistics calculations
        """
        self.repository = repository

    def execute(self) -> AgeResponseDTO:
        """
        Execute the age statistics calculation.

        Returns:
            AgeResponseDTO with calculated statistics from input data or error status
        """
        try:
            # Retrieve loaded entities (automatically loaded in constructor)
            user_ages = self.repository.find_all()

            if not user_ages:
                return AgeResponseDTO(
                    status="success",
                    message="No data available for statistics calculation",
                    min_age=0,
                    max_age=0,
                    avg_age=0.0,
                )

            # Calculate statistics
            ages = [user_age.age for user_age in user_ages]
            min_age = min(ages)
            max_age = max(ages)
            avg_age = round(mean(ages), 1)

            return AgeResponseDTO(
                status="success",
                message=f"Statistics calculated from {len(user_ages)} records",
                min_age=min_age,
                max_age=max_age,
                avg_age=avg_age,
            )

        except Exception as e:
            # Return error response instead of raising exception
            return AgeResponseDTO(
                status="error",
                message=f"Failed to calculate age statistics: {str(e)}",
                min_age=0,
                max_age=0,
                avg_age=0.0,
            )