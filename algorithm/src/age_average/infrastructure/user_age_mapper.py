"""Concrete implementation of MapperInterface for UserAge."""

from typing import List

from age_average.domain.age_request_dto import AgeRequestDTO
from age_average.domain.user_age import UserAge
from shared.domain.mapper_interface import MapperInterface
from shared.domain.request_dto import RequestDTO
from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError


class UserAgeMapper(MapperInterface[UserAge]):
    """
    Concrete implementation for mapping RequestDTO to UserAge entities.

    This mapper transforms input DTOs into domain entities, performing
    necessary validations and data transformations.

    Follows SOLID DIP: all dependencies injected via constructor.
    """

    def map_to_entities(self, requests: List[RequestDTO]) -> List[UserAge]:
        """
        Transform a list of RequestDTO objects into UserAge entities.

        Args:
            requests: List of RequestDTO objects to transform

        Returns:
            List of UserAge entities

        Raises:
            ValidationError: If requests is None or contains invalid data
            ParsingError: If data transformation fails
        """
        if requests is None:
            raise ValidationError("Requests list cannot be None")

        if not isinstance(requests, list):
            raise ValidationError(f"Requests must be a list, got {type(requests)}")

        user_ages = []

        for i, request in enumerate(requests):
            try:
                # Validate required fields
                if not hasattr(request, 'user_id') or request.user_id is None:
                    raise ValidationError(f"Request at index {i} missing required field 'user_id'")

                if not hasattr(request, 'age') or request.age is None:
                    raise ValidationError(f"Request at index {i} missing required field 'age'")

                # Validate data types and ranges
                if not isinstance(request.user_id, int) or request.user_id < 0:
                    raise ValidationError(f"Request at index {i}: 'user_id' must be a non-negative integer, got {request.user_id}")

                if not isinstance(request.age, int) or request.age < 0 or request.age > 150:
                    raise ValidationError(f"Request at index {i}: 'age' must be an integer between 0 and 150, got {request.age}")

                # Create UserAge entity
                user_age = UserAge.create(
                    user_id=request.user_id,
                    age=request.age
                )

                user_ages.append(user_age)

            except AttributeError as e:
                raise ParsingError(f"Failed to parse request at index {i}: {e}")
            except (TypeError, ValueError) as e:
                raise ValidationError(f"Invalid data in request at index {i}: {e}")

        return user_ages