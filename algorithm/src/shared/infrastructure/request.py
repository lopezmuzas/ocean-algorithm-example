"""Ocean Protocol input request wrapper."""

import json
from pathlib import Path
from typing import Iterator, Optional
from logging import Logger
from urllib.parse import urlparse, parse_qs

from ocean_runner import Algorithm

from shared.domain.exceptions.validation_error import ValidationError
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.file_operation_error import FileOperationError
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
    
    def get_custom_parameters(self) -> dict:
        """
        Get custom parameters from both dataset query params and algoCustomData.json.
        
        Combines parameters from two sources:
        1. Dataset query parameters: URL query params from dataset URLs (e.g., ?sampling=10)
        2. Algorithm custom data: Parameters from algoCustomData.json file
        
        Examples:
            Dataset query params: https://example.com/mydata?sampling=10&window=5
            Algorithm custom data: {"iterations": 100, "threshold": 0.5}
            
        Returns:
            Dictionary with all custom parameters merged. Algorithm custom data
            takes precedence over dataset query params if keys overlap.
            
        Raises:
            ParsingError: If custom data file cannot be parsed
        """
        params = {}
        
        # 1. Get dataset query parameters from input URLs
        dataset_params = self._get_dataset_query_parameters()
        params.update(dataset_params)
        
        # 2. Get algorithm custom data (overrides dataset params if same key)
        algo_params = self._get_algo_custom_data()
        params.update(algo_params)        
        return params
    
    def _get_dataset_query_parameters(self) -> dict:
        """
        Extract query parameters from dataset input URLs.
        
        Publisher can define parameters in dataset URLs like:
        https://example.com/mydata?sampling=10&window=5
        
        Returns:
            Dictionary with query parameters from all input URLs merged.
            Values are lists since query params can have multiple values.
        """
        params = {}
        
        try:
            for idx, path in self.algorithm.job_details.inputs():
                # Try to get URL from job details if available
                # Note: Ocean Protocol may store original URL in metadata
                # For now, we'll skip URL parsing as paths are local after download
                pass
        except Exception as e:
            self.logger.warning(f"Could not extract dataset query parameters: {e}")
        
        return params
    
    def _get_algo_custom_data(self) -> dict:
        """
        Read algorithm custom data from algoCustomData.json file.
        
        Buyer can provide custom parameters when running the algorithm.
        Ocean Protocol stores these in /data/inputs/algoCustomData.json
        
        Returns:
            Dictionary with algorithm custom parameters, empty dict if file not found
            
        Raises:
            ParsingError: If JSON file is malformed
        """
        custom_data_path = Path("/data/inputs/algoCustomData.json")
        
        if not custom_data_path.exists():
            self.logger.debug(f"No custom data file found at {custom_data_path}")
            return {}
        
        try:
            with open(custom_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)            
            return data
            
        except json.JSONDecodeError as e:
            raise ParsingError(
                f"Invalid JSON in custom data file {custom_data_path}: {e}"
            )
        except Exception as e:
            raise FileOperationError(
                f"Error reading custom data file {custom_data_path}: {e}"
            )
    
    def get_job_details(self) -> dict:
        """
        Get the complete job details from Ocean Protocol.
        
        Returns:
            Dictionary containing all job details information
        """
        return self.algorithm.job_details.__dict__
    
    def show_job_details(self) -> None:
        """
        Display all job details in multi-line format for better readability.
        
        Shows all attributes from job_details with line breaks (dd-style from Laravel).
        """
        job_details = self.get_job_details()
        
        # Format header
        output = "\n" + "=" * 60 + "\n"
        output += "Job Details:\n"
        output += "=" * 60 + "\n"
        
        # Format each attribute
        for key, value in job_details.items():
            if callable(value):
                # Handle callable attributes (like inputs)
                try:
                    if key == 'inputs':
                        inputs_list = list(value())
                        output += f"  {key}: <function> [{len(inputs_list)} files]\n"
                    else:
                        output += f"  {key}: <function>\n"
                except Exception as e:
                    output += f"  {key}: <function> [Error: {e}]\n"
            else:
                # Format regular attributes
                output += f"  {key}: {value}\n"
        
        output += "=" * 60 + "\n"
        self.logger.info(output)
