"""Performance metrics data model."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""
    execution_time_seconds: float
    memory_usage_mb: float
    peak_memory_usage_mb: float
    cpu_percent: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            'execution_time_seconds': round(self.execution_time_seconds, 3),
            'memory_usage_mb': round(self.memory_usage_mb, 2),
            'peak_memory_usage_mb': round(self.peak_memory_usage_mb, 2),
            'cpu_percent': round(self.cpu_percent, 2)
        }