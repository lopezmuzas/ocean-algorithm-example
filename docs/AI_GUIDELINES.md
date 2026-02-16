# AI Development Guidelines - Quick Reference

**Optimized for LLM consumption. For detailed explanations, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

---

## Quick Reference

| Aspect | Rule |
|--------|------|
| **Architecture** | Hexagonal: Domain → Services → Infrastructure |
| **Class per file** | One class = One file |
| **Package structure** | ❌ DO NOT create `__init__.py` files |
| **Naming** | `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants) |
| **Methods order** | dunder → classmethod → staticmethod → property → public (α) → private (α) |
| **Type hints** | Mandatory on all functions |
| **Docstrings** | Google style on all public classes/methods |
| **Tests** | Mirror src/ structure, 80%+ coverage |
| **DI** | Always inject dependencies via `__init__` |

---

## Architecture Layers

```
algorithm/src/
├── shared/                    # Cross-cutting concerns
│   ├── domain/               # Config, base models, exceptions
│   └── infrastructure/       # Monitoring, utilities
│
├── <bounded_context>/        # e.g., age_average, price_analysis
│   ├── domain/              # Pure business logic (NO dependencies)
│   ├── application/         # Use cases (depend on domain)
│   └── infrastructure/      # I/O, APIs (depend on domain + application)
│
└── algorithm.py             # Orchestration (Ocean Runner integration)
```

### Layer Rules

| Layer | ✅ Allowed | ❌ Forbidden |
|-------|-----------|-------------|
| **Domain** | Pure functions, Pydantic models, business rules | I/O, framework imports, service imports |
| **Services** | Orchestrate domain, DI via constructor | Direct I/O, framework-specific code |
| **Infrastructure** | I/O, external APIs, framework integration | Business logic |

### Dependency Flow
```
Infrastructure → Services → Domain
(Outer layers depend on inner layers, NEVER reverse)
```

---

## SOLID Principles - Applied

### Single Responsibility
```python
# ✅ DO: One responsibility per class
class InputParser:
    def extract_ages(self, text: str) -> list[int]: pass

class AgeStatisticsCalculator:
    def calculate(self, ages: list[int]) -> AgeStatistics: pass

# ❌ DON'T: Multiple responsibilities
class DataProcessor:
    def parse_extract_calculate_write(self): pass
```

### Dependency Inversion
```python
# ✅ DO: Inject dependencies
class MyService:
    def __init__(self, logger: Logger, config: Config):
        self.logger = logger
        self.config = config

# ❌ DON'T: Create dependencies internally
class MyService:
    def __init__(self):
        self.logger = logging.getLogger()  # Hard dependency
```

---

## Class Organization - Strict Order

```python
class ExampleClass:
    """1. Class docstring (Google style)."""
    
    # 2. Public class attributes
    DEFAULT_VALUE = 100
    
    # 3. Private class attributes
    _internal_cache = {}
    
    # 4. Special methods (__dunder__)
    def __init__(self, dependency: Dep):
        self.dependency = dependency
        self._state = None
    
    def __str__(self) -> str:
        return f"Example({self.dependency})"
    
    # 5. Class methods
    @classmethod
    def from_config(cls, config: dict) -> "ExampleClass":
        return cls(config['dep'])
    
    # 6. Static methods
    @staticmethod
    def validate_input(value: int) -> bool:
        return value > 0
    
    # 7. Properties
    @property
    def status(self) -> str:
        return self._state or "idle"
    
    # 8. Public methods (alphabetically)
    def calculate(self, data: str) -> dict:
        validated = self._validate(data)
        return self._process(validated)
    
    def get_result(self) -> dict:
        return {"status": self.status}
    
    # 9. Private methods (alphabetically)
    def _process(self, data: str) -> dict:
        pass
    
    def _validate(self, data: str) -> str:
        if not data:
            raise ValueError("Empty data")
        return data.strip()
```

---

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Variables | `snake_case` | `user_age`, `total_count` |
| Functions | `snake_case` | `calculate_average()` |
| Classes | `PascalCase` | `InputParser`, `AgeCalculator` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private | `_prefix` | `_internal_method()`, `_cache` |
| Modules | `snake_case` | `input_parser.py` |
| Booleans | `is_/has_/can_/should_` | `is_valid`, `has_errors` |

---

## Error Handling

### Exception Hierarchy
```
AlgorithmError (base)
├── ValidationError       # Input validation failures
├── ParsingError         # Data parsing issues
├── CalculationError     # Business logic errors
└── FileOperationError   # I/O failures
```

### Pattern
```python
# ✅ DO: Specific exceptions, log, re-raise/wrap
def extract_data(self, text: str, source: str) -> list[int]:
    try:
        data = json.loads(text)
        return self._extract(data)
    except json.JSONDecodeError as e:
        self.logger.error(f"JSON parsing failed for {source}: {e}")
        raise ParsingError(f"Invalid JSON in {source}: {e}")
    except KeyError as e:
        raise ValidationError(f"Missing field {e} in {source}")

# ❌ DON'T: Bare except or swallow
def bad_example():
    try:
        risky_operation()
    except:  # Too broad
        pass  # Silently swallowed
```

---

## Ocean Protocol Patterns

### Pattern 1: Modern Algorithm with BaseAlgorithm
```python
from shared.infrastructure.base_algorithm import BaseAlgorithm
from shared.infrastructure.algorithm_dependencies import AlgorithmDependencies

class MyAlgorithm(BaseAlgorithm):
    """Custom algorithm inheriting common functionality."""
    
    def __init__(
        self,
        deps: AlgorithmDependencies,
        calculate_action: MyCalculateAction,
        config: AppConfig,
    ):
        super().__init__()
        self.config = config
        self.algorithm = deps.ocean_algorithm
        self.request = deps.request  # Set for base class validations
        self.response = deps.response
        self.calculate_action = calculate_action
        
        # Callbacks registered automatically
        self.register_callbacks(deps.ocean_algorithm)
    
    @classmethod
    def create(cls, config: AppConfig) -> "MyAlgorithm":
        """Composition root for this bounded context."""
        # Create common infrastructure dependencies
        deps = AlgorithmDependencies.create(MyRequestDTO)
        
        # Create bounded context specific dependencies
        mapper = MyMapper()
        repository = MyRepository(deps.request, mapper)
        action = MyCalculateAction(repository)
        
        return cls(deps, action, config)
    
    def validate_input(self, algo: Algorithm) -> None:
        # Performance monitoring starts automatically
        algo.logger.info("validate: starting")
        # Placeholder for business-specific validations
    
    def run(self, algo: Algorithm) -> MyResponseDTO:
        # Delegate to action (handles exceptions internally)
        algo.logger.info("run: starting")
        return self.calculate_action.execute()
    
    def save(self, algo: Algorithm, results: ResponseDTO, base_path: Path) -> None:
        # Use integrated response writer
        algo.logger.info("save: starting")
        output_file = base_path / self.config.output.filename
        self.response.write_results(results, output_file)
        # Performance monitoring stops automatically

# Usage
algorithm = MyAlgorithm.create(AppConfig.load()).algorithm
```

### Pattern 2: File Reader with Validation
```python
class FileReader:
    MAX_FILE_SIZE_MB = 100
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def read_text(self, path: Path) -> str:
        if not path.exists():
            raise FileOperationError(f"File not found: {path}")
        
        size_mb = path.stat().st_size / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            raise ValidationError(f"File too large: {size_mb:.2f}MB")
        
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            raise FileOperationError(f"Error reading {path}: {e}")
```

### Pattern 3: Input Parser Strategy
```python
class InputParser:
    def extract_data(self, text: str, source: str) -> list[DomainObject]:
        data = json.loads(text)
        
        if isinstance(data, list):
            return self._from_array(data)
        elif isinstance(data, dict) and 'data' in data:
            return self._from_object(data)
        else:
            raise ParsingError(f"Unsupported format in {source}")
```

### Pattern 4: Domain Validation
```python
class AgeInputParameters(InputParameters):
    ages: list[int]
    
    @field_validator('ages')
    @classmethod
    def validate_ages(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("Ages list cannot be empty")
        for age in v:
            if not (0 <= age <= 150):
                raise ValueError(f"Invalid age: {age}")
        return v
```

### Pattern 5: Service with Structured Logging
```python
class MyCalculator:
    def calculate(self, data: list[int]) -> Results:
        start = time.time()
        
        try:
            result = self._perform_calculation(data)
            
            self.logger.info(
                "Calculation completed",
                extra={
                    'item_count': len(data),
                    'execution_time_ms': (time.time() - start) * 1000,
                    'status': 'success'
                }
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Calculation failed: {e}",
                extra={'status': 'error', 'error_type': type(e).__name__}
            )
            raise
```

---

## Ocean Protocol Repository Pattern

### READ-ONLY Repositories

**CRITICAL**: Ocean Protocol repositories are **READ-ONLY**. They can only load data from Ocean Protocol input files, not modify it.

```python
# ✅ CORRECT: OceanInMemoryRepository for read-only access
from shared.infrastructure.repositories.ocean_in_memory_repository import OceanInMemoryRepository
from shared.domain.mapper_interface import MapperInterface

class UserAgeOceanRepository(OceanInMemoryRepository[UserAge, int]):
    """Read-only repository for UserAge entities from Ocean Protocol."""
    
    def __init__(self, request: Request, mapper: MapperInterface[UserAge]):
        super().__init__(request, mapper)
    
    # All functionality inherited:
    # - get_entities_from_input(AgeRequestDTO) - Loads data from Ocean inputs
    # - find_all() - Returns loaded entities
    # - clear() - Clears internal storage
    # - count() - Returns entity count

# Usage in Action
class CalculateAgeStatisticsAction:
    def __init__(self, repository: RepositoryInterface):
        self.repository = repository
    
    def execute(self) -> AgeResponseDTO:
        # Load data from Ocean Protocol inputs (READ-ONLY)
        self.repository.get_entities_from_input(AgeRequestDTO)
        
        # Query loaded data
        user_ages = self.repository.find_all()
        
        # Calculate statistics
        return self._calculate_stats(user_ages)

# ❌ WRONG: Attempting write operations
repository.save(entity)    # Raises NotImplementedError
repository.delete(id)      # Raises NotImplementedError
```

### Repository Hierarchy

```
RepositoryInterface[T, ID]  (Domain - Abstract interface)
         ↑
         |
    OceanRepository[T, ID]  (Infrastructure - READ-ONLY base)
         ↑                   - Provides Ocean Protocol access via Request
         |                   - save() and delete() raise NotImplementedError
         |
    OceanInMemoryRepository[T, ID]  (Infrastructure - In-memory storage)
         ↑                           - Stores entities in List[T]
         |                           - get_entities_from_input(dto_class)
         |                           - find_all(), clear(), count()
         |
    UserAgeOceanRepository  (Domain-specific implementation)
                            - Minimal code, inherits all functionality
                            - Specifies entity types (UserAge, int)
```

### Key Rules for Ocean Repositories

1. **READ-ONLY**: No `save()` or `delete()` operations allowed
2. **Mapper Required**: Must inject `MapperInterface[T]` for DTO-to-Entity conversion
3. **Generic Loading**: Use `get_entities_from_input(DTOClass)` to load data
4. **In-Memory Only**: Data stored temporarily in `List[T]` during execution
5. **Stateless**: Data cleared between algorithm runs

---

## Bounded Context Template

### Minimal structure for new feature (e.g., `price_analysis`):

```
algorithm/src/price_analysis/
├── domain/
│   ├── price_input_parameters.py   # extends InputParameters
│   ├── price_results.py            # extends Results
│   └── price_statistics.py         # Pydantic model
├── application/
│   ├── price_parser.py             # DI: logger
│   └── price_calculator.py         # DI: logger
└── infrastructure/
    └── csv_reader.py                # DI: logger

algorithm/tests/price_analysis/     # Mirror structure (NO __init__.py files)
```

### Domain Model Template
```python
# domain/price_statistics.py
from pydantic import BaseModel, Field

class PriceStatistics(BaseModel):
    """Value object for price statistics."""
    min_price: float = Field(ge=0.0)
    max_price: float = Field(ge=0.0)
    avg_price: float = Field(ge=0.0)
    
    @property
    def range(self) -> float:
        return self.max_price - self.min_price
```

### Service Template
```python
# application/price_calculator.py
from logging import Logger
from ..domain.price_statistics import PriceStatistics

class PriceCalculator:
    """Calculate price statistics."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def calculate(self, prices: list[float]) -> PriceStatistics:
        if not prices:
            raise CalculationError("Empty price list")
        
        stats = PriceStatistics(
            min_price=min(prices),
            max_price=max(prices),
            avg_price=round(sum(prices) / len(prices), 2)
        )
        
        self.logger.info(f"Calculated stats for {len(prices)} prices")
        return stats
```

### Infrastructure Template
```python
# infrastructure/csv_reader.py
from pathlib import Path
from logging import Logger

class CSVReader:
    """Read CSV files."""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def read_csv(self, path: Path) -> list[dict]:
        if not path.exists():
            raise FileOperationError(f"File not found: {path}")
        # ... implementation
```

---

## Testing Patterns

### Test Structure (mirror src/)
```python
# tests/price_analysis/application/test_price_calculator.py
import pytest
from price_analysis.application.price_calculator import PriceCalculator
from shared.domain.exceptions.calculation_error import CalculationError

class TestPriceCalculator:
    @pytest.fixture
    def calculator(self, mock_logger):
        return PriceCalculator(mock_logger)
    
    def test_calculate_with_valid_prices(self, calculator):
        # Arrange
        prices = [100.0, 200.0, 300.0]
        
        # Act
        stats = calculator.calculate(prices)
        
        # Assert
        assert stats.min_price == 100.0
        assert stats.max_price == 300.0
        assert stats.avg_price == 200.0
    
    def test_calculate_with_empty_list_raises_error(self, calculator):
        with pytest.raises(CalculationError):
            calculator.calculate([])
```

### Test Naming
Pattern: `test_<method>_<scenario>_<expected_result>`

Examples:
- `test_calculate_with_valid_data_returns_correct_stats`
- `test_parse_with_empty_input_raises_validation_error`
- `test_read_with_nonexistent_file_raises_file_error`

---

## Configuration Pattern

```python
# shared/domain/config/app_config.py
from pydantic import BaseModel, Field

class AlgorithmConfig(BaseModel):
    name: str
    version: str = "1.0.0"

class DataConfig(BaseModel):
    max_file_size_mb: int = Field(default=100, ge=1)

class AppConfig(BaseModel):
    algorithm: AlgorithmConfig
    data: DataConfig = Field(default_factory=DataConfig)
    
    @classmethod
    def load(cls) -> "AppConfig":
        """Load from YAML with env override."""
        path = cls._resolve_config_path()  # Check env → /config.yaml → ./config.yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
```

---

## Code Checklist

Before committing, verify:

- [ ] **Architecture**: Correct layer (domain/application/infrastructure)
- [ ] **SOLID**: Single responsibility, dependency injection used
- [ ] **Class order**: dunder → classmethod → staticmethod → property → public (α) → private (α)
- [ ] **Type hints**: All function signatures have types
- [ ] **Docstrings**: Google style on public classes/methods
- [ ] **Exceptions**: Specific exceptions, proper logging
- [ ] **Tests**: Written, passing, mirror src/ structure
- [ ] **Config**: No hardcoded values
- [ ] **Logging**: Used for debugging (injected logger)
- [ ] **Names**: Clear, intention-revealing (no abbreviations)
- [ ] **DRY**: No code duplication

---

## Common Mistakes - Quick Fix

| ❌ Mistake | ✅ Fix |
|-----------|--------|
| Business logic in infrastructure | Move to service layer |
| Service creating dependencies | Inject via `__init__` |
| Bare `except:` | Catch specific exceptions |
| Missing type hints | Add to all functions |
| Hardcoded values | Use configuration |
| Methods out of order | Follow class organization |
| God class (too many responsibilities) | Split into focused classes |
| No tests | Write tests mirroring src/ |
| Vague names (`calc`, `proc`) | Use descriptive names |
| Swallowed exceptions | Log and re-raise/wrap |

---

## Quick Commands

```bash
# Run tests
docker compose run --rm algorithm pytest -v

# Run with coverage
docker compose run --rm algorithm pytest --cov=algorithm --cov-report=term-missing

# Run algorithm
docker compose up --build

# View logs
cat _data/logs/algorithm.log
```

---

**For detailed explanations, examples, and tutorials, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

**Version**: 2.0  
**Last Updated**: February 2026  
**Document Size**: ~12KB (optimized for LLM consumption)
