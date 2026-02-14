# Algorithm implementation based on the OceanProtocol ecosystem

Build and push

```bash
$ docker buildx build --platform linux/amd64,linux/arm64 -t {ALGORITHM_TAG}:{ALGORITHM_VERSION} . --push 
```

## CI/CD

Este proyecto incluye un pipeline básico de GitHub Actions que ejecuta:
- Tests automatizados con pytest
- Construcción de imagen Docker multi-plataforma

Los workflows están definidos en `.github/workflows/ci.yml`.

## Configuración

Los parámetros del algoritmo se pueden configurar en `config.yaml`:
- Parámetros de datos (formatos soportados, límites de archivo)
- Configuración de estadísticas (decimales, incluir conteo)
- Logging (nivel, formato)
- Rendimiento (tamaño de batch, timeouts)

## Cómo crear un nuevo algoritmo

Para crear un nuevo algoritmo basado en esta arquitectura hexagonal, sigue estos pasos:

### 1. Crear un nuevo contexto delimitado (Bounded Context)

Crea una nueva carpeta bajo `algorithm/src/` con el nombre de tu algoritmo, por ejemplo `price_analysis`:

```
algorithm/src/price_analysis/
├── domain/
├── services/
└── infrastructure/
```

### 2. Implementar la capa de dominio

- **Parámetros de entrada**: Crea una clase que herede de `shared.domain.input_parameters.InputParameters`
- **Resultados**: Crea una clase que herede de `shared.domain.results.Results`
- **Objetos de valor**: Define las entidades y objetos de valor específicos de tu dominio

Ejemplo:
```python
# algorithm/src/price_analysis/domain/price_input_parameters.py
from shared.domain.input_parameters import InputParameters

class PriceInputParameters(InputParameters):
    prices: list[float]
```

### 3. Implementar servicios de aplicación

Crea servicios que contengan la lógica de negocio, dependientes solo del dominio:

```python
# algorithm/src/price_analysis/services/price_calculator.py
from price_analysis.domain.price_input_parameters import PriceInputParameters
from price_analysis.domain.price_results import PriceResults

class PriceCalculator:
    def calculate_average_price(self, params: PriceInputParameters) -> PriceResults:
        # Lógica de negocio aquí
        pass
```

### 4. Implementar adaptadores de infraestructura

Crea adaptadores para entrada/salida de datos:

```python
# algorithm/src/price_analysis/infrastructure/price_reader.py
from price_analysis.domain.price_input_parameters import PriceInputParameters

class PriceReader:
    def read_from_file(self, file_path: str) -> PriceInputParameters:
        # Leer datos del archivo
        pass
```

### 5. Actualizar el archivo principal `algorithm.py`

Modifica `algorithm/src/algorithm.py` para usar tu nuevo contexto:

```python
from price_analysis.services.price_calculator import PriceCalculator
from price_analysis.infrastructure.price_reader import PriceReader
from price_analysis.infrastructure.price_writer import PriceWriter

# Instanciar servicios
calculator = PriceCalculator()
reader = PriceReader()
writer = PriceWriter()

@algorithm.validate
def validate_price(params: PriceInputParameters, algorithm: Algorithm) -> bool:
    # Validación específica
    pass

@algorithm.run
def run_price(params: PriceInputParameters, algorithm: Algorithm) -> PriceResults:
    # Ejecutar cálculo
    pass

@algorithm.save_results
def save_price_results(results: PriceResults, algorithm: Algorithm) -> None:
    # Guardar resultados
    pass
```

### 6. Crear tests

Crea tests que reflejen la estructura del código fuente en `algorithm/tests/price_analysis/`.

### 7. Actualizar configuración

Si es necesario, añade parámetros específicos en el archivo de configuración `config.yaml`.

_Algorithm details_