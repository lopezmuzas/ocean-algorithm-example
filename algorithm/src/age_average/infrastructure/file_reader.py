"""File reading service."""

from pathlib import Path
from logging import Logger

from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.domain.exceptions.validation_error import ValidationError


class FileReader:
    """Service for reading files with error handling."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def read_text(self, path: Path) -> str:
        """
        Read text content from a file with error handling.
        
        Args:
            path: Path to the file
            
        Returns:
            File content as string
            
        Raises:
            ValidationError: If path is invalid
            FileOperationError: If file cannot be read
        """
        if not path:
            raise ValidationError("File path cannot be None or empty")
        
        if not isinstance(path, Path):
            raise ValidationError(f"Path must be a Path object, got {type(path)}")
        
        if not path.exists():
            raise FileOperationError(f"File does not exist: {path}")
        
        if not path.is_file():
            raise FileOperationError(f"Path is not a file: {path}")
        
        try:
            content = path.read_text(encoding='utf-8', errors="replace")
            if not content.strip():
                raise ValidationError(f"File is empty: {path}")
            return content
        except ValidationError:
            raise  # Re-raise ValidationError without wrapping
        except Exception as e:
            raise FileOperationError(f"Error reading file {path}: {e}")
