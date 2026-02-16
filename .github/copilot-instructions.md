# Instrucciones de IA

**IMPORTANTE**: Este archivo contiene un resumen de las reglas críticas. Para el contenido completo y actualizado, consulta **@docs/AI_GUIDELINES.md**.

## Reglas Arquitectónicas Críticas

### Arquitectura Hexagonal (OBLIGATORIA)
```
Domain Layer (Core Business Logic) → Application Layer (Use Cases) → Infrastructure Layer (External Adapters)
```

### Reglas Estrictas (NO NEGOCIABLES)
- **❌ NO crear archivos `__init__.py`**
- **Una clase = Un archivo**
- **Inyección de dependencias estricta**: Todas las dependencias deben ser inyectadas explícitamente a través del constructor o métodos de clase. No se permiten instanciaciones directas dentro de métodos.
- **Type hints obligatorios** en todas las funciones
- **Docstrings Google style** en clases/métodos públicos

### Patrón de Algoritmo Moderno
```python
class MyAlgorithm(BaseAlgorithm):
    def __init__(self, config: AppConfig, request: Request, calculate_action: MyAction):
        super().__init__()
        self.config = config
        self.request = request
        self.calculate_action = calculate_action
        
    @classmethod
    def create(cls, config: AppConfig) -> "MyAlgorithm":
        # Crear todas las dependencias con inyección estricta
        
    def validate_input(self, algo: Algorithm) -> None:
        # Validaciones genéricas automáticas en BaseAlgorithm
        
    def run(self, algo: Algorithm) -> Results:
        # Delegar a action (maneja excepciones internamente)
        return self.calculate_action.execute()
```

### Manejo de Excepciones
- **Actions manejan excepciones internamente** y retornan `Results` con status "error"
- **Excepciones específicas**: `ValidationError`, `ParsingError`, `CalculationError`, `FileOperationError`

### Repositorios Ocean (READ-ONLY)
- **❌ NO usar `save()` o `delete()`** en repositorios Ocean (lanzan `NotImplementedError`)
- **✅ Usar `get_entities_from_input(DTOClass)`** para cargar datos de Ocean Protocol
- **Mapper obligatorio**: Inyectar `MapperInterface[T]` en constructor
- **Herencia**: `OceanInMemoryRepository[Entity, ID]` para almacenamiento temporal
- **Consulta**: Usar `find_all()`, `clear()`, `count()` para datos cargados

---

**Para reglas completas, ejemplos detallados y mejores prácticas: @docs/AI_GUIDELINES.md**