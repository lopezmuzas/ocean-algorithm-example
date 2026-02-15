# AI Development Guidelines - Quick Reference

**Optimized for LLM consumption. For detailed explanations, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**

---

## Quick Reference

| Aspect | Rule |
|--------|------|
| **Architecture** | Hexagonal: Domain → Services → Infrastructure |
| **Class per file** | One class = One file |
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
│   ├── services/            # Use cases (depend on domain)
│   └── infrastructure/      # I/O, APIs (depend on domain + services)
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

### Pattern 1: Algorithm Integration
```python
class MyAlgorithm:
    def __init__(self):
        self.config = AppConfig.load()
        self.algorithm = Algorithm(config=Config(custom_input=MyInputParameters))
        self.performance = PerformanceMonitor(self.algorithm.logger)
        
        self.algorithm.validate(self.validate)
        self.algorithm.run(self.run)
        self.algorithm.save_results(self.save)
    
    def validate(self, algo: Algorithm) -> None:
        input_count = len(list(algo.job_details.inputs()))
        if input_count == 0:
            raise ValidationError("No input files")
    
    def run(self, algo: Algorithm) -> Results:
        # Initialize services (DI)
        reader = FileReader(algo.logger)
        parser = InputParser(algo.logger)
        calculator = MyCalculator(algo.logger)
        
        # Process inputs
        all_data = []
        for idx, path in algo.job_details.inputs():
            text = reader.read_text(path)
            data = parser.extract_data(text, path.name)
            all_data.extend(data)
        
        return calculator.calculate(all_data)
    
    def save(self, algo: Algorithm, results: Results, base_path: Path) -> None:
        writer = ResultWriter(algo.logger, self.config.output)
        writer.write(results, base_path / "outputs")
        self.performance.log_metrics()

algorithm = MyAlgorithm()
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

## Bounded Context Template

### Minimal structure for new feature (e.g., `price_analysis`):

```
algorithm/src/price_analysis/
├── domain/
│   ├── __init__.py
│   ├── price_input_parameters.py   # extends InputParameters
│   ├── price_results.py            # extends Results
│   └── price_statistics.py         # Pydantic model
├── services/
│   ├── __init__.py
│   ├── price_parser.py             # DI: logger
│   └── price_calculator.py         # DI: logger
└── infrastructure/
    ├── __init__.py
    └── csv_reader.py                # DI: logger

algorithm/tests/price_analysis/     # Mirror structure
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
# services/price_calculator.py
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
# tests/price_analysis/services/test_price_calculator.py
import pytest
from price_analysis.services.price_calculator import PriceCalculator
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

- [ ] **Architecture**: Correct layer (domain/services/infrastructure)
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
