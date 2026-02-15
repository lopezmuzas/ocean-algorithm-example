"""Test configuration for unit testing."""

from .app_config import AppConfig
from .algorithm_config import AlgorithmConfig
from .data_config import DataConfig
from .logging_config import LoggingConfig
from .output_config import OutputConfig
from .performance_config import PerformanceConfig


class TestConfig(AppConfig):
    """Test configuration with sensible defaults for testing."""

    @classmethod
    def create(cls) -> 'TestConfig':
        """Create a test configuration with default test values."""
        return cls(
            algorithm=AlgorithmConfig(
                name="test_algorithm",
                version="1.0.0",
                description="Test algorithm for unit tests"
            ),
            data=DataConfig(),
            logging=LoggingConfig(),
            output=OutputConfig(),
            performance=PerformanceConfig()
        )