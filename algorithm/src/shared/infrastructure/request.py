"""Ocean Protocol input request wrapper."""

from pathlib import Path
from typing import Iterator
from logging import Logger

from ocean_runner import Algorithm

from shared.domain.exceptions.validation_error import ValidationError
from shared.infrastructure.file_reader import FileReader


class Request:
    """
    Encapsulates Ocean Protocol input file access operations.
    
    Provides a clean interface to work with algo.job_details.inputs() and handles
    file reading operations through FileReader service.
    
    Follows SOLID Dependency Inversion Principle (DIP) strictly:
    - Requires explicit dependency injection (no defaults)
    - Depends on abstractions (FileReader interface) not concretions
    - Enables testability and flexibility through injection
    """
    
    def __init__(self, algorithm: Algorithm, file_reader: FileReader):
        """
        Initialize request with Ocean Protocol algorithm.
        
        Dependencies must be injected for proper SOLID DIP compliance.
        
        Args:
            algorithm: Ocean Protocol Algorithm instance
            file_reader: FileReader instance (required dependency injection)
        """
        self.algorithm = algorithm
        self.logger = algorithm.logger
        
        self.file_reader = file_reader
    
    def validate_inputs(self) -> None:
        """
        Validate that input files are available and accessible.
        
        This method performs generic input validations that should be done
        at the infrastructure level, not in the algorithm business logic.
        
        Raises:
            ValidationError: If no input files are provided or files are not accessible
        """
        input_count = self.count()
        if input_count == 0:
            raise ValidationError("No input files provided")
        
        # Additional validations could be added here in the future
        # (e.g., file size limits, format validation, etc.)
    
    def count(self) -> int:
        """
        Count the number of input files.
        
        Returns:
            Number of input files available
        """
        return len(list(self.algorithm.job_details.inputs()))
    
    def get_content(self, index: int) -> str:
        """
        Get content of a specific input file by index.
        
        Args:
            index: Zero-based index of the input file
            
        Returns:
            Content of the file as string
            
        Raises:
            ValidationError: If index is out of range
        """
        inputs = list(self.algorithm.job_details.inputs())
        
        if index < 0 or index >= len(inputs):
            raise ValidationError(f"Index {index} out of range (0-{len(inputs)-1})")
        
        idx, path = inputs[index]
        self.logger.info(f"Reading input {idx}: {path.name}")
        return self.file_reader.read_text(path)
    
    def iter_files(self) -> Iterator[tuple[int, Path]]:
        """
        Iterate over all input files.
        
        Yields:
            Tuple of (index, path) for each input file
        """
        for idx, path in self.algorithm.job_details.inputs():
            yield idx, path
    
    def merge_all(self, separator: str = "\n") -> str:
        """
        Merge content from all input files.
        
        Args:
            separator: String to use between file contents (default: newline)
            
        Returns:
            Merged content from all files
            
        Raises:
            ValidationError: If no input files available
        """
        contents = []
        for idx, path in self.algorithm.job_details.inputs():
            self.logger.info(f"Reading input {idx}: {path.name}")
            content = self.file_reader.read_text(path)
            contents.append(content)
        
        if not contents:
            raise ValidationError("No input files to merge")
        
        return separator.join(contents)
    
    def batch_iter(self, batch_size: int) -> Iterator[list[str]]:
        """
        Iterate over input files in batches.
        
        Args:
            batch_size: Number of files to process in each batch
            
        Yields:
            List of file contents for each batch
            
        Raises:
            ValidationError: If batch_size is invalid
        """
        if batch_size <= 0:
            raise ValidationError(f"Batch size must be positive, got {batch_size}")
        
        batch = []
        for idx, path in self.algorithm.job_details.inputs():
            self.logger.info(f"Reading input {idx}: {path.name}")
            content = self.file_reader.read_text(path)
            batch.append(content)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        # Yield remaining items if any
        if batch:
            yield batch
    
    def get_job_details(self) -> dict:
        """
        Get the complete job details from Ocean Protocol.
        
        Returns:
            Dictionary containing all job details information
        """
        return self.algorithm.job_details.__dict__
    
    def show_job_details(self) -> None:
        """
        Display job details in compact format.
        """
        job_details = self.get_job_details()
        inputs_func = job_details.get('inputs')
        inputs_count = len(list(inputs_func())) if inputs_func else 0
        
        self.logger.info(f"Job details: {len(job_details)} fields, {inputs_count} input files")
