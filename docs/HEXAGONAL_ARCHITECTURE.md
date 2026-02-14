# Hexagonal Architecture Implementation

This project implements **Hexagonal Architecture** (Ports & Adapters) following SOLID principles, providing a robust and maintainable foundation for Ocean Protocol algorithms.

## Architecture Overview

Hexagonal Architecture separates business logic from external concerns, making the system more testable, maintainable, and adaptable to change.

### Key Principles

- **Dependency Inversion**: Business logic doesn't depend on infrastructure
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code
- **Interface Segregation**: Clean interfaces between layers
- **Dependency Injection**: Services are injected, not created

## Project Structure

```
algorithm/src/
├── shared/                          # Reusable components
│   ├── domain/                      # Shared domain models
│   │   ├── config/                  # Configuration models
│   │   │   ├── __init__.py
│   │   │   ├── algorithm_config.py  # AlgorithmConfig
│   │   │   ├── app_config.py        # AppConfig (main)
│   │   │   ├── data_config.py       # DataConfig
│   │   │   ├── logging_config.py    # LoggingConfig
│   │   │   ├── output_config.py     # OutputConfig
│   │   │   ├── performance_config.py # PerformanceConfig
│   │   │   └── statistics_config.py # StatisticsConfig
│   │   ├── exceptions/              # Exception hierarchy
│   │   │   ├── __init__.py
│   │   │   ├── algorithm_error.py   # AlgorithmError base
│   │   │   ├── validation_error.py  # ValidationError
│   │   │   ├── parsing_error.py     # ParsingError
│   │   │   ├── calculation_error.py # CalculationError
│   │   │   └── file_operation_error.py # FileOperationError
│   │   ├── input_parameters.py      # Base InputParameters
│   │   ├── results.py               # Base Results
│   │   └── __init__.py
│   └── infrastructure/              # Shared infrastructure
│       └── performance/              # Performance monitoring
│           ├── __init__.py
│           ├── performance_metrics.py # PerformanceMetrics
│           └── performance_monitor.py # PerformanceMonitor
│
├── age_average/                     # Age statistics bounded context
│   ├── domain/                      # Business entities & value objects
│   │   ├── age_input_parameters.py  # AgeInputParameters
│   │   ├── age_results.py           # AgeResults
│   │   └── age_statistics.py        # AgeStatistics
│   ├── services/                    # Application services
│   │   ├── input_parser.py          # InputParser
│   │   └── age_statistics_calculator.py # AgeStatisticsCalculator
│   └── infrastructure/              # Infrastructure adapters
│       ├── file_reader.py           # FileReader
│       └── result_writer.py         # ResultWriter
│
└── algorithm.py                     # Main orchestration (Ocean Runner)
```

## Architecture Layers

### 1. Domain Layer (Core Business Logic)

**Purpose**: Contains pure business logic with no external dependencies.

**Shared Domain Components**:
- `InputParameters`: Base class for all algorithm inputs
- `Results`: Base class for all algorithm outputs
- `AppConfig`: Main configuration with Pydantic validation
- Exception hierarchy for domain-specific errors

**Bounded Context Domain**:
- `AgeInputParameters`: Specific input model for age statistics
- `AgeResults`: Specific output model for age statistics
- `AgeStatistics`: Value object for statistical calculations

### 2. Application Layer (Use Cases)

**Purpose**: Orchestrates domain objects to fulfill business requirements.

**Services**:
- `InputParser`: Transforms external data into domain objects
- `AgeStatisticsCalculator`: Implements age calculation business rules
- Dependency injection ensures testability and flexibility

### 3. Infrastructure Layer (External Adapters)

**Purpose**: Handles external concerns like I/O, APIs, and frameworks.

**Adapters**:
- `FileReader`: File system abstraction for reading inputs
- `ResultWriter`: File system abstraction for writing outputs
- `PerformanceMonitor`: System monitoring and metrics collection

### 4. Presentation Layer (Orchestration)

**Purpose**: Coordinates the entire algorithm execution.

**Main Components**:
- `algorithm.py`: Entry point using Ocean Runner framework
- Exception handling and error propagation
- Performance monitoring integration
- Configuration loading and validation

## Dependency Flow

```
Infrastructure → Application → Domain
     ↓             ↓           ↓
  External APIs  Use Cases  Business Rules
```

- **Domain** has zero dependencies (pure logic)
- **Application** depends only on Domain
- **Infrastructure** depends on Domain and Application
- **Presentation** coordinates all layers

## Configuration Management

The project uses **Pydantic** for robust configuration validation:

### Configuration Sources
1. **YAML file** (`algorithm/config.yaml`): Base configuration
2. **Environment variables**: Override YAML values
3. **Validation**: Automatic type checking and constraint validation

### Configuration Structure
```yaml
algorithm:
  name: "age_average"
  version: "1.0.0"
  description: "Calculate age statistics"

data:
  supported_formats: ["json"]
  max_file_size_mb: 100
  age_range:
    min: 0
    max: 150

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

performance:
  batch_size: 1000
  timeout_seconds: 300
```

## Error Handling

Comprehensive exception hierarchy for different error types:

- `AlgorithmError`: Base exception for all algorithm errors
- `ValidationError`: Input validation failures
- `ParsingError`: Data parsing issues
- `CalculationError`: Business logic calculation errors
- `FileOperationError`: File I/O operation failures

Each exception provides specific error information for better debugging and user feedback.

## Performance Monitoring

Built-in performance tracking throughout the execution:

- **Execution time**: Total algorithm runtime
- **Memory usage**: Current and peak memory consumption
- **CPU utilization**: Processor usage percentage
- **Structured logging**: Metrics available in both log messages and structured data

## Testing Strategy

Comprehensive test suite mirroring the source structure:

```
algorithm/tests/
├── shared/
│   ├── domain/
│   └── infrastructure/
├── age_average/
│   ├── domain/
│   ├── services/
│   └── infrastructure/
└── test_algorithm.py
```

**Test Coverage**:
- 51 tests passing
- Unit tests for all domain objects
- Service layer testing with mocked dependencies
- Integration tests for complete workflows
- Configuration validation tests

## Benefits

### 1. **Maintainability**
- Clear separation of concerns
- One class per file (SOLID principle)
- Easy to locate and modify specific functionality

### 2. **Testability**
- Dependency injection enables easy mocking
- Each layer testable in isolation
- High test coverage ensures reliability

### 3. **Extensibility**
- New bounded contexts follow the same pattern
- Infrastructure adapters easily swappable
- Configuration-driven behavior

### 4. **Reusability**
- Shared components usable across contexts
- Generic base classes reduce duplication
- Modular design supports composition

### 5. **Robustness**
- Comprehensive error handling
- Configuration validation prevents runtime errors
- Performance monitoring aids optimization

## Adding New Features

To add a new algorithm (e.g., `price_analysis`):

1. **Create bounded context structure**:
   ```
   algorithm/src/price_analysis/
   ├── domain/
   ├── services/
   └── infrastructure/
   ```

2. **Implement domain models** extending shared base classes

3. **Create application services** with business logic

4. **Build infrastructure adapters** for external interactions

5. **Update main algorithm.py** to orchestrate the new context

6. **Add comprehensive tests** following the existing pattern

## Development Workflow

### Local Development
```bash
# Run tests
docker compose run --rm algorithm pytest

# Run algorithm
docker compose up

# Check logs
docker compose logs algorithm
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Modify values as needed
# Algorithm will automatically load .env file
```

### Performance Monitoring
Metrics are automatically logged at algorithm completion:
```
Algorithm execution completed: execution_time=0.107s, memory_usage=0.01MB, peak_memory=39.84MB, cpu_percent=0.00%
```

## CI/CD Integration

GitHub Actions pipeline provides:
- Automated testing on every push
- Multi-platform Docker image building
- Quality assurance and deployment readiness

This architecture provides a solid foundation for building and maintaining complex algorithms while keeping the codebase clean, testable, and maintainable.
    │   ├── price_input_parameters.py
    │   ├── price_results.py
    │   └── price_statistics.py
    ├── services/
    │   └── price_calculator.py
    └── infrastructure/
        └── price_writer.py
```

Each bounded context is self-contained and independent!

## Test Structure

Tests mirror the source structure:
```
algorithm/tests/
├── shared/
│   ├── domain/
│   └── infrastructure/
├── age_average/
│   ├── domain/
│   ├── services/
│   └── infrastructure/
└── test_algorithm.py
```

**51 tests passing** covering all functionality.

## Running the Project

### Run Tests
```bash
docker compose run --rm algorithm pytest -v
```

### Run Algorithm
```bash
# Using docker compose (recommended)
docker compose up

# Or manually
docker compose run --rm algorithm python -m src.algorithm
```

### Directory Structure Summary

**Source Code:**
- 22 Python files across `shared/` and `age_average/` modules
- Clean hexagonal architecture with proper separation of concerns
- No duplicate or legacy code

**Tests:**
- 15 test files mirroring the source structure
- 51 tests covering all functionality
- Complete test coverage for domain, services, and infrastructure layers

## Implemented Improvements

### ✅ Error Handling
- **Specific exceptions**: Custom exceptions implemented in dedicated `shared/domain/exceptions/` subdirectory:
  - `algorithm_error.py`: `AlgorithmError` (base class)
  - `validation_error.py`: `ValidationError` (validation errors)
  - `parsing_error.py`: `ParsingError` (parsing errors)
  - `calculation_error.py`: `CalculationError` (calculation errors)
  - `file_operation_error.py`: `FileOperationError` (file errors)
  - `__init__.py`: Exception package exporting all classes
  - `exceptions.py`: Convenience file importing all exceptions

- **Robust handling**: Services now throw specific exceptions instead of returning default values
- **Error propagation**: `algorithm.py` catches and handles exceptions appropriately, returning informative error results

### ✅ CI/CD Pipeline
- **GitHub Actions**: Basic pipeline in `.github/workflows/ci.yml`
- **Automated tests**: Runs all tests with pytest
- **Docker building**: Builds multi-platform images (linux/amd64, linux/arm64)

### ✅ Configuration File
- **config.yaml**: Centralized algorithm parameters file
- **Configuration categories**:
  - `algorithm`: Algorithm metadata
  - `data`: Data processing configuration
  - `statistics`: Statistical calculation parameters
  - `logging`: Logging configuration
  - `output`: Output format
  - `performance`: Performance settings

### ✅ Documentation Improvements
- **Updated README.md**: Includes CI/CD, configuration, and guide for creating new algorithms
- **English documentation**: Complete English documentation for better accessibility

## Benefits of Improvements

1. **Robustness**: Specific error handling improves reliability and debugging
2. **Automation**: CI/CD ensures code quality on every commit
3. **Flexibility**: External configuration allows algorithm adaptation without code changes
4. **Maintainability**: Clear documentation facilitates extension and maintenance
