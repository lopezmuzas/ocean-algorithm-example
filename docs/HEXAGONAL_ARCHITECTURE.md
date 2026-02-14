# Hexagonal Architecture

This project follows **Hexagonal Architecture** (also known as Ports and Adapters) with a clear separation between generic shared components and specific business functionalities.

## Structure Overview

```
algorithm/src/
├── shared/                          # Generic, reusable components
│   ├── domain/                      # Base domain models
│   │   ├── input_parameters.py      # Base InputParameters model
│   │   ├── results.py               # Base Results model
│   │   ├── exceptions.py            # Imports all exception classes
│   │   └── exceptions/              # Exception classes directory
│   │       ├── __init__.py          # Exception package
│   │       ├── algorithm_error.py   # AlgorithmError base class
│   │       ├── validation_error.py  # ValidationError class
│   │       ├── parsing_error.py     # ParsingError class
│   │       ├── calculation_error.py # CalculationError class
│   │       └── file_operation_error.py # FileOperationError class
│   ├── services/                    # Generic services (currently empty)
│   └── infrastructure/              # Generic infrastructure (currently empty)
│
├── age_average/                     # Age statistics bounded context
│   ├── domain/                      # Core business logic (entities & value objects)
│   │   ├── age_input_parameters.py  # AgeInputParameters (extends base)
│   │   ├── age_results.py           # AgeResults (extends base)
│   │   └── age_statistics.py        # AgeStatistics value object
│   │
│   ├── services/                    # Application services (use cases)
│   │   ├── input_parser.py          # Parse input data
│   │   └── age_statistics_calculator.py  # Calculate age statistics
│   │
│   └── infrastructure/              # External adapters (file I/O, etc.)
│       ├── file_reader.py           # Read files from disk
│       └── result_writer.py         # Write results to disk
│
└── algorithm.py                     # Orchestration layer (Ocean Runner)
```

## Architecture Principles

### 1. **Shared Module**
Contains generic base classes and infrastructure that can be reused across different bounded contexts:
- **Domain**: `InputParameters` (base class for all algorithm inputs), `Results` (base class for all algorithm results)
- **Services**: Generic application services (currently empty, ready for shared business logic)
- **Infrastructure**: Generic adapters and infrastructure components (currently empty, ready for shared I/O operations)

These are domain-agnostic and define the contract for Ocean Protocol algorithms.

### 2. **Age Average Module** (Bounded Context)
A complete implementation of age statistics functionality following hexagonal architecture:

#### Domain Layer (Core)
- **Pure business logic**, no dependencies on infrastructure
- Contains entities, value objects, and domain models
- `AgeInputParameters`, `AgeResults`, `AgeStatistics`

#### Services Layer (Use Cases)
- **Application logic** that orchestrates domain models
- `InputParser`: Transforms external data into domain objects
- `AgeStatisticsCalculator`: Implements age calculation business rules

#### Infrastructure Layer (Adapters)
- **External concerns** like file I/O, databases, APIs
- `FileReader`: Adapter for reading files
- `ResultWriter`: Adapter for writing results
- Can be easily swapped with different implementations

### 3. **Dependency Direction**
```
Infrastructure → Services → Domain
         ↓          ↓          ↓
      Shared Domain (base classes)
```

- **Domain** has no dependencies (pure business logic)
- **Services** depend only on Domain
- **Infrastructure** depends on Domain and Services
- **All layers** can use Shared components

## Benefits

1. **Reusability**: Shared module can be used by multiple bounded contexts
2. **Testability**: Each layer can be tested independently (51 tests passing)
3. **Maintainability**: One class per file, clear responsibilities
4. **Extensibility**: Easy to add new bounded contexts (e.g., `price_analysis`, `user_segmentation`)
5. **Independence**: Business logic (domain) is isolated from technical concerns
6. **Clean Structure**: No duplicate code, all old directories removed

## Adding a New Bounded Context

To add a new feature (e.g., `price_analysis`):

```
algorithm/src/
├── shared/                    # Reuse existing base classes
├── age_average/              # Existing feature
└── price_analysis/           # New bounded context
    ├── domain/
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
├── shared/domain/              # Tests for base classes
├── age_average/               # Tests for age_average module
│   ├── domain/
│   ├── services/
│   └── infrastructure/
└── test_algorithm.py          # Integration tests
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

## Mejoras Implementadas

### ✅ Manejo de Errores
- **Excepciones específicas**: Se han implementado excepciones personalizadas en un subdirectorio dedicado `shared/domain/exceptions/`:
  - `algorithm_error.py`: `AlgorithmError` (clase base)
  - `validation_error.py`: `ValidationError` (errores de validación)
  - `parsing_error.py`: `ParsingError` (errores de parsing)
  - `calculation_error.py`: `CalculationError` (errores de cálculo)
  - `file_operation_error.py`: `FileOperationError` (errores de archivo)
  - `__init__.py`: Paquete de excepciones que exporta todas las clases
  - `exceptions.py`: Archivo de conveniencia que importa todas las excepciones

- **Manejo robusto**: Los servicios ahora lanzan excepciones específicas en lugar de retornar valores por defecto
- **Propagación de errores**: El `algorithm.py` captura y maneja apropiadamente las excepciones, retornando resultados de error informativos

### ✅ CI/CD Pipeline
- **GitHub Actions**: Pipeline básico en `.github/workflows/ci.yml`
- **Tests automatizados**: Ejecuta todos los tests con pytest
- **Construcción Docker**: Construye la imagen multi-plataforma (linux/amd64, linux/arm64)

### ✅ Archivo de Configuración
- **config.yaml**: Archivo centralizado para parámetros del algoritmo
- **Categorías de configuración**:
  - `algorithm`: Metadatos del algoritmo
  - `data`: Configuración de procesamiento de datos
  - `statistics`: Parámetros de cálculo estadístico
  - `logging`: Configuración de logging
  - `output`: Formato de salida
  - `performance`: Ajustes de rendimiento

### ✅ Mejoras en Documentación
- **README.md actualizado**: Incluye secciones de CI/CD, configuración y guía para crear nuevos algoritmos
- **README en español**: Documentación completa en español para facilitar el uso

## Beneficios de las Mejoras

1. **Robustez**: El manejo de errores específico mejora la fiabilidad y debugging
2. **Automatización**: CI/CD asegura calidad de código en cada commit
3. **Flexibilidad**: Configuración externa permite adaptar el algoritmo sin modificar código
4. **Mantenibilidad**: Documentación clara facilita la extensión y mantenimiento
