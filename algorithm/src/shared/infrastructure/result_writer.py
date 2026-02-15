"""Result writing service."""

from pathlib import Path
from logging import Logger
from shared.domain.results import Results
from shared.domain.config.output_config import OutputConfig

from shared.domain.exceptions.file_operation_error import FileOperationError
from shared.domain.exceptions.validation_error import ValidationError


class ResultWriter:
    """Service for writing results to files."""
    
    def __init__(self, logger: Logger, output_config: OutputConfig = None):
        self.logger = logger
        self.output_config = output_config or OutputConfig()
    
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
            
            # Write the JSON file using output configuration
            json_content = results.model_dump_json(indent=self.output_config.indent)
            output_path.write_text(json_content, encoding=self.output_config.encoding)
            
            self.logger.info(f"Results written to {output_path}")
            
        except Exception as e:
            raise FileOperationError(f"Error writing results to {output_path}: {e}")
