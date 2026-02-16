"""
Shared infrastructure dependencies for Ocean Protocol algorithms.
"""

from dataclasses import dataclass
from typing import Type
from ocean_runner import Algorithm, Config

from shared.domain.request_dto import RequestDTO
from shared.infrastructure.file_reader import FileReader
from shared.infrastructure.request import Request
from shared.infrastructure.response import Response
from shared.infrastructure.response_writer import ResponseWriter


@dataclass
class AlgorithmDependencies:
    """Agrupa dependencias comunes del algoritmo."""
    ocean_algorithm: Algorithm
    request: Request
    response: Response
    
    @classmethod
    def create(cls, request_dto_class: Type[RequestDTO]) -> "AlgorithmDependencies":
        """
        Factory method para crear todas las dependencias comunes.
        
        Args:
            request_dto_class: Clase DTO para validación de inputs
            
        Returns:
            AlgorithmDependencies con todas las dependencias inicializadas
        """
        ocean_algorithm = Algorithm(config=Config(custom_input=request_dto_class))
        file_reader = FileReader(ocean_algorithm.logger)
        result_writer = ResponseWriter(ocean_algorithm.logger)
        request = Request(ocean_algorithm, file_reader)
        response = Response(result_writer)
        
        return cls(
            ocean_algorithm=ocean_algorithm,
            request=request,
            response=response,
        )
