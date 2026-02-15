"""Service for parsing input data from different formats."""

import json
from logging import Logger

from src.shared.domain.exceptions.parsing_error import ParsingError
from src.shared.domain.exceptions.validation_error import ValidationError
from .age_extractor import AgeExtractor


class InputParser:
    """
    Parses input data from various formats and extracts age information.
    
    Follows Single Responsibility Principle - only handles input parsing.
    Uses Strategy pattern for extensible format support.
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.age_extractor = AgeExtractor(logger)
    
    def extract_ages(self, text: str, source_name: str) -> list[int]:
        """
        Extract ages from JSON text supporting multiple formats.
        
        Supported formats:
        1. Array of objects: [{"user_id": 1, "age": 10}, ...]
        2. Object with ages field: {"ages": [25, 30, ...]}
        
        Args:
            text: JSON text content
            source_name: Name of the source file (for logging)
            
        Returns:
            List of extracted ages
            
        Raises:
            ParsingError: If JSON parsing fails
            ValidationError: If data structure is invalid or no ages found
        """
        if not text or not text.strip():
            raise ValidationError(f"Empty or invalid input text from {source_name}")
        
        try:
            data = json.loads(text)
            ages = self.age_extractor.extract_ages(data, source_name)
            
            self.logger.info(f"Extracted {len(ages)} ages from {source_name}")
            return ages
            
        except json.JSONDecodeError as e:
            raise ParsingError(f"Could not parse JSON from {source_name}: {e}")
        except (KeyError, TypeError) as e:
            raise ValidationError(f"Invalid data structure in {source_name}: {e}")
