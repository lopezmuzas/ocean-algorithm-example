"""Performance monitoring service."""

import time
import psutil
from logging import Logger

from .performance_metrics import PerformanceMetrics


class PerformanceMonitor:
    """Monitor performance metrics during algorithm execution."""

    def __init__(self, logger: Logger):
        self.logger = logger
        self.start_time = time.time()
        self.process = psutil.Process()
        self.memory_start = self.process.memory_info().rss
        self.peak_memory = self.memory_start

    def update_peak_memory(self) -> None:
        """Update peak memory usage."""
        current_memory = self.process.memory_info().rss
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        self.update_peak_memory()

        execution_time = time.time() - self.start_time
        current_memory = self.process.memory_info().rss
        memory_usage = current_memory - self.memory_start
        cpu_percent = self.process.cpu_percent(interval=0.1)

        return PerformanceMetrics(
            execution_time_seconds=execution_time,
            memory_usage_mb=memory_usage / 1024 / 1024,
            peak_memory_usage_mb=self.peak_memory / 1024 / 1024,
            cpu_percent=cpu_percent
        )

    def log_metrics(self, operation: str = "operation") -> None:
        """Log current performance metrics."""
        metrics = self.get_metrics()
        self.logger.info(
            f"Performance metrics for {operation}: "
            f"execution_time={metrics.execution_time_seconds:.3f}s, "
            f"memory_usage={metrics.memory_usage_mb:.2f}MB, "
            f"peak_memory={metrics.peak_memory_usage_mb:.2f}MB, "
            f"cpu_percent={metrics.cpu_percent:.2f}%",
            extra=metrics.to_dict()
        )

    def log_final_metrics(self) -> None:
        """Log final performance metrics at the end of execution."""
        metrics = self.get_metrics()
        self.logger.info(
            f"Algorithm execution completed: "
            f"execution_time={metrics.execution_time_seconds:.3f}s, "
            f"memory_usage={metrics.memory_usage_mb:.2f}MB, "
            f"peak_memory={metrics.peak_memory_usage_mb:.2f}MB, "
            f"cpu_percent={metrics.cpu_percent:.2f}%",
            extra={
                **metrics.to_dict(),
                'status': 'completed'
            }
        )