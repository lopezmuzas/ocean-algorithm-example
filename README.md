# Ocean Protocol Algorithm Template

[![CI](https://github.com/oceanprotocol/ocean-algorithm-example/workflows/CI/badge.svg)](https://github.com/oceanprotocol/ocean-algorithm-example/actions)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

A production-ready template for building Ocean Protocol algorithms using **Hexagonal Architecture** and **SOLID principles**. Features comprehensive testing, Docker containerization, and clean code practices.

## ✨ Features

- 🏗️ **Hexagonal Architecture**: Clean separation of concerns with domain-driven design
- 🧪 **Comprehensive Testing**: 51+ tests with 80%+ coverage
- 🐳 **Docker Ready**: Multi-platform containerization with optimized builds
- 📊 **Performance Monitoring**: Built-in metrics and structured logging
- 🔧 **Configuration Management**: Pydantic-based config with environment overrides
- 📚 **Developer Friendly**: Extensive documentation and development guides
- 🚀 **CI/CD Ready**: GitHub Actions pipeline for automated testing and deployment

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (optional, for local development)

### Run the Example Algorithm

```bash
# Clone repository
git clone https://github.com/oceanprotocol/ocean-algorithm-example.git
cd ocean-algorithm-example

# Run algorithm with sample data
docker compose up --build

# View results
cat _data/outputs/age_statistics_output.json
```

### Run Tests

```bash
# Using Docker (recommended)
docker compose run --rm algorithm pytest -v

# With coverage report
docker compose run --rm algorithm pytest --cov=algorithm --cov-report=term-missing
```

## 📖 Documentation

### For Developers
- **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Comprehensive guide with tutorials, examples, and best practices
- **[AI_GUIDELINES.md](docs/AI_GUIDELINES.md)** - Quick reference optimized for AI assistants

### Key Topics
- 🏛️ **Architecture Overview**: Hexagonal architecture implementation
- 🎯 **SOLID Principles**: Applied design patterns
- 📝 **Code Standards**: Naming conventions, class organization, testing
- 🔄 **Bounded Contexts**: Creating new algorithms step-by-step
- 🐳 **Docker Integration**: Containerization and deployment
- ⚙️ **Configuration**: Environment and YAML-based config management

## 🏗️ Architecture

This template implements **Hexagonal Architecture** (Ports & Adapters) ensuring:

```
Domain Layer (Core Business Logic)
    ↓
Application Layer (Use Cases)
    ↓
Infrastructure Layer (External Adapters)
```

### Current Implementation
- **Age Statistics Algorithm**: Calculates min/max/average from age datasets
- **51 Tests**: Comprehensive test coverage across all layers
- **Performance Monitoring**: Execution time, memory usage, CPU metrics
- **Error Handling**: Hierarchical exception system with specific error types

### Project Structure

```
├── algorithm/                    # Algorithm implementation
│   ├── config.yaml              # Configuration file
│   ├── pyproject.toml           # Python dependencies
│   ├── src/                     # Source code
│   │   ├── age_average/         # Current bounded context
│   │   │   ├── domain/          # Business entities & validation
│   │   │   ├── application/     # Application logic
│   │   │   └── infrastructure/  # External adapters
│   │   └── shared/              # Cross-cutting concerns
│   │       ├── domain/          # Shared models & exceptions
│   │       └── infrastructure/  # Shared utilities
│   └── tests/                   # Test suite (mirrors src/)
├── docs/                        # Documentation
├── _data/                       # Data directories
│   ├── inputs/                  # Sample input data
│   ├── outputs/                 # Generated results
│   └── logs/                    # Application logs
├── docker-compose.yaml          # Local development
├── Dockerfile                   # Container definition
└── .env.example                 # Environment template
```

## 🛠️ Development

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
# ALGORITHM_NAME=age_average
# LOG_LEVEL=INFO
# MAX_FILE_SIZE_MB=100
```

### Local Development

```bash
# Install dependencies (requires Python 3.12+)
cd algorithm/
pip install -e ".[dev]"

# Run tests locally
pytest -v

# Run algorithm locally
python -m src.algorithm
```

### Docker Development

```bash
# Build and run
docker compose up --build

# Run tests in container
docker compose run --rm algorithm pytest

# Interactive development
docker compose run --rm algorithm bash
```

## 🔧 Configuration

### Configuration Sources (Priority Order)
1. **Environment Variables** (highest priority)
2. **YAML Config File** (`algorithm/config.yaml`)
3. **Default Values** (fallback)

### Key Configuration Areas

```yaml
# algorithm/config.yaml
algorithm:
  name: "age_average"
  version: "1.0.0"

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

## 🧪 Testing Strategy

### Test Organization
Tests mirror source structure with comprehensive coverage:

- **Unit Tests**: Domain models, services, infrastructure
- **Integration Tests**: End-to-end algorithm execution
- **Configuration Tests**: Validation and loading
- **Performance Tests**: Resource usage monitoring

### Test Coverage
- **51 tests** currently passing
- **80%+ coverage** target
- **CI/CD integration** with automated testing

## 🚀 Creating New Algorithms

This template makes it easy to add new algorithms. See **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** for the complete step-by-step tutorial.

### Quick Example: Price Analysis Algorithm

1. **Create bounded context structure**:
   ```bash
   mkdir -p algorithm/src/price_analysis/{domain,services,infrastructure}
   ```

2. **Implement domain models**:
   ```python
   # algorithm/src/price_analysis/domain/price_statistics.py
   from pydantic import BaseModel, Field

   class PriceStatistics(BaseModel):
       min_price: float = Field(ge=0.0)
       max_price: float = Field(ge=0.0)
       avg_price: float = Field(ge=0.0)
   ```

3. **Create application service**:
   ```python
   # algorithm/src/price_analysis/application/price_calculator.py
   class PriceCalculator:
       def __init__(self, logger: Logger):
           self.logger = logger

       def calculate(self, prices: list[float]) -> PriceStatistics:
           return PriceStatistics(
               min_price=min(prices),
               max_price=max(prices),
               avg_price=sum(prices) / len(prices)
           )
   ```

4. **Add infrastructure adapter**:
   ```python
   # algorithm/src/price_analysis/infrastructure/csv_reader.py
   class CSVReader:
       def read_csv(self, path: Path) -> list[dict]:
           # CSV reading logic
           pass
   ```

5. **Update main algorithm** and **add tests**!

See **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** for complete implementation details.

## 📊 Performance & Monitoring

### Built-in Metrics
- **Execution Time**: Algorithm runtime tracking
- **Memory Usage**: Current and peak memory consumption
- **CPU Utilization**: Processor usage percentage
- **Structured Logging**: JSON-formatted logs with context

### Example Output
```
Algorithm execution completed: execution_time=0.107s, memory_usage=0.01MB, peak_memory=39.84MB, cpu_percent=0.00%
```

## 🔒 Security & Best Practices

- **Input Validation**: Comprehensive data validation using Pydantic
- **Error Handling**: Specific exceptions with proper logging
- **Resource Limits**: File size and processing time constraints
- **Dependency Injection**: No hardcoded dependencies
- **Type Safety**: Full type hints throughout codebase

## 🤝 Contributing

We welcome contributions! Please see our development guidelines:

1. 📖 Read **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** for architecture and coding standards
2. 🧪 Write tests for new functionality
3. 📝 Update documentation as needed
4. ✅ Ensure all tests pass before submitting PR
5. 🎯 Follow the established patterns and conventions

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-algorithm`)
3. Make changes following the guidelines
4. Run tests (`docker compose run --rm algorithm pytest`)
5. Submit pull request

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](algorithm/LICENSE) file for details.

## 🙏 Acknowledgments

- Ocean Protocol Community for the ecosystem
- Hexagonal Architecture and Domain-Driven Design principles
- SOLID design pattern community
- Open source testing and development tools

---

**For detailed documentation, tutorials, and examples, see [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)**

**Built with ❤️ for the Ocean Protocol ecosystem**