"""Main application configuration model."""

from pathlib import Path
from pydantic import BaseModel, Field
import os

from .algorithm_config import AlgorithmConfig
from .data_config import DataConfig
from .logging_config import LoggingConfig
from .output_config import OutputConfig
from .performance_config import PerformanceConfig


class AppConfig(BaseModel):
    """Main application configuration."""
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)

    @classmethod
    def _resolve_config_path(cls) -> Path:
        """
        Resolve configuration file path using intelligent fallback strategy.
        
        Resolution order:
        1. CONFIG_PATH environment variable (if set)
        2. /config.yaml (Docker/production environment)
        3. ./config.yaml relative to project root (development/testing)
        
        Returns:
            Path: Resolved configuration file path
            
        Raises:
            FileNotFoundError: If no valid configuration file is found
        """
        # Try environment variable first
        env_path = os.getenv("CONFIG_PATH")
        if env_path:
            path = Path(env_path)
            if path.exists():
                return path
        
        # Try Docker/production path
        docker_path = Path("/config.yaml")
        if docker_path.exists():
            return docker_path
        
        # Try development/test path (relative to project root)
        # This file is in algorithm/src/shared/domain/config/app_config.py
        # config.yaml is in algorithm/config.yaml (5 levels up)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        dev_path = project_root / "config.yaml"
        if dev_path.exists():
            return dev_path
        
        raise FileNotFoundError(
            "Configuration file not found. Tried:\n"
            f"  - CONFIG_PATH env variable: {env_path or 'not set'}\n"
            f"  - Docker path: {docker_path}\n"
            f"  - Development path: {dev_path}"
        )

    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load application configuration with automatic path resolution.
        
        This method encapsulates the configuration loading strategy,
        automatically discovering the config file location and applying
        environment variable overrides.
        
        Returns:
            AppConfig: Loaded and validated configuration
        """
        config_path = cls._resolve_config_path()
        return cls.from_yaml_with_env(config_path)

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