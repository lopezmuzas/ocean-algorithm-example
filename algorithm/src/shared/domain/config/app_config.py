"""Main application configuration model."""

from pathlib import Path
from pydantic import BaseModel, Field

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
        1. /config.yaml (Docker/production environment)
        2. ./config.yaml relative to project root (development/testing)
        
        Returns:
            Path: Resolved configuration file path
            
        Raises:
            FileNotFoundError: If no valid configuration file is found
        """
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
            f"  - Docker path: {docker_path}\n"
            f"  - Development path: {dev_path}"
        )

    @classmethod
    def load(cls) -> 'AppConfig':
        """
        Load application configuration with automatic path resolution.
        
        This method encapsulates the configuration loading strategy,
        automatically discovering the config file location.
        
        Returns:
            AppConfig: Loaded and validated configuration
        """
        config_path = cls._resolve_config_path()
        return cls.from_yaml(config_path)

    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'AppConfig':
        """Load configuration from YAML file."""
        import yaml

        # Load YAML configuration
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(**data)