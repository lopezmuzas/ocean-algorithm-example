"""Main application configuration model."""

from pathlib import Path
from pydantic import BaseModel, Field
import os

from .algorithm_config import AlgorithmConfig
from .data_config import DataConfig
from .logging_config import LoggingConfig
from .output_config import OutputConfig
from .performance_config import PerformanceConfig
from .statistics_config import StatisticsConfig


class AppConfig(BaseModel):
    """Main application configuration."""
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    statistics: StatisticsConfig = Field(default_factory=StatisticsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    @classmethod
    def from_yaml_with_env(cls, yaml_path: Path) -> 'AppConfig':
        """Load configuration from YAML file with environment variable overrides."""
        import yaml

        # Load YAML configuration
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Override with environment variables
        if 'algorithm' in data:
            algo = data['algorithm']
            algo['name'] = os.getenv('ALGORITHM_NAME', algo.get('name', 'age_average'))
            algo['version'] = os.getenv('ALGORITHM_VERSION', algo.get('version', '1.0.0'))
            algo['description'] = os.getenv('ALGORITHM_DESCRIPTION', algo.get('description', ''))

        if 'data' in data:
            data_config = data['data']
            data_config['max_file_size_mb'] = int(os.getenv('MAX_FILE_SIZE_MB', data_config.get('max_file_size_mb', 100)))

        if 'logging' in data:
            logging_config = data['logging']
            logging_config['level'] = os.getenv('LOG_LEVEL', logging_config.get('level', 'INFO'))

        if 'performance' in data:
            perf_config = data['performance']
            perf_config['batch_size'] = int(os.getenv('BATCH_SIZE', perf_config.get('batch_size', 1000)))
            perf_config['timeout_seconds'] = int(os.getenv('TIMEOUT_SECONDS', perf_config.get('timeout_seconds', 300)))

        return cls(**data)