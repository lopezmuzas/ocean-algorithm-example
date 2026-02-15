# Ocean Protocol Algorithm Example

A robust, production-ready template for building algorithms on the Ocean Protocol ecosystem using hexagonal architecture and SOLID principles.

## Build and Push

```bash
$ docker buildx build --platform linux/amd64,linux/arm64 -t {ALGORITHM_TAG}:{ALGORITHM_VERSION} . --push
```

## CI/CD

This project includes a basic GitHub Actions pipeline that runs:
- Automated tests with pytest
- Multi-platform Docker image building (hidden)

Workflows are defined in `.github/workflows/ci.yml`.

## Configuration

Algorithm parameters can be configured in `algorithm/config.yaml`:
- Data parameters (supported formats, file limits)
- Statistics configuration (decimals, include count)
- Logging (level, format)
- Performance (batch size, timeouts)

Environment variables can override configuration values. Copy `.env.example` to `.env` and modify as needed.

## How to Create a New Algorithm

To create a new algorithm based on this hexagonal architecture, follow these steps:

### 1. Create a New Bounded Context

Create a new folder under `algorithm/src/` with your algorithm name, for example `price_analysis`:

```
algorithm/src/price_analysis/
├── domain/
├── services/
└── infrastructure/
```

### 2. Implement the Domain Layer

- **Input Parameters**: Create a class that inherits from `shared.domain.input_parameters.InputParameters`
- **Results**: Create a class that inherits from `shared.domain.results.Results`
- **Value Objects**: Define domain-specific entities and value objects

Example:
```python
# algorithm/src/price_analysis/domain/price_input_parameters.py
from shared.domain.input_parameters import InputParameters

class PriceInputParameters(InputParameters):
    prices: list[float]
```

### 3. Implement Application Services

Create services containing business logic, dependent only on the domain:

```python
# algorithm/src/price_analysis/services/price_calculator.py
from price_analysis.domain.price_input_parameters import PriceInputParameters
from price_analysis.domain.price_results import PriceResults

class PriceCalculator:
    def calculate_average_price(self, params: PriceInputParameters) -> PriceResults:
        # Business logic here
        pass
```

### 4. Implement Infrastructure Adapters

Create adapters for data input/output:

```python
# algorithm/src/price_analysis/infrastructure/price_reader.py
from price_analysis.domain.price_input_parameters import PriceInputParameters

class PriceReader:
    def read_from_file(self, file_path: str) -> PriceInputParameters:
        # Read data from file
        pass
```

### 5. Update the Main `algorithm.py` File

Modify `algorithm/src/algorithm.py` to use your new context:

```python
from price_analysis.services.price_calculator import PriceCalculator
from price_analysis.infrastructure.price_reader import PriceReader
from price_analysis.infrastructure.price_writer import PriceWriter

# Instantiate services
calculator = PriceCalculator()
reader = PriceReader()
writer = PriceWriter()

@algorithm.validate
def validate_price(params: PriceInputParameters, algorithm: Algorithm) -> bool:
    # Domain-specific validation
    pass

@algorithm.run
def run_price(params: PriceInputParameters, algorithm: Algorithm) -> PriceResults:
    # Execute calculation
    pass

@algorithm.save_results
def save_price_results(results: PriceResults, algorithm: Algorithm) -> None:
    # Save results
    pass
```

### 6. Create Tests

Create tests that mirror the source code structure in `algorithm/tests/price_analysis/`.

### 7. Update Configuration

If necessary, add specific parameters in the configuration file `algorithm/config.yaml`.

## Architecture

This project follows **Hexagonal Architecture** (Ports & Adapters) with **SOLID principles**:

- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and business rules
- **Infrastructure Layer**: External concerns (files, databases, APIs)

### Key Benefits

- **Testability**: Each layer can be tested in isolation
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to change implementations without affecting business logic
- **Scalability**: Modular structure supports growth

## Project Structure

```
├── algorithm/                    # Algorithm implementation
│   ├── config.yaml              # Configuration file
│   ├── pyproject.toml           # Python dependencies
│   ├── src/                     # Source code
│   │   ├── age_average/         # Current algorithm implementation
│   │   │   ├── domain/          # Domain entities
│   │   │   ├── services/        # Application services
│   │   │   └── infrastructure/  # Infrastructure adapters
│   │   └── shared/              # Shared components
│   │       ├── domain/          # Shared domain models
│   │       └── infrastructure/  # Shared infrastructure
│   └── tests/                   # Test suite
├── docs/                        # Documentation
├── _data/                       # Data directories
│   ├── inputs/                  # Input data
│   ├── outputs/                 # Output results
│   └── logs/                    # Log files
├── docker-compose.yaml          # Docker composition
├── Dockerfile                   # Container definition
└── .env.example                 # Environment variables template
```

## Development

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Running Tests

#### Option 1: Using Docker (Recommended)
```bash
docker compose run --rm algorithm pytest
```

### Running the Algorithm

```bash
docker compose up
```

### Environment Variables

Copy `.env.example` to `.env` and modify values:

```bash
cp .env.example .env
```

Available variables:
- `ALGORITHM_NAME`: Algorithm identifier
- `ALGORITHM_VERSION`: Version number
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `MAX_FILE_SIZE_MB`: Maximum input file size
- `BATCH_SIZE`: Processing batch size
- `TIMEOUT_SECONDS`: Operation timeout
-  DID : Decentralized identifier for asset in Ocean Protocol

## Contributing

1. Follow the hexagonal architecture principles
2. Write tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting PR

## License

See `algorithm/LICENSE` for details.