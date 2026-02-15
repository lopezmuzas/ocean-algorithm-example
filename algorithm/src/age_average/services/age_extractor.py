"""Extracts ages from JSON data using different formats."""

from typing import Any, List, Callable
from logging import Logger

from src.shared.domain.exceptions.validation_error import ValidationError


class AgeExtractor:
    """
    Extracts ages from JSON data supporting multiple formats.

    Simplified version using functions instead of complex strategy classes.
    """

    def __init__(self, logger: Logger):
        self.logger = logger

    def extract_ages(self, data: Any, source_name: str) -> List[int]:
        """
        Extract ages from data using the appropriate format handler.

        Args:
            data: The parsed JSON data
            source_name: Name of the source file (for error messages)

        Returns:
            List of extracted ages

        Raises:
            ValidationError: If data format is unsupported or extraction fails
        """
        # Try different formats in order of preference
        if self._is_array_of_objects(data):
            return self._extract_from_array_of_objects(data, source_name)
        elif self._is_object_with_ages_field(data):
            return self._extract_from_object_with_ages_field(data, source_name)
        else:
            raise ValidationError(f"Unsupported data format in {source_name}")

    def _is_array_of_objects(self, data: Any) -> bool:
        """Check if data is array of objects format."""
        return isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict)

    def _is_object_with_ages_field(self, data: Any) -> bool:
        """Check if data is object with ages field format."""
        return isinstance(data, dict) and "ages" in data

    def _extract_from_array_of_objects(self, data: Any, source_name: str) -> List[int]:
        """Extract ages from array of objects format: [{"age": 10}, ...]."""
        ages = []
        for item in data:
            if not isinstance(item, dict):
                raise ValidationError(f"Expected object in array, got {type(item)} in {source_name}")

            if "age" in item:
                age = item["age"]
                if not isinstance(age, int) or age < 0:
                    raise ValidationError(f"Invalid age value '{age}' in {source_name}")
                ages.append(age)
            # Skip items without age field silently

        if not ages:
            raise ValidationError(f"No valid ages found in {source_name}")

        return ages

    def _extract_from_object_with_ages_field(self, data: Any, source_name: str) -> List[int]:
        """Extract ages from object with ages field: {"ages": [25, 30, ...]}."""
        ages_field = data["ages"]
        if not isinstance(ages_field, list):
            raise ValidationError(f"'ages' field must be an array in {source_name}")

        ages = []
        for age in ages_field:
            if not isinstance(age, int) or age < 0:
                raise ValidationError(f"Invalid age value '{age}' in {source_name}")
            ages.append(age)

        if not ages:
            raise ValidationError(f"No valid ages found in {source_name}")

        return ages