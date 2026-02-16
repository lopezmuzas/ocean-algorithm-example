"""
Ocean Protocol Algorithm Entry Point.

This module serves as the composition root orchestrator, delegating
dependency injection to each bounded context's factory method.

Architecture Pattern:
    1. Load application configuration
    2. Delegate to bounded context factory (e.g., AgeAverageAlgorithm.create())
    3. Extract Ocean Runner algorithm instance
    4. Execute Ocean Protocol pipeline

Design Rationale:
    - Entry point remains minimal and focused on orchestration
    - Bounded contexts manage their own dependency graphs
    - Follows DDD principle: bounded contexts are autonomous
    - Scales easily when adding new algorithms
"""

# Create algorithm instance using factory method
from age_average.age_average_algorithm import AgeAverageAlgorithm
from shared.domain.config.app_config import AppConfig

# Composition Root: Delegate to bounded context factory
# Note: .algorithm extracts the Ocean Runner instance for execution
algorithm = AgeAverageAlgorithm.create(AppConfig.load()).algorithm

if __name__ == "__main__":
    algorithm()
