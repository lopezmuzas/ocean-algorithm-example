"""Result writing service."""

from pathlib import Path
from logging import Logger
from src.shared.domain.results import Results

from src.shared.domain.exceptions.file_operation_error import FileOperationError
from src.shared.domain.exceptions.validation_error import ValidationError


class ResultWriter:
    """Service for writing results to files."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def write_json(self, results: Results, output_path: Path) -> None:
        """
        Write results to a JSON file.
        
        Args:
            results: Results object to write
            output_path: Path where to write the file
            
        Raises:
            ValidationError: If results or path are invalid
            FileOperationError: If file cannot be written
        """
        if not results:
            raise ValidationError("Results object cannot be None")
        
        if not isinstance(results, Results):
            raise ValidationError(f"Results must be a Results object, got {type(results)}")
        
        if not output_path:
            raise ValidationError("Output path cannot be None or empty")
        
        if not isinstance(output_path, Path):
            raise ValidationError(f"Output path must be a Path object, got {type(output_path)}")
        
        try:
            # Ensure parent directory exists
            if not output_path.parent.exists():
                output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the JSON file
            json_content = results.model_dump_json(indent=2)
            output_path.write_text(json_content, encoding='utf-8')
            
            self.logger.info(f"Results written to {output_path}")
            
        except Exception as e:
            raise FileOperationError(f"Error writing results to {output_path}: {e}")
