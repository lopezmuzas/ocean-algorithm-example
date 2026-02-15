"""Ocean Protocol input request wrapper."""

from pathlib import Path
from typing import Iterator
from logging import Logger

from ocean_runner import Algorithm

from shared.domain.exceptions.validation_error import ValidationError


class Request:
    """
    Encapsulates Ocean Protocol input file access.
    
    Provides a clean interface to work with algo.job_details.inputs() and handles
    file operations through the injected file reader.
    """
    
    def __init__(self, algorithm: Algorithm, file_reader):
        """
        Initialize request with Ocean Protocol algorithm and file reader.
        
        Args:
            algorithm: Ocean Protocol Algorithm instance
            file_reader: FileReader instance for reading file content
        """
        self.algorithm = algorithm
        self.file_reader = file_reader
        self.logger = algorithm.logger
    
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
