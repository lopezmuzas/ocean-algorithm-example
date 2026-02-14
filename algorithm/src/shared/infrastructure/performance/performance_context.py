"""Performance monitoring context for algorithm execution lifecycle."""

from typing import Optional, Callable, Any
from functools import wraps
from logging import Logger

from .performance_monitor import PerformanceMonitor


class PerformanceContext:
    """
    Manages performance monitoring lifecycle for algorithm execution.
    
    This class encapsulates performance monitoring state without using global variables,
    following SOLID principles and clean code practices.
    """
    
    _MONITOR_ATTR = '_perf_monitor'
    
    @classmethod
    def start_monitoring(cls, algo) -> None:
        """
        Initialize performance monitoring at the start of algorithm execution.
        
        Args:
            algo: Algorithm instance to attach the monitor to
        """
        monitor = PerformanceMonitor(algo.logger)
        setattr(algo, cls._MONITOR_ATTR, monitor)
    
    @classmethod
    def log_completion(cls, algo) -> None:
        """
        Log final performance metrics at algorithm completion.
        
        Args:
            algo: Algorithm instance with attached monitor
        """
        monitor: Optional[PerformanceMonitor] = getattr(algo, cls._MONITOR_ATTR, None)
        if monitor:
            metrics = monitor.get_metrics()
            algo.logger.info(
                f"Total execution time: {metrics.execution_time_seconds:.3f}s | "
                f"Memory: {metrics.memory_usage_mb:.2f}MB | "
                f"Peak: {metrics.peak_memory_usage_mb:.2f}MB | "
                f"CPU: {metrics.cpu_percent:.2f}%"
            )


def with_performance_monitoring(func: Callable) -> Callable:
    """
    Decorator to automatically initialize performance monitoring for a function.
    
    This decorator should be applied to the validate function to ensure
    performance monitoring starts at the beginning of algorithm execution.
    
    Args:
        func: Function to wrap with performance monitoring
        
    Returns:
        Wrapped function with automatic performance monitoring initialization
    """
    @wraps(func)
    def wrapper(algo, *args, **kwargs):
        PerformanceContext.start_monitoring(algo)
        return func(algo, *args, **kwargs)
    return wrapper
