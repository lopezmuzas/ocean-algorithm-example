"""Response wrapper for Ocean Protocol algorithm output operations."""

from pathlib import Path
from logging import Logger

from shared.domain.exceptions.validation_error import ValidationError
from shared.infrastructure.result_writer import ResultWriter


class Response:
    """
    Encapsulates Ocean Protocol output operations for algorithm results.

    Handles result writing operations through ResultWriter service.

    Follows SOLID Dependency Inversion Principle (DIP) strictly:
    - Requires explicit dependency injection (no defaults)
    - Depends on abstractions (ResultWriter interface) not concretions
    - Enables testability and flexibility through injection
    """

    def __init__(self, result_writer: ResultWriter):
        """
        Initialize response with ResultWriter.

        Dependencies must be injected for proper SOLID DIP compliance.

        Args:
            result_writer: ResultWriter instance (required dependency injection)
        """
        self.result_writer = result_writer

    def write_results(self, results, output_path: Path) -> None:
        """
        Write results to an output file.

        Args:
            results: Results object to write
            output_path: Path where to write the results

        Raises:
            ValidationError: If results or path are invalid
            FileOperationError: If file cannot be written
        """
        self.result_writer.write_json(results, output_path)