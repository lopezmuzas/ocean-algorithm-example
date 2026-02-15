"""Test configuration for unit testing."""

from shared.domain.config.app_config import AppConfig
from shared.domain.config.algorithm_config import AlgorithmConfig
from shared.domain.config.data_config import DataConfig
from shared.domain.config.logging_config import LoggingConfig
from shared.domain.config.output_config import OutputConfig
from shared.domain.config.performance_config import PerformanceConfig


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