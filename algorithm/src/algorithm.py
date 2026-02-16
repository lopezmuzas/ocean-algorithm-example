# Create algorithm instance using factory method
from age_average.age_average_algorithm import AgeAverageAlgorithm
from shared.domain.config.app_config import AppConfig

# Create the algorithm instance
algorithm = AgeAverageAlgorithm.create(AppConfig.load()).algorithm

if __name__ == "__main__":
    algorithm()
