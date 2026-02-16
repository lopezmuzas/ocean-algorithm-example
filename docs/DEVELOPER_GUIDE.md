# AI Development Guidelines

**Ocean Protocol Algorithm Development - Complete Reference**

This document provides comprehensive guidelines for developing Ocean Protocol algorithms following clean architecture principles, SOLID design patterns, and Ocean Protocol best practices.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [SOLID Principles](#solid-principles)
3. [Project Structure](#project-structure)
4. [Class Organization](#class-organization)
5. [Naming Conventions](#naming-conventions)
6. [Error Handling](#error-handling)
7. [Testing Standards](#testing-standards)
8. [Documentation](#documentation)
9. [Configuration Management](#configuration-management)
10. [Ocean Protocol Patterns](#ocean-protocol-patterns)
11. [Creating New Bounded Contexts](#creating-new-bounded-contexts)
12. [Code Examples](#code-examples)
13. [Best Practices Summary](#best-practices-summary)
14. [Development Workflow](#development-workflow)
15. [Code Review Checklist](#code-review-checklist)
16. [Additional Resources](#additional-resources)

---

## Architecture Overview

This project implements **Hexagonal Architecture** (Ports & Adapters) following SOLID principles, providing a robust and maintainable foundation for Ocean Protocol algorithms.

### Why Hexagonal Architecture?

Hexagonal Architecture separates business logic from external concerns, making the system:
- **More testable**: Dependencies can be easily mocked
- **More maintainable**: Clear separation of concerns
- **More adaptable**: Easy to swap implementations

### Key Architectural Principles

- **Dependency Inversion**: Business logic doesn't depend on infrastructure
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Easy to extend without modifying existing code
- **Interface Segregation**: Clean interfaces between layers
- **Dependency Injection**: Services are injected, not created

### Complete Project Structure

```
algorithm/src/
├── shared/                          # Reusable components across bounded contexts
│   ├── domain/                      # Shared domain models
│   │   ├── algorithm_interface.py   # AlgorithmInterface (contract)
│   │   ├── base_algorithm.py        # BaseAlgorithm (common functionality)
│   │   ├── config/                  # Configuration models
│   │   │   ├── __init__.py
│   │   │   ├── algorithm_config.py  # AlgorithmConfig
│   │   │   ├── app_config.py        # AppConfig (main configuration)
│   │   │   ├── data_config.py       # DataConfig
│   │   │   ├── logging_config.py    # LoggingConfig
│   │   │   ├── output_config.py     # OutputConfig
│   │   │   ├── performance_config.py # PerformanceConfig
│   │   │   └── statistics_config.py # StatisticsConfig
│   │   ├── exceptions/              # Exception hierarchy
│   │   │   ├── __init__.py
│   │   │   ├── algorithm_error.py   # AlgorithmError (base)
│   │   │   ├── validation_error.py  # ValidationError
│   │   │   ├── parsing_error.py     # ParsingError
│   │   │   ├── calculation_error.py # CalculationError
│   │   │   └── file_operation_error.py # FileOperationError
│   │   ├── input_parameters.py      # Base InputParameters
│   │   ├── results.py               # Base Results
│   │   └── __init__.py
│   └── infrastructure/              # Shared infrastructure services
│       ├── file_reader.py           # FileReader (moved from age_average)
│       ├── response_writer.py         # ResponseWriter (moved from age_average)
│       ├── request.py               # Request (input operations wrapper)
│       ├── response.py              # Response (output operations wrapper)
│       └── performance/              # Performance monitoring
│           ├── __init__.py
│           ├── performance_metrics.py # PerformanceMetrics
│           └── performance_monitor.py # PerformanceMonitor
│
├── age_average/                     # Example: Age statistics bounded context
│   ├── domain/                      # Business entities & value objects
│   │   ├── age_input_parameters.py  # AgeInputParameters
│   │   ├── age_results.py           # AgeResults
│   │   └── age_statistics.py        # AgeStatistics
│   ├── application/                 # Application services (use cases)
│   │   ├── input_parser.py          # InputParser
│   │   ├── age_extractor.py         # AgeExtractor
│   │   └── age_statistics_calculator.py # AgeStatisticsCalculator
│   └── infrastructure/              # Infrastructure adapters (specific to this BC)
│       └── __init__.py              # (Empty - services moved to shared)
│
└── algorithm.py                     # Main orchestration (Ocean Runner integration)
```

### Architecture Layers

#### 1. Domain Layer (`domain/`)

**Purpose**: Contains pure business logic with no external dependencies.

**Characteristics**:
- No framework dependencies, pure Python
- Immutable value objects when possible
- Business rules and validations
- Domain events and exceptions

**Shared Domain Components**:
- `AlgorithmInterface`: Contract that all algorithms must implement
- `BaseAlgorithm`: Abstract base class providing common algorithm functionality
- `InputParameters`: Base class for all algorithm inputs
- `Results`: Base class for all algorithm outputs
- `AppConfig`: Main configuration with Pydantic validation
- Exception hierarchy for domain-specific errors

**Algorithm Architecture**:
- **AlgorithmInterface**: Defines the contract (`validate_input`, `run`, `save`)
- **BaseAlgorithm**: Provides automatic performance monitoring and callback registration
- **Concrete Algorithms**: Extend `BaseAlgorithm` and implement specific business logic

**Bounded Context Domain** (e.g., `age_average/domain/`):
- `AgeInputParameters`: Specific input model
- `AgeResults`: Specific output model
- `AgeStatistics`: Value object for calculations

**Rules**:
- ✅ Pure functions and immutable data structures
- ✅ Pydantic models for validation
- ✅ Domain-specific exceptions
- ❌ No I/O operations
- ❌ No framework dependencies
- ❌ No service layer imports

#### 2. Application Layer (`application/`)

**Purpose**: Orchestrates domain objects to fulfill business requirements (use cases).

**Characteristics**:
- Application logic and workflows
- Coordinates between domain and infrastructure
- Uses dependency injection
- Transaction boundaries

**Examples**:
- `InputParser`: Transforms external data into domain objects
- `AgeStatisticsCalculator`: Implements calculation business rules
- `AgeExtractor`: Extracts specific data from inputs

**Rules**:
- ✅ Depend on domain layer
- ✅ Accept dependencies via constructor
- ✅ Coordinate multiple domain objects
- ❌ No direct I/O (use infrastructure)
- ❌ No framework-specific code

#### 3. Infrastructure Layer (`infrastructure/`)

**Purpose**: Handles external concerns like I/O, APIs, and framework integrations.

**Characteristics**:
- File system operations
- Database access
- External API calls
- Framework integrations (Ocean Protocol)
- Shared services available across bounded contexts

**Examples**:
- `FileReader`: Generic file reading service (shared)
- `ResponseWriter`: Generic result writing service (shared)
- `Request`: Input operations wrapper (file reading)
- `Response`: Output operations wrapper (result writing)
- `PerformanceMonitor`: System monitoring and metrics

**Rules**:
- ✅ Can depend on domain and services
- ✅ Implements technical concerns
- ✅ Framework-specific code allowed
- ✅ Shared services should be generic and reusable
- ❌ No business logic
- ❌ Should be easily swappable

#### 4. Presentation Layer (Orchestration)

**Purpose**: Coordinates the entire algorithm execution.

**Main Components**:
- `algorithm.py`: Entry point using Ocean Runner framework
- Exception handling and error propagation
- Performance monitoring integration
- Configuration loading and validation

### Dependency Flow

```
Presentation Layer (algorithm.py)
        ↓
Infrastructure Layer (adapters)
        ↓
Service Layer (use cases)
        ↓
Domain Layer (business logic)
```

**Key Rule**: Dependencies point inward. Inner layers never depend on outer layers.

---

## SOLID Principles

### Single Responsibility Principle (SRP)
Each class should have **one and only one reason to change**.

✅ **DO**:
```python
class InputParser:
    """Only handles input parsing."""
    def extract_ages(self, text: str) -> list[int]:
        pass

class AgeStatisticsCalculator:
    """Only handles statistics calculation."""
    def calculate(self, ages: list[int]) -> AgeStatistics:
        pass
```

❌ **DON'T**:
```python
class DataProcessor:
    """Does too many things - parsing AND calculating AND writing."""
    def parse_and_calculate_and_write(self):
        pass
```

### Open/Closed Principle (OCP)
Classes should be **open for extension, closed for modification**.

✅ **DO**: Use composition and dependency injection
```python
class InputParser:
    def __init__(self, logger: Logger):
        self.age_extractor = AgeExtractor(logger)  # Can be extended/replaced
```

### Liskov Substitution Principle (LSP)
Derived classes must be substitutable for their base classes.

✅ **DO**:
```python
class AlgorithmError(Exception):
    """Base exception for algorithm errors."""
    pass

class ValidationError(AlgorithmError):
    """Maintains same interface as parent."""
    pass
```

### Interface Segregation Principle (ISP)
Clients should not depend on interfaces they don't use.

✅ **DO**: Create focused, specific classes
```python
class FileReader:
    """Only provides file reading capabilities."""
    def read_text(self, path: Path) -> str:
        pass

class ResponseWriter:
    """Only provides result writing capabilities."""
    def write_json(self, results: dict, path: Path) -> None:
        pass
```

### Dependency Inversion Principle (DIP)
Depend on **abstractions**, not concretions. High-level modules should not depend on low-level modules.

✅ **DO**: Use strict dependency injection - Request requires explicit injection

```python
# Strict dependency injection (required for SOLID compliance)
file_reader = FileReader(logger)
result_writer = ResponseWriter(logger)
request = Request(ocean_algorithm, file_reader, result_writer)

class AgeAlgorithm(BaseAlgorithm):
    def run(self, algo: Algorithm) -> AgeResults:
        # Depend on abstractions through Request interface
        parser = InputParser(algo.logger)
        calculator = AgeStatisticsCalculator(algo.logger)

        # Process inputs using injected FileReader
        all_ages = []
        for idx, path in self.request.iter_files():
            text = self.request.file_reader.read_text(path)  # Abstracted I/O
            ages = parser.extract_ages(text)
            all_ages.extend(ages)

        stats = calculator.calculate(all_ages)
        return stats
```

❌ **DON'T**: Create concrete dependencies directly or use defaults
```python
class AgeAlgorithm:
    def __init__(self):
        # Violates DIP - depends on concrete FileReader implementation
        self.file_reader = FileReader(self.logger)  # ❌ Tight coupling
        
        # Also violates DIP - no dependency injection
        request = Request(ocean_algorithm)  # ❌ Missing required dependencies
```

---

## Project Structure

### Directory Organization

```
algorithm/
├── src/
│   ├── age_average/              # Feature module (bounded context)
│   │   ├── domain/
│   │   │   ├── age_input_parameters.py   # Input models
│   │   │   ├── age_results.py            # Output models
│   │   │   └── age_statistics.py         # Business entities
│   │   ├── application/
│   │   │   ├── input_parser.py           # Parsing logic
│   │   │   ├── age_extractor.py          # Extraction logic
│   │   │   └── age_statistics_calculator.py
│   │   └── infrastructure/       # BC-specific infrastructure (usually empty)
│   ├── shared/                   # Shared kernel (reusable across BCs)
│   │   ├── domain/
│   │   │   ├── algorithm_interface.py   # Algorithm contract
│   │   │   ├── base_algorithm.py        # Common algorithm functionality
│   │   │   ├── config/           # Configuration models
│   │   │   ├── exceptions/       # Custom exceptions
│   │   │   ├── input_parameters.py
│   │   │   └── results.py
│   │   └── infrastructure/       # Shared infrastructure services
│   │       ├── file_reader.py    # Generic file reading
│   │       ├── result_writer.py  # Generic result writing
│   │       ├── request.py        # Integrated I/O wrapper
│   │       └── performance/      # Performance monitoring
│   └── algorithm.py              # Entry point (Ocean Runner integration)
└── tests/                        # Mirror src structure
    ├── age_average/
    │   ├── domain/
    │   ├── application/
    │   └── infrastructure/
    └── shared/
```

### File Naming
- **Modules**: `snake_case.py`
- **Classes**: Match the primary class name: `input_parser.py` → `InputParser`
- **Tests**: `test_<module_name>.py`

---

## Class Organization

**STRICTLY follow this order in ALL classes:**

```python
class ExampleClass:
    """
    1. Class docstring (Google style).
    
    Brief description of the class purpose and responsibility.
    """
    
    # 2. Public class attributes
    DEFAULT_TIMEOUT = 30
    VERSION = "1.0.0"
    
    # 3. Private class attributes
    _internal_counter = 0
    _config_cache = {}
    
    # 4. Special methods (dunder methods)
    def __init__(self, dependency: Dependency):
        """
        Initialize the instance.
        
        Args:
            dependency: Description of dependency
        """
        self.dependency = dependency
        self._internal_state = None
    
    def __str__(self) -> str:
        """String representation."""
        return f"ExampleClass({self.dependency})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"ExampleClass(dependency={self.dependency!r})"
    
    # 5. Public methods (alphabetically ordered)
    def calculate_result(self, input_data: str) -> dict:
        """
        Public method for external use.
        
        Args:
            input_data: Description
            
        Returns:
            Dictionary with results
            
        Raises:
            ValueError: If input is invalid
        """
        validated = self._validate_input(input_data)
        return self._process_data(validated)
    
    def get_status(self) -> str:
        """Get current status."""
        return self._internal_state or "idle"
    
    # 6. Private methods (alphabetically ordered)
    def _process_data(self, data: str) -> dict:
        """Internal processing logic."""
        pass
    
    def _validate_input(self, data: str) -> str:
        """Internal validation logic."""
        if not data:
            raise ValueError("Data cannot be empty")
        return data.strip()
```

### Method Ordering Rules

1. **Special methods**: `__init__`, `__str__`, `__repr__`, `__eq__`, etc.
2. **Class methods**: `@classmethod` decorators
3. **Static methods**: `@staticmethod` decorators
4. **Properties**: `@property` decorators
5. **Public methods**: Alphabetically sorted
6. **Private methods**: Alphabetically sorted (prefix with `_`)

---

## Naming Conventions

### Python Standard (PEP 8)

| Element | Convention | Example |
|---------|-----------|---------|
| **Variables** | `snake_case` | `user_age`, `total_count` |
| **Functions** | `snake_case` | `calculate_average()`, `parse_input()` |
| **Classes** | `PascalCase` | `InputParser`, `AgeCalculator` |
| **Constants** | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| **Private** | `_prefix` | `_internal_method()`, `_cache` |
| **Modules** | `snake_case` | `input_parser.py`, `age_statistics.py` |

### Semantic Naming

✅ **DO**: Use descriptive, intention-revealing names
```python
def calculate_average_age(ages: list[int]) -> float:
    """Clear what it does."""
    return sum(ages) / len(ages)

def extract_ages(data: dict) -> list[int]:
    """Clear input and output."""
    pass
```

❌ **DON'T**: Use abbreviations or unclear names
```python
def calc(d):  # What does this calculate? What is 'd'?
    pass

def proc_data(x):  # Too vague
    pass
```

### Boolean Variables
Prefix with `is_`, `has_`, `can_`, `should_`

```python
is_valid = True
has_errors = False
can_process = True
should_retry = False
```

---

## Error Handling

### Exception Hierarchy

All custom exceptions inherit from a base exception:

```
AlgorithmError (Exception)
├── ValidationError        # Input validation failures
├── ParsingError          # Data parsing failures
├── CalculationError      # Business logic failures
└── FileOperationError    # I/O failures
```

### Creating Custom Exceptions

```python
# shared/domain/exceptions/algorithm_error.py
class AlgorithmError(Exception):
    """Base exception for all algorithm-related errors."""
    pass

# shared/domain/exceptions/validation_error.py
class ValidationError(AlgorithmError):
    """Raised when data validation fails."""
    pass
```

### Exception Handling Best Practices

✅ **DO**: Catch specific exceptions, log appropriately, re-raise or wrap

```python
def extract_ages(self, text: str, source: str) -> list[int]:
    """Extract ages with proper error handling."""
    try:
        data = json.loads(text)
        return self._extract_from_data(data)
    except json.JSONDecodeError as e:
        self.logger.error(f"JSON parsing failed for {source}: {e}")
        raise ParsingError(f"Invalid JSON in {source}: {e}")
    except KeyError as e:
        self.logger.error(f"Missing required field in {source}: {e}")
        raise ValidationError(f"Missing field {e} in {source}")
```

❌ **DON'T**: Use bare except or swallow exceptions

```python
def bad_example():
    try:
        risky_operation()
    except:  # Too broad!
        pass  # Error silently swallowed!
```

### Error Messages
- **Be specific**: Include context (file names, values, etc.)
- **Be actionable**: Tell what went wrong and why
- **Use consistent format**: `"<Action> failed for <context>: <reason>"`

```python
# Good error messages
raise ValidationError(f"Empty or invalid input text from {source_name}")
raise ParsingError(f"Invalid JSON structure in {file_name}: expected array or object with 'ages' field")
raise CalculationError(f"Cannot calculate statistics: no valid ages found in {len(input_files)} input files")
```

---

## Testing Standards

### Test Organization

Mirror the `src/` directory structure:

```
tests/
├── age_average/
│   ├── domain/
│   │   └── test_age_statistics.py
│   ├── application/
│   │   └── test_input_parser.py
│   └── infrastructure/
│       └── test_file_reader.py
└── shared/
    └── domain/
        └── test_app_config.py
```

### Test Class Structure

```python
"""Tests for InputParser service."""

import pytest
from age_average.application.input_parser import InputParser
from shared.domain.exceptions.parsing_error import ParsingError


class TestInputParser:
    """Test suite for InputParser."""
    
    @pytest.fixture
    def parser(self, mock_logger):
        """Create parser instance for testing."""
        return InputParser(mock_logger)
    
    def test_extract_ages_from_array_format(self, parser):
        """Test extracting ages from array of objects."""
        # Arrange
        json_text = '[{"user_id": 1, "age": 25}]'
        
        # Act
        result = parser.extract_ages(json_text, "test.json")
        
        # Assert
        assert result == [25]
        assert len(result) == 1
    
    def test_extract_ages_raises_error_on_invalid_json(self, parser):
        """Test that invalid JSON raises ParsingError."""
        # Arrange
        invalid_json = "not valid json"
        
        # Act & Assert
        with pytest.raises(ParsingError):
            parser.extract_ages(invalid_json, "test.json")
```

### Testing Principles

1. **Unit Tests**: Test single class in isolation
   - Mock external dependencies
   - Fast execution (< 100ms per test)
   - No I/O operations

2. **Integration Tests**: Test interaction between classes
   - Minimal mocking
   - Use test fixtures/data
   - Test realistic scenarios

3. **Test Coverage**: Aim for 80%+ coverage
   ```bash
   pytest --cov=algorithm --cov-report=term-missing
   ```

### Test Naming

Pattern: `test_<method>_<scenario>_<expected_result>`

```python
def test_calculate_statistics_with_valid_ages_returns_correct_stats(self):
    pass

def test_extract_ages_with_empty_input_raises_validation_error(self):
    pass

def test_read_text_with_nonexistent_file_raises_file_operation_error(self):
    pass
```

### Arrange-Act-Assert Pattern

```python
def test_example(self):
    # Arrange: Set up test data and dependencies
    ages = [10, 20, 30]
    calculator = AgeStatisticsCalculator(mock_logger)
    
    # Act: Execute the method under test
    result = calculator.calculate(ages)
    
    # Assert: Verify the result
    assert result.average == 20.0
    assert result.minimum == 10
    assert result.maximum == 30
```

---

## Documentation

### Module Docstrings

```python
"""
Service for parsing input data from different formats.

This module provides the InputParser class which handles extraction
of age data from various JSON formats. It follows the Single Responsibility
Principle by focusing solely on input parsing.
"""
```

### Class Docstrings (Google Style)

```python
class InputParser:
    """
    Parses input data from various formats and extracts age information.
    
    This class supports multiple JSON formats:
    - Array of objects with age field
    - Object with ages array field
    
    Attributes:
        logger: Logger instance for debugging
        age_extractor: Component for extracting ages from parsed data
        
    Example:
        >>> parser = InputParser(logger)
        >>> ages = parser.extract_ages('[{"age": 25}]', "data.json")
        >>> print(ages)
        [25]
    """
```

### Function Docstrings

```python
def extract_ages(self, text: str, source_name: str) -> list[int]:
    """
    Extract ages from JSON text supporting multiple formats.
    
    Parses JSON and extracts age values using the configured
    extraction strategy. Supports both array and object formats.
    
    Args:
        text: JSON text content to parse
        source_name: Name of the source file (used for error messages)
        
    Returns:
        List of extracted age values (integers)
        
    Raises:
        ParsingError: If JSON parsing fails or format is invalid
        ValidationError: If input is empty or no ages are found
        
    Example:
        >>> parser.extract_ages('[{"age": 30}]', "users.json")
        [30]
    """
```

### Type Hints

**Always use type hints** for function signatures:

```python
from typing import Optional, Union
from pathlib import Path

def read_text(self, path: Path) -> str:
    """Read text with type hints."""
    pass

def calculate_average(self, ages: list[int]) -> float:
    """Calculate with type hints."""
    pass

def get_config_value(self, key: str, default: Optional[str] = None) -> str:
    """Optional parameter with type hint."""
    pass
```

---

## Configuration Management

### Pydantic Models

Use Pydantic for all configuration with validation:

```python
from pydantic import BaseModel, Field, field_validator

class OutputConfig(BaseModel):
    """Configuration for output generation."""
    
    # Fields with defaults and documentation
    filename: str = Field(
        default="age_statistics_output.json",
        description="Name of the output file"
    )
    format: str = Field(
        default="json",
        description="Output format (json, csv, etc.)"
    )
    pretty_print: bool = Field(
        default=True,
        description="Whether to format JSON with indentation"
    )
    
    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate format is supported."""
        allowed = ["json", "csv", "xml"]
        if v not in allowed:
            raise ValueError(f"Format must be one of {allowed}")
        return v
```

### Configuration Composition

```python
class AppConfig(BaseModel):
    """Main application configuration."""
    
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    
    @classmethod
    def load(cls) -> "AppConfig":
        """
        Load configuration from file with intelligent fallback.
        
        Resolution order:
        1. CONFIG_PATH environment variable
        2. /config.yaml (production)
        3. ./config.yaml (development)
        
        Returns:
            Loaded and validated configuration
        """
        path = cls._resolve_config_path()
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

### Environment Variables

Use environment variables for sensitive or environment-specific values:

```python
import os

class DatabaseConfig(BaseModel):
    """Database configuration with env var support."""
    
    host: str = Field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    password: str = Field(default_factory=lambda: os.getenv("DB_PASSWORD", ""))
```

---

## Code Examples

### Complete Service Example

```python
"""Service for calculating age statistics."""

from logging import Logger
from shared.domain.exceptions.calculation_error import CalculationError
from age_average.domain.age_statistics import AgeStatistics


class AgeStatisticsCalculator:
    """
    Calculates statistical metrics for age data.
    
    Follows Single Responsibility Principle by focusing solely on
    age statistics calculation. Uses dependency injection for logger.
    
    Attributes:
        logger: Logger instance for debugging and monitoring
    """
    
    def __init__(self, logger: Logger):
        """
        Initialize the calculator.
        
        Args:
            logger: Logger instance for output
        """
        self.logger = logger
    
    def calculate(self, ages: list[int]) -> AgeStatistics:
        """
        Calculate min, max, and average age from a list.
        
        Args:
            ages: List of age values (must not be empty)
            
        Returns:
            AgeStatistics object with calculated metrics
            
        Raises:
            CalculationError: If ages list is empty
            
        Example:
            >>> calc = AgeStatisticsCalculator(logger)
            >>> stats = calc.calculate([20, 30, 40])
            >>> print(stats.average)
            30.0
        """
        if not ages:
            raise CalculationError("Cannot calculate statistics: empty ages list")
        
        stats = AgeStatistics(
            minimum=min(ages),
            maximum=max(ages),
            average=round(sum(ages) / len(ages), 2)
        )
        
        self.logger.info(
            f"Calculated statistics for {len(ages)} ages: "
            f"Min={stats.minimum}, Max={stats.maximum}, Avg={stats.average}"
        )
        
        return stats
```

### Complete Domain Model Example

```python
"""Domain model for age statistics."""

from pydantic import BaseModel, Field


class AgeStatistics(BaseModel):
    """
    Value object representing age statistics.
    
    Immutable data class following Domain-Driven Design principles.
    Uses Pydantic for validation and serialization.
    
    Attributes:
        minimum: Minimum age value
        maximum: Maximum age value
        average: Average (mean) age value
    """
    
    minimum: int = Field(..., ge=0, description="Minimum age")
    maximum: int = Field(..., ge=0, description="Maximum age")
    average: float = Field(..., ge=0.0, description="Average age")
    
    @property
    def range(self) -> int:
        """Calculate age range (max - min)."""
        return self.maximum - self.minimum
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Ages: min={self.minimum}, max={self.maximum}, avg={self.average:.2f}"
```

---

## Ocean Protocol Patterns

### Pattern 1: Input Parser Strategy

**Purpose**: Handle multiple input formats dynamically.

```python
class InputParser:
    """
    Parse various input formats using strategy pattern.
    
    Supports multiple JSON structures:
    - Array of objects with field
    - Object with array field
    - Nested structures
    """
    
    def extract_data(self, text: str, source_name: str) -> list[DomainObject]:
        """Extract data supporting multiple formats."""
        data = self._parse_json(text, source_name)
        
        if self._is_array_format(data):
            return self._extract_from_array(data)
        elif self._is_object_format(data):
            return self._extract_from_object(data)
        else:
            raise ParsingError(
                f"Unsupported format in {source_name}: "
                f"expected array or object with data field"
            )
    
    def _is_array_format(self, data: Any) -> bool:
        """Check if data is array format."""
        return isinstance(data, list)
    
    def _is_object_format(self, data: Any) -> bool:
        """Check if data is object format with data field."""
        return isinstance(data, dict) and 'data' in data
```

### Pattern 2: File Reader with Validation

**Purpose**: Safe file reading with comprehensive validation.

```python
class FileReader:
    """Read files with validation and error handling."""
    
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def read_text(self, path: Path) -> str:
        """
        Read text file with validation.
        
        Args:
            path: Path to file
            
        Returns:
            File content as string
            
        Raises:
            FileOperationError: If file not found or unreadable
            ValidationError: If file too large
        """
        # Validate existence
        if not path.exists():
            raise FileOperationError(f"File not found: {path}")
        
        # Validate size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise ValidationError(
                f"File too large: {size_mb:.2f}MB "
                f"(max: {self.MAX_FILE_SIZE_MB}MB)"
            )
        
        # Read with error handling
        try:
            content = path.read_text(encoding='utf-8')
            self.logger.debug(f"Read {len(content)} characters from {path.name}")
            return content
        except Exception as e:
            raise FileOperationError(f"Error reading {path}: {e}")
```

### Pattern 3: Domain Validation

**Purpose**: Validate business rules in domain models.

```python
class AgeInputParameters(InputParameters):
    """Input parameters with domain validation."""
    
    ages: list[int]
    
    @field_validator('ages')
    @classmethod
    def validate_ages(cls, v: list[int]) -> list[int]:
        """Validate age values according to business rules."""
        if not v:
            raise ValueError("Ages list cannot be empty")
        
        for age in v:
            if not (0 <= age <= 150):
                raise ValueError(
                    f"Invalid age: {age}. Must be between 0 and 150"
                )
        
        return v
    
    @field_validator('ages')
    @classmethod
    def validate_reasonable_dataset_size(cls, v: list[int]) -> list[int]:
        """Ensure dataset size is reasonable."""
        if len(v) > 1_000_000:
            raise ValueError(
                f"Dataset too large: {len(v)} items "
                f"(max: 1,000,000)"
            )
        return v
```

### Pattern 4: Configuration Loading with Environment Override

**Purpose**: Load configuration with environment variable fallback.

```python
class AppConfig(BaseModel):
    """Application configuration with smart loading."""
    
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    @classmethod
    def load(cls) -> "AppConfig":
        """
        Load configuration from file with environment override.
        
        Resolution order:
        1. CONFIG_PATH environment variable (if set)
        2. /config.yaml (Docker/production)
        3. ./config.yaml (development/testing)
        
        Returns:
            Loaded and validated configuration
            
        Raises:
            FileNotFoundError: If no config file found
            ValidationError: If config invalid
        """
        path = cls._resolve_config_path()
        with open(path) as f:
            data = yaml.safe_load(f)
        
        # Override with environment variables
        if env_name := os.getenv("ALGORITHM_NAME"):
            data.setdefault('algorithm', {})['name'] = env_name
        
        if env_level := os.getenv("LOG_LEVEL"):
            data.setdefault('logging', {})['level'] = env_level
        
        return cls(**data)
```

### Pattern 5: Structured Logging with Context

**Purpose**: Rich logging with contextual information.

```python
class AgeStatisticsCalculator:
    """Calculator with structured logging."""
    
    def calculate(self, ages: list[int]) -> AgeStatistics:
        """Calculate with structured logging."""
        start_time = time.time()
        
        try:
            stats = self._perform_calculation(ages)
            
            # Log success with context
            self.logger.info(
                f"Calculated statistics for {len(ages)} ages",
                extra={
                    'age_count': len(ages),
                    'min_age': stats.minimum,
                    'max_age': stats.maximum,
                    'avg_age': stats.average,
                    'execution_time_ms': (time.time() - start_time) * 1000,
                    'status': 'success'
                }
            )
            
            return stats
            
        except Exception as e:
            # Log failure with context
            self.logger.error(
                f"Calculation failed: {e}",
                extra={
                    'age_count': len(ages),
                    'execution_time_ms': (time.time() - start_time) * 1000,
                    'status': 'error',
                    'error_type': type(e).__name__
                }
            )
            raise
```

### Pattern 6: Performance Monitoring

**Purpose**: Track algorithm performance metrics.

```python
class PerformanceMonitor:
    """Monitor algorithm performance."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.start_time = time.time()
        self.process = psutil.Process()
        self.memory_start = self.process.memory_info().rss
    
    def get_metrics(self) -> dict[str, float]:
        """
        Get current performance metrics.
        
        Returns:
            Dictionary with execution time, memory usage, CPU usage
        """
        memory_current = self.process.memory_info().rss
        memory_peak = self.process.memory_info().vms
        
        return {
            'execution_time': time.time() - self.start_time,
            'memory_usage_mb': (memory_current - self.memory_start) / 1024 / 1024,
            'peak_memory_mb': memory_peak / 1024 / 1024,
            'cpu_percent': self.process.cpu_percent()
        }
    
    def log_metrics(self) -> None:
        """Log current metrics."""
        metrics = self.get_metrics()
        self.logger.info(
            f"Algorithm execution completed: "
            f"execution_time={metrics['execution_time']:.3f}s, "
            f"memory_usage={metrics['memory_usage_mb']:.2f}MB, "
            f"peak_memory={metrics['peak_memory_mb']:.2f}MB, "
            f"cpu_percent={metrics['cpu_percent']:.2f}%"
        )
```

### Pattern 7: Modern Ocean Runner Integration with BaseAlgorithm

**Purpose**: Properly integrate with Ocean Runner framework using BaseAlgorithm.

```python
from shared.infrastructure.base_algorithm import BaseAlgorithm
from shared.infrastructure.request import Request
from shared.infrastructure.response import Response

class MyAlgorithm(BaseAlgorithm):
    """Algorithm with automatic Ocean Runner integration."""
    
    def __init__(
        self,
        deps: AlgorithmDependencies,
        calculate_action: MyCalculateAction,
        config: AppConfig,
    ):
        """Initialize with injected dependencies."""
        super().__init__()
        self.config = config
        self.algorithm = deps.ocean_algorithm
        self.request = deps.request  # Input operations
        self.response = deps.response  # Output operations
        self.calculate_action = calculate_action
        
        # Callbacks registered automatically by BaseAlgorithm
        self.register_callbacks(deps.ocean_algorithm)
    
    @classmethod
    def create(cls, config: AppConfig) -> "MyAlgorithm":
        """Factory method - composition root for bounded context."""
        # Create common infrastructure dependencies
        deps = AlgorithmDependencies.create(MyRequestDTO)
        
        # Create bounded context specific dependencies
        mapper = MyMapper()
        repository = MyRepository(deps.request, mapper)
        action = MyCalculateAction(repository)
        
        return cls(deps, action, config)
    
    def validate_input(self, algo: Algorithm) -> None:
        """
        Validate inputs before processing.
        
        Performance monitoring starts automatically via BaseAlgorithm.
        
        Args:
            algo: Algorithm instance with job details
            
        Raises:
            ValidationError: If validation fails
        """
        algo.logger.info("validate: starting")
        
        input_count = self.request.count()
        if input_count == 0:
            raise ValidationError("No input files provided")
        
        algo.logger.info(f"Found {input_count} input files to process")
    
    def run(self, algo: Algorithm) -> Results:
        """
        Execute main algorithm logic.
        
        Args:
            algo: Algorithm instance
            
        Returns:
            Results object with calculated data
        """
        algo.logger.info("run: starting")
        
        # Use integrated services from request
        parser = InputParser(algo.logger)
        calculator = MyCalculator(algo.logger)
        
        # Process inputs using integrated FileReader
        all_data = []
        for idx, path in self.request.iter_files():
            algo.logger.info(f"Processing input {idx}: {path.name}")
            text = self.request.file_reader.read_text(path)
            data = parser.extract_data(text, path.name)
            all_data.extend(data)
        
        # Calculate results
        results = calculator.calculate(all_data)
        
        return results
    
    def save(self, algo: Algorithm, results: Results, base_path: Path) -> None:
        """
        Save results to output.
        
        Performance monitoring stops automatically via BaseAlgorithm.
        
        Args:
            algo: Algorithm instance
            results: Results to save
            base_path: Base path for outputs
        """
        algo.logger.info("save: starting")
        
        # Use integrated ResponseWriter via Response
        output_file = base_path / self.config.output.filename
        self.response.write_results(results, output_file)
        
        algo.logger.info(f"Results written to {output_file}")
        # Performance metrics logged automatically

# Usage in algorithm.py entry point
algorithm = MyAlgorithm.create(AppConfig.load()).algorithm
```

### Pattern 8: Test Fixtures

**Purpose**: Reusable test data and mocks.

```python
import pytest
from logging import Logger

@pytest.fixture
def mock_logger() -> Logger:
    """Create mock logger for testing."""
    return logging.getLogger('test')

@pytest.fixture
def sample_age_data() -> list[dict]:
    """Sample age data for testing."""
    return [
        {"user_id": 1, "age": 25, "name": "Alice"},
        {"user_id": 2, "age": 30, "name": "Bob"},
        {"user_id": 3, "age": 35, "name": "Charlie"}
    ]

@pytest.fixture
def temp_input_file(tmp_path: Path, sample_age_data: list[dict]) -> Path:
    """Create temporary input file."""
    file_path = tmp_path / "test_input.json"
    file_path.write_text(json.dumps(sample_age_data))
    return file_path

@pytest.fixture
def input_parser(mock_logger: Logger) -> InputParser:
    """Create InputParser instance."""
    return InputParser(mock_logger)
```

---

## Creating New Bounded Contexts

When you need to add a new algorithm or feature (bounded context), follow this systematic approach.

### Step 1: Plan Your Bounded Context

Define:
- **Domain**: What business entities and value objects do you need?
- **Use Cases**: What are the main workflows?
- **External Dependencies**: What infrastructure adapters are needed?

**Example**: Creating a `price_analysis` bounded context

```
Business Goal: Analyze price trends from historical data
Domain: PricePoint, PriceStatistics, PriceTrend
Use Cases: Parse prices, calculate statistics, detect trends
Infrastructure: CSV reader, chart generator
```

### Step 2: Create Directory Structure

```bash
mkdir -p algorithm/src/price_analysis/{domain,services,infrastructure}
mkdir -p algorithm/tests/price_analysis/{domain,services,infrastructure}
```

Resulting structure:
```
algorithm/src/price_analysis/
├── domain/
│   ├── __init__.py
│   ├── price_input_parameters.py
│   ├── price_results.py
│   ├── price_point.py
│   └── price_statistics.py
├── application/
│   ├── __init__.py
│   ├── price_parser.py
│   └── price_statistics_calculator.py
└── infrastructure/
    ├── __init__.py
    ├── csv_reader.py
    └── chart_generator.py
```

### Step 3: Implement Domain Layer

Start with pure domain models (no dependencies).

**`price_input_parameters.py`**:
```python
"""Input parameters for price analysis."""

from pydantic import Field, field_validator
from shared.domain.input_parameters import InputParameters


class PriceInputParameters(InputParameters):
    """Input parameters for price analysis algorithm."""
    
    min_price: float = Field(default=0.0, ge=0.0)
    max_price: float = Field(default=10000.0, ge=0.0)
    currency: str = Field(default="USD", pattern=r'^[A-Z]{3}$')
    
    @field_validator('max_price')
    @classmethod
    def validate_price_range(cls, v: float, info) -> float:
        """Ensure max_price > min_price."""
        if 'min_price' in info.data and v <= info.data['min_price']:
            raise ValueError("max_price must be greater than min_price")
        return v
```

**`price_point.py`**:
```python
"""Domain model for price point."""

from datetime import datetime
from pydantic import BaseModel, Field


class PricePoint(BaseModel):
    """Represents a single price observation."""
    
    timestamp: datetime
    price: float = Field(gt=0.0)
    volume: float = Field(ge=0.0)
    currency: str = Field(pattern=r'^[A-Z]{3}$')
    
    @property
    def total_value(self) -> float:
        """Calculate total value (price * volume)."""
        return self.price * self.volume
```

**`price_statistics.py`**:
```python
"""Domain model for price statistics."""

from pydantic import BaseModel, Field


class PriceStatistics(BaseModel):
    """Statistical metrics for prices."""
    
    min_price: float = Field(ge=0.0)
    max_price: float = Field(ge=0.0)
    avg_price: float = Field(ge=0.0)
    median_price: float = Field(ge=0.0)
    std_deviation: float = Field(ge=0.0)
    total_volume: float = Field(ge=0.0)
    
    @property
    def price_range(self) -> float:
        """Calculate price range."""
        return self.max_price - self.min_price
```

**`price_results.py`**:
```python
"""Results model for price analysis."""

from shared.domain.results import Results
from .price_statistics import PriceStatistics


class PriceResults(Results):
    """Results from price analysis algorithm."""
    
    statistics: PriceStatistics
    data_points_analyzed: int
    currency: str
```

### Step 4: Implement Service Layer

Business logic and use cases.

**`price_parser.py`**:
```python
"""Service for parsing price data."""

from logging import Logger
from datetime import datetime
from shared.domain.exceptions.parsing_error import ParsingError
from shared.domain.exceptions.validation_error import ValidationError
from ..domain.price_point import PricePoint


class PriceParser:
    """
    Parse price data from various formats.
    
    Follows Single Responsibility Principle by focusing only on parsing.
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def parse_prices(self, data: list[dict], source: str) -> list[PricePoint]:
        """
        Parse price data from dictionaries.
        
        Args:
            data: List of price dictionaries
            source: Source name for error messages
            
        Returns:
            List of PricePoint objects
            
        Raises:
            ParsingError: If parsing fails
            ValidationError: If data invalid
        """
        if not data:
            raise ValidationError(f"Empty data from {source}")
        
        prices = []
        for idx, item in enumerate(data):
            try:
                price_point = self._parse_single_price(item)
                prices.append(price_point)
            except Exception as e:
                self.logger.warning(
                    f"Skipping invalid price at index {idx} in {source}: {e}"
                )
        
        if not prices:
            raise ParsingError(f"No valid prices found in {source}")
        
        self.logger.info(f"Parsed {len(prices)} prices from {source}")
        return prices
    
    def _parse_single_price(self, item: dict) -> PricePoint:
        """Parse single price item."""
        return PricePoint(
            timestamp=datetime.fromisoformat(item['timestamp']),
            price=float(item['price']),
            volume=float(item.get('volume', 0.0)),
            currency=item.get('currency', 'USD')
        )
```

**`price_statistics_calculator.py`**:
```python
"""Service for calculating price statistics."""

from logging import Logger
from statistics import mean, median, stdev
from shared.domain.exceptions.calculation_error import CalculationError
from ..domain.price_point import PricePoint
from ..domain.price_statistics import PriceStatistics


class PriceStatisticsCalculator:
    """
    Calculate statistical metrics for prices.
    
    Follows Single Responsibility Principle.
    """
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def calculate(self, prices: list[PricePoint]) -> PriceStatistics:
        """
        Calculate price statistics.
        
        Args:
            prices: List of price points
            
        Returns:
            PriceStatistics with calculated metrics
            
        Raises:
            CalculationError: If calculation fails
        """
        if not prices:
            raise CalculationError("Cannot calculate statistics: empty price list")
        
        if len(prices) == 1:
            return self._single_price_stats(prices[0])
        
        price_values = [p.price for p in prices]
        
        stats = PriceStatistics(
            min_price=min(price_values),
            max_price=max(price_values),
            avg_price=round(mean(price_values), 2),
            median_price=round(median(price_values), 2),
            std_deviation=round(stdev(price_values), 2),
            total_volume=sum(p.volume for p in prices)
        )
        
        self.logger.info(
            f"Calculated statistics for {len(prices)} prices: "
            f"Min={stats.min_price}, Max={stats.max_price}, "
            f"Avg={stats.avg_price}, StdDev={stats.std_deviation}"
        )
        
        return stats
    
    def _single_price_stats(self, price: PricePoint) -> PriceStatistics:
        """Handle single price case."""
        return PriceStatistics(
            min_price=price.price,
            max_price=price.price,
            avg_price=price.price,
            median_price=price.price,
            std_deviation=0.0,
            total_volume=price.volume
        )
```

### Step 5: Implement Infrastructure Layer

External adapters (file I/O, APIs, etc.).

**`csv_reader.py`**:
```python
"""Infrastructure adapter for CSV file reading."""

import csv
from pathlib import Path
from logging import Logger
from shared.domain.exceptions.file_operation_error import FileOperationError


class CSVReader:
    """
    Read and parse CSV files.
    
    Infrastructure adapter following hexagonal architecture.
    """
    
    MAX_FILE_SIZE_MB = 50
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def read_csv(self, path: Path) -> list[dict]:
        """
        Read CSV file and return as list of dictionaries.
        
        Args:
            path: Path to CSV file
            
        Returns:
            List of dictionaries (one per row)
            
        Raises:
            FileOperationError: If file cannot be read
        """
        if not path.exists():
            raise FileOperationError(f"File not found: {path}")
        
        # Validate size
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise FileOperationError(
                f"File too large: {size_mb:.2f}MB (max: {self.MAX_FILE_SIZE_MB}MB)"
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            self.logger.debug(f"Read {len(data)} rows from {path.name}")
            return data
            
        except Exception as e:
            raise FileOperationError(f"Error reading CSV {path}: {e}")
```

### Step 6: Integrate with Algorithm Entry Point

Update `algorithm.py` to use your new bounded context.

```python
"""Algorithm entry point."""

from pathlib import Path
from ocean_runner import Algorithm, Config

# Import your new bounded context
from price_analysis.domain.price_input_parameters import PriceInputParameters
from price_analysis.domain.price_results import PriceResults
from price_analysis.application.price_parser import PriceParser
from price_analysis.application.price_statistics_calculator import PriceStatisticsCalculator

from shared.infrastructure.base_algorithm import BaseAlgorithm
from shared.domain.config.app_config import AppConfig
from shared.infrastructure.request import Request
from shared.infrastructure.response import Response


class PriceAnalysisAlgorithm(BaseAlgorithm):
    """Price analysis algorithm with automatic monitoring and service integration."""
    
    def __init__(
        self,
        deps: AlgorithmDependencies,
        calculate_action: CalculatePriceStatisticsAction,
        config: AppConfig,
    ):
        """Initialize with injected dependencies."""
        super().__init__()
        self.config = config
        self.algorithm = deps.ocean_algorithm
        self.request = deps.request  # Input operations
        self.response = deps.response  # Output operations
        self.calculate_action = calculate_action
        
        # Callbacks registered automatically by BaseAlgorithm
        self.register_callbacks(deps.ocean_algorithm)
    
    @classmethod
    def create(cls, config: AppConfig) -> "PriceAnalysisAlgorithm":
        """Factory method - composition root for price_analysis bounded context."""
        # Create common infrastructure dependencies
        deps = AlgorithmDependencies.create(PriceRequestDTO)
        
        # Create bounded context specific dependencies
        mapper = PriceMapper()
        repository = PriceOceanRepository(deps.request, mapper)
        action = CalculatePriceStatisticsAction(repository)
        
        return cls(deps, action, config)
    
    def validate_input(self, algo: Algorithm) -> None:
        """Validate inputs before processing."""
        algo.logger.info("validate: starting")
        
        input_count = self.request.count()
        if input_count == 0:
            raise ValidationError("No input files provided")
        
        algo.logger.info(f"Found {input_count} input files")
    
    def run(self, algo: Algorithm) -> PriceResponseDTO:
        """Execute price analysis - delegates to action."""
        algo.logger.info("run: starting")
        
        # Delegate business logic to action (handles all exceptions internally)
        return self.calculate_action.execute()
    
    def save(self, algo: Algorithm, results: ResponseDTO, base_path: Path) -> None:
        """Save results."""
        algo.logger.info("save: starting")
        
        # Use integrated ResponseWriter via Response
        output_file = base_path / self.config.output.filename
        self.response.write_results(results, output_file)
        
        algo.logger.info(f"Results written to {output_file}")
        # Performance metrics logged automatically


# Update algorithm.py entry point
algorithm = PriceAnalysisAlgorithm.create(AppConfig.load()).algorithm
```

### Step 7: Write Tests

Mirror the source structure with comprehensive tests.

**`tests/price_analysis/domain/test_price_point.py`**:
```python
"""Tests for PricePoint domain model."""

import pytest
from datetime import datetime
from price_analysis.domain.price_point import PricePoint


class TestPricePoint:
    """Test suite for PricePoint."""
    
    def test_create_valid_price_point(self):
        """Test creating valid price point."""
        # Arrange & Act
        price = PricePoint(
            timestamp=datetime(2026, 1, 1, 12, 0),
            price=100.50,
            volume=1000.0,
            currency="USD"
        )
        
        # Assert
        assert price.price == 100.50
        assert price.volume == 1000.0
        assert price.total_value == 100500.0
    
    def test_price_must_be_positive(self):
        """Test that price must be > 0."""
        # Act & Assert
        with pytest.raises(ValueError):
            PricePoint(
                timestamp=datetime.now(),
                price=0.0,  # Invalid
                volume=100.0,
                currency="USD"
            )
    
    def test_currency_must_be_three_letters(self):
        """Test currency validation."""
        # Act & Assert
        with pytest.raises(ValueError):
            PricePoint(
                timestamp=datetime.now(),
                price=100.0,
                volume=100.0,
                currency="US"  # Too short
            )
```

**`tests/price_analysis/application/test_price_statistics_calculator.py`**:
```python
"""Tests for PriceStatisticsCalculator service."""

import pytest
from datetime import datetime
from price_analysis.application.price_statistics_calculator import PriceStatisticsCalculator
from price_analysis.domain.price_point import PricePoint
from shared.domain.exceptions.calculation_error import CalculationError


class TestPriceStatisticsCalculator:
    """Test suite for PriceStatisticsCalculator."""
    
    @pytest.fixture
    def calculator(self, mock_logger):
        """Create calculator instance."""
        return PriceStatisticsCalculator(mock_logger)
    
    @pytest.fixture
    def sample_prices(self):
        """Create sample price data."""
        return [
            PricePoint(timestamp=datetime.now(), price=100.0, volume=10.0, currency="USD"),
            PricePoint(timestamp=datetime.now(), price=200.0, volume=20.0, currency="USD"),
            PricePoint(timestamp=datetime.now(), price=300.0, volume=30.0, currency="USD"),
        ]
    
    def test_calculate_with_valid_prices(self, calculator, sample_prices):
        """Test calculation with valid prices."""
        # Act
        stats = calculator.calculate(sample_prices)
        
        # Assert
        assert stats.min_price == 100.0
        assert stats.max_price == 300.0
        assert stats.avg_price == 200.0
        assert stats.total_volume == 60.0
        assert stats.std_deviation > 0
    
    def test_calculate_with_empty_list_raises_error(self, calculator):
        """Test that empty list raises CalculationError."""
        # Act & Assert
        with pytest.raises(CalculationError):
            calculator.calculate([])
```

### Step 8: Update Configuration (Optional)

Add bounded context-specific configuration if needed.

**`shared/domain/config/price_config.py`**:
```python
"""Configuration for price analysis."""

from pydantic import BaseModel, Field


class PriceConfig(BaseModel):
    """Price analysis configuration."""
    
    min_data_points: int = Field(default=10, ge=1)
    outlier_threshold_std: float = Field(default=3.0, gt=0.0)
    supported_currencies: list[str] = Field(default=["USD", "EUR", "GBP"])
```

Update `AppConfig`:
```python
class AppConfig(BaseModel):
    """Main application configuration."""
    
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    price: PriceConfig = Field(default_factory=PriceConfig)  # Add this
```

### Step 9: Documentation

Document your bounded context.

**`algorithm/src/price_analysis/README.md`**:
```markdown
# Price Analysis Bounded Context

## Overview

This bounded context implements price analysis functionality for historical price data.

## Domain Models

- **PricePoint**: Represents a single price observation with timestamp, price, volume, and currency
- **PriceStatistics**: Statistical metrics (min, max, avg, median, std deviation)
- **PriceResults**: Final results including statistics and metadata

## Services

- **PriceParser**: Parses price data from dictionaries into domain models
- **PriceStatisticsCalculator**: Calculates statistical metrics

## Infrastructure

- **CSVReader**: Reads CSV files containing price data

## Usage

```python
from price_analysis.application.price_parser import PriceParser
from price_analysis.application.price_statistics_calculator import PriceStatisticsCalculator

# Parse prices
parser = PriceParser(logger)
prices = parser.parse_prices(data, "source.csv")

# Calculate statistics
calculator = PriceStatisticsCalculator(logger)
stats = calculator.calculate(prices)
```

## Testing

Run tests:
```bash
pytest tests/price_analysis/ -v
```
```

### Checklist for New Bounded Context

- [ ] Directory structure created (domain/application/infrastructure)
- [ ] Domain models implemented with Pydantic validation
- [ ] Services implement business logic with dependency injection
- [ ] Infrastructure adapters handle external concerns
- [ ] All classes follow SOLID principles
- [ ] Type hints on all functions
- [ ] Docstrings on all public classes/methods
- [ ] Tests mirror source structure
- [ ] Unit tests for domain and services
- [ ] Integration tests for workflows
- [ ] Configuration updated if needed
- [ ] README documentation created
- [ ] algorithm.py updated to use new context
- [ ] All tests passing

---

## Best Practices Summary

### ✅ Always Do

1. **Follow Hexagonal Architecture**: Separate domain, services, and infrastructure
2. **Apply SOLID Principles**: Single responsibility, dependency injection
3. **Use Type Hints**: All function signatures must have types
4. **Write Docstrings**: Google style for all public classes and methods
5. **Handle Errors Properly**: Specific exceptions with context
6. **Test Thoroughly**: Unit tests for all services and domain logic
7. **Use Pydantic**: For all configuration and data models
8. **Log Appropriately**: Use injected logger for debugging
9. **Order Methods**: Follow the class organization structure
10. **Name Descriptively**: Clear, intention-revealing names

### ❌ Never Do

1. **Mix Layers**: Don't put business logic in infrastructure
2. **Use Bare Except**: Always catch specific exceptions
3. **Hardcode Values**: Use configuration files instead
4. **Skip Tests**: All new code must have tests
5. **Ignore Type Hints**: All functions need proper typing
6. **Write Vague Docstrings**: Be specific about behavior
7. **Create God Classes**: Keep classes focused and small
8. **Use Global State**: Use dependency injection instead
9. **Swallow Exceptions**: Log and re-raise or wrap appropriately
10. **Write Unclear Names**: Avoid abbreviations and vague terms

---

## Development Workflow

### Local Development Setup

#### Prerequisites
- Docker and Docker Compose
- Python 3.12 (for local testing without Docker)
- Git

#### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd ocean-algorithm-example

# Review project structure
ls -la algorithm/

# Check configuration
cat algorithm/config.yaml
```

### Running Tests

#### Using Docker (Recommended)
```bash
# Run all tests
docker compose run --rm algorithm pytest -v

# Run specific test file
docker compose run --rm algorithm pytest tests/age_average/application/test_input_parser.py -v

# Run with coverage
docker compose run --rm algorithm pytest --cov=algorithm --cov-report=term-missing

# Run only unit tests
docker compose run --rm algorithm pytest tests/ -m "not integration" -v
```

#### Local Python Environment
```bash
cd algorithm/

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies with uv
pip install uv
uv pip install -e ".[dev]"

# Run tests
pytest -v
```

### Running the Algorithm

#### Using Docker Compose
```bash
# Build and run
docker compose up --build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f algorithm

# Stop
docker compose down
```

#### Manual Docker Run
```bash
# Build image
docker build -t ocean-algorithm .

# Run container
docker run --rm \
  -v $(pwd)/_data:/data \
  ocean-algorithm
```

### Development Cycle

#### 1. Create Feature Branch
```bash
git checkout -b feature/new-bounded-context
```

#### 2. Implement Changes
Follow the architecture and guidelines in this document.

#### 3. Run Tests Locally
```bash
docker compose run --rm algorithm pytest -v
```

#### 4. Check Code Quality
```bash
# Run linting (if configured)
docker compose run --rm algorithm ruff check .

# Run type checking (if configured)
docker compose run --rm algorithm mypy algorithm/src/
```

#### 5. Commit Changes
```bash
git add .
git commit -m "feat: add price analysis bounded context"
```

#### 6. Push and Create PR
```bash
git push origin feature/new-bounded-context
```

### Configuration Management

#### Development Configuration
Use `algorithm/config.yaml` for default development settings.

#### Environment-Specific Configuration

Create `.env` file for environment overrides:
```bash
# .env
ALGORITHM_NAME=price_analysis
LOG_LEVEL=DEBUG
MAX_FILE_SIZE_MB=200
```

#### Docker Environment Variables
Override in `docker-compose.yaml`:
```yaml
services:
  algorithm:
    environment:
      - ALGORITHM_NAME=price_analysis
      - LOG_LEVEL=INFO
      - CONFIG_PATH=/config.yaml
```

### Performance Monitoring

#### View Metrics During Execution
```bash
# Follow logs in real-time
docker compose logs -f algorithm

# Look for performance metrics at end
# Example output:
# Algorithm execution completed: execution_time=0.107s, memory_usage=0.01MB, peak_memory=39.84MB, cpu_percent=0.00%
```

#### Analyze Test Performance
```bash
# Run tests with duration report
docker compose run --rm algorithm pytest --durations=10 -v
```

### Debugging

#### Interactive Debugging in Container
```bash
# Run container with interactive shell
docker compose run --rm algorithm bash

# Inside container, run Python REPL
python
>>> from algorithm.src.age_average.application.input_parser import InputParser
>>> # Test interactively
```

#### Debug Specific Test
```bash
# Run single test with verbose output
docker compose run --rm algorithm pytest tests/age_average/application/test_input_parser.py::TestInputParser::test_extract_ages_from_array_format -vv
```

#### View Container Logs
```bash
# Check algorithm logs
cat _data/logs/algorithm.log

# View with timestamps
docker compose logs --timestamps algorithm
```

### CI/CD Pipeline

#### GitHub Actions Workflow
Located at `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: docker compose run --rm algorithm pytest -v
      
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t ocean-algorithm .
```

#### Pipeline Stages
1. **Test**: Run all tests
2. **Build**: Build Docker image
3. **Quality**: Code quality checks (if configured)
4. **Deploy**: Push to registry (optional)

### Troubleshooting

#### Common Issues

**Issue**: Tests fail with import errors
```bash
# Solution: Rebuild container
docker compose build --no-cache algorithm
```

**Issue**: Configuration not loading
```bash
# Solution: Check config path and permissions
docker compose run --rm algorithm bash -c "ls -la /config.yaml && cat /config.yaml"
```

**Issue**: File not found errors
```bash
# Solution: Verify volume mounts
docker compose run --rm algorithm bash -c "ls -la /data/inputs/"
```

**Issue**: Performance degradation
```bash
# Solution: Check memory limits and usage
docker stats

# Increase memory if needed in docker-compose.yaml
services:
  algorithm:
    mem_limit: 2g
```

### Best Practices for Development

1. **Always run tests before committing**
   ```bash
   docker compose run --rm algorithm pytest -v
   ```

2. **Use feature branches**
   - Never commit directly to main/master
   - Use descriptive branch names: `feature/`, `fix/`, `refactor/`

3. **Write tests first (TDD)**
   - Write failing test
   - Implement feature
   - Verify test passes

4. **Keep commits atomic**
   - One logical change per commit
   - Use conventional commit messages

5. **Update documentation**
   - Update docstrings
   - Update README if needed
   - Document breaking changes

6. **Monitor performance**
   - Check execution time and memory usage
   - Optimize if metrics degrade

7. **Review error logs**
   - Check `_data/logs/algorithm.log`
   - Ensure proper error handling

---

## Code Review Checklist

Before committing code, verify:

- [ ] Follows hexagonal architecture (correct layer)
- [ ] SOLID principles applied
- [ ] Class methods in correct order
- [ ] All functions have type hints
- [ ] All public classes/methods have docstrings
- [ ] Custom exceptions used appropriately
- [ ] Tests written and passing
- [ ] No hardcoded values (use config)
- [ ] Logging added for debugging
- [ ] Error messages are descriptive
- [ ] Code is self-documenting with clear names
- [ ] No code duplication (DRY principle)

---

## Additional Resources

### Python & Design Patterns
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)

### Architecture & SOLID Principles
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Domain-Driven Design Quickly](https://www.infoq.com/minibooks/domain-driven-design-quickly/)

### Ocean Protocol
- [Ocean Protocol Documentation](https://docs.oceanprotocol.com/)
- [Compute-to-Data Documentation](https://docs.oceanprotocol.com/developers/compute-to-data/)
- [Ocean Protocol Python Library](https://github.com/oceanprotocol/ocean.py)
- [Algorithm Examples Repository](https://github.com/oceanprotocol/algo_examples)

### Testing & Quality
- [pytest Documentation](https://docs.pytest.org/)
- [pytest Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Python Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

### Tools & Libraries
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pydantic v2 Migration Guide](https://docs.pydantic.dev/latest/migration/)
- [uv - Fast Python Package Installer](https://github.com/astral-sh/uv)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Performance & Monitoring
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [Python Memory Management](https://realpython.com/python-memory-management/)

### Community Resources
- [Real Python](https://realpython.com/) - Python tutorials and best practices
- [Full Stack Python](https://www.fullstackpython.com/) - Comprehensive Python guide
- [Awesome Python](https://github.com/vinta/awesome-python) - Curated list of Python resources

---

**Document Version**: 2.0  
**Last Updated**: February 2026  
**Project**: Ocean Protocol Algorithm Template  
**Maintainer**: Development Team

---

## Summary

This guide provides everything needed to develop high-quality Ocean Protocol algorithms:

1. **Architecture**: Hexagonal architecture with clear layer separation
2. **SOLID Principles**: Practical application of design principles
3. **Code Organization**: Consistent structure and naming
4. **Error Handling**: Comprehensive exception hierarchy
5. **Testing**: Complete test coverage strategy
6. **Documentation**: Clear, maintainable documentation
7. **Patterns**: Ocean Protocol-specific patterns
8. **Bounded Contexts**: Step-by-step guide for new features
9. **Workflow**: Complete development and deployment process

Follow these guidelines consistently to ensure:
- ✅ Clean, maintainable code
- ✅ Comprehensive test coverage
- ✅ Proper error handling
- ✅ Clear documentation
- ✅ Scalable architecture
- ✅ Ocean Protocol compatibility

**Remember**: Good code is not just about making it work—it's about making it maintainable, testable, and understandable for future developers (including yourself!).

---

*For questions or suggestions about these guidelines, please open an issue or submit a pull request.*
