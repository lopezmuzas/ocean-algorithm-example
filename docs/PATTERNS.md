# Patrones Comunes de Ocean Protocol

Este documento describe los patrones comunes y mejores prácticas para desarrollar algoritmos que se ejecuten en el entorno Compute-to-Data de Ocean Protocol.

## Arquitectura General

### Patrón Hexagonal (Ports & Adapters)
```
Domain (Core Business Logic)
    ↓
Services (Application Logic)
    ↓
Infrastructure (External Adapters)
```

- **Domain**: Lógica de negocio pura, sin dependencias externas
- **Services**: Casos de uso que coordinan domain objects
- **Infrastructure**: Adaptadores para I/O (archivos, APIs, bases de datos)

## Patrones Específicos de Ocean Protocol

### 1. Manejo de Entradas (Input Handling)

#### Patrón: Input Parser Strategy
```python
class InputParser:
    def extract_data(self, text: str, source_name: str) -> List[DomainObject]:
        # Soporta múltiples formatos
        if self._is_json_array(text):
            return self._parse_json_array(text)
        elif self._is_json_object(text):
            return self._parse_json_object(text)
        else:
            raise ParsingError(f"Unsupported format in {source_name}")
```

#### Patrón: File Reader con Validación
```python
class FileReader:
    def read_text(self, path: Path) -> str:
        if not path.exists():
            raise FileOperationError(f"File not found: {path}")
        if path.stat().st_size > MAX_FILE_SIZE:
            raise ValidationError(f"File too large: {path}")
        return path.read_text(encoding='utf-8')
```

### 2. Validación de Datos

#### Patrón: Domain Validation
```python
class AgeInputParameters(InputParameters):
    ages: List[int]

    @field_validator('ages')
    @classmethod
    def validate_ages(cls, v):
        for age in v:
            if not (0 <= age <= 150):
                raise ValueError(f'Invalid age: {age}')
        return v
```

#### Patrón: Business Rule Validation
```python
class AgeStatisticsCalculator:
    def calculate(self, ages: List[int]) -> AgeStatistics:
        if not ages:
            raise ValidationError("Cannot calculate statistics for empty dataset")
        # ... cálculo
```

### 3. Manejo de Errores

#### Patrón: Exception Hierarchy
```
AlgorithmError (base)
├── ValidationError
├── ParsingError
├── CalculationError
└── FileOperationError
```

#### Patrón: Error Recovery
```python
try:
    result = self._process_data(data)
except ValidationError:
    # Log and return error result
    return ErrorResult(message="Invalid input data")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}")
    raise
```

### 4. Configuración

#### Patrón: Configuration Loading with Environment Override
```python
@dataclass
class Config:
    algorithm_name: str
    max_file_size: int
    log_level: str

    @classmethod
    def from_yaml_and_env(cls, yaml_path: Path) -> 'Config':
        # Load YAML
        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Override with environment variables
        data['algorithm_name'] = os.getenv('ALGORITHM_NAME', data.get('algorithm_name'))
        data['max_file_size'] = int(os.getenv('MAX_FILE_SIZE', data.get('max_file_size', 100)))

        return cls(**data)
```

### 5. Logging y Monitoreo

#### Patrón: Structured Logging
```python
logger.info(
    "Processing completed",
    extra={
        'input_files': len(inputs),
        'processing_time': time.time() - start_time,
        'memory_usage': psutil.Process().memory_info().rss
    }
)
```

#### Patrón: Performance Metrics
```python
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.memory_start = psutil.Process().memory_info().rss

    def get_metrics(self) -> Dict[str, float]:
        return {
            'execution_time': time.time() - self.start_time,
            'memory_usage_mb': (psutil.Process().memory_info().rss - self.memory_start) / 1024 / 1024
        }
```

### 6. Testing

#### Patrón: Test Pyramid
```
Unit Tests (51 tests) - Domain + Services
Integration Tests - Full algorithm execution
E2E Tests - Docker container execution
```

#### Patrón: Test Fixtures
```python
@pytest.fixture
def sample_input_data():
    return [
        {"user_id": 1, "age": 25},
        {"user_id": 2, "age": 30}
    ]

@pytest.fixture
def mock_logger():
    return logging.getLogger('test')
```

### 7. Ocean Runner Integration

#### Patrón: Algorithm Lifecycle
```python
@algorithm.validate
def validate(algo: Algorithm) -> None:
    # Pre-flight checks
    pass

@algorithm.run
def run(algo: Algorithm) -> Results:
    # Main processing
    pass

@algorithm.save_results
def save_results(algo: Algorithm, results: Results, base_path: Path) -> None:
    # Output generation
    pass
```

#### Patrón: Input Processing
```python
def process_inputs(algo: Algorithm) -> List[ProcessedData]:
    results = []
    for idx, path in algo.job_details.inputs():
        algo.logger.info(f"Processing input {idx}: {path.name}")
        data = self.file_reader.read_text(path)
        processed = self.input_parser.extract_data(data, path.name)
        results.extend(processed)
    return results
```

## Mejores Prácticas

### 1. Diseño
- Mantén la lógica de dominio pura (sin side effects)
- Usa inyección de dependencias
- Implementa interfaces para facilitar testing

### 2. Rendimiento
- Procesa datos en lotes para grandes volúmenes
- Implementa timeouts para operaciones
- Monitorea uso de recursos

### 3. Seguridad
- Valida tamaños de archivos
- Sanitiza inputs
- Evita ejecución de código arbitrario

### 4. Mantenibilidad
- Una clase por archivo
- Documentación completa
- Tests automatizados

### 5. Escalabilidad
- Diseño modular para agregar nuevos algoritmos
- Configuración externa
- Logging estructurado

## Casos de Uso Comunes

### Algoritmo de Estadísticas
- Validación de rangos
- Cálculo de métricas básicas
- Formato de salida JSON

### Algoritmo de Machine Learning
- Preprocesamiento de datos
- Entrenamiento de modelo
- Predicciones

### Algoritmo de Análisis de Datos
- Parsing de múltiples formatos
- Agregaciones complejas
- Visualizaciones

## Referencias

- [Ocean Protocol Documentation](https://docs.oceanprotocol.com/)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)