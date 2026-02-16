"""Response wrapper for Ocean Protocol algorithm output operations."""

from pathlib import Path
from logging import Logger

from shared.domain.exceptions.validation_error import ValidationError
from shared.infrastructure.response_writer import ResponseWriter


class Response:
    """
    Encapsulates Ocean Protocol output operations for algorithm results.

    Handles result writing operations through ResponseWriter service.

    Follows SOLID Dependency Inversion Principle (DIP) strictly:
    - Requires explicit dependency injection (no defaults)
    - Depends on abstractions (ResponseWriter interface) not concretions
    - Enables testability and flexibility through injection
    """

    def __init__(self, result_writer: ResponseWriter):
        """
        Initialize response with ResultWriter.

        Dependencies must be injected for proper SOLID DIP compliance.

        Args:
            result_writer: ResponseWriter instance (required dependency injection)
        """
        self.result_writer = result_writer

    def write_results(self, results, output_path: Path) -> None:
        """
        Write results to an output file.

        Args:
            results: ResponseDTO object to write
            output_path: Path where to write the results

        Raises:
            ValidationError: If results or path are invalid
            FileOperationError: If file cannot be written
        """
        self.result_writer.write_json(results, output_path)