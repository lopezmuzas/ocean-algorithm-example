"""Service for parsing input data from different formats."""

import json
from typing import Any
from logging import Logger

from src.shared.domain.exceptions import ParsingError, ValidationError


class InputParser:
    """
    Parses input data from various formats and extracts age information.
    
    Follows Single Responsibility Principle - only handles input parsing.
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
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
        
        ages = []
        
        try:
            data = json.loads(text)
            
            if isinstance(data, list):
                # Format: [{"user_id": 1, "age": 10}, ...]
                for item in data:
                    if isinstance(item, dict) and "age" in item:
                        age = item["age"]
                        if not isinstance(age, int) or age < 0:
                            raise ValidationError(f"Invalid age value '{age}' in {source_name}")
                        ages.append(age)
            elif isinstance(data, dict):
                # Format: {"ages": [25, 30, ...]}
                if "ages" in data:
                    for age in data["ages"]:
                        if not isinstance(age, int) or age < 0:
                            raise ValidationError(f"Invalid age value '{age}' in {source_name}")
                        ages.append(age)
                else:
                    raise ValidationError(f"No 'ages' field found in data from {source_name}")
            else:
                raise ValidationError(f"Unsupported data format in {source_name}")
            
            if not ages:
                raise ValidationError(f"No valid ages found in {source_name}")
            
            self.logger.info(f"Extracted {len(ages)} ages from {source_name}")
            
        except json.JSONDecodeError as e:
            raise ParsingError(f"Could not parse JSON from {source_name}: {e}")
        except (KeyError, TypeError) as e:
            raise ValidationError(f"Invalid data structure in {source_name}: {e}")
        
        return ages
