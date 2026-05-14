"""
Módulo de modelos del proyecto Estacionamiento
"""

from src.models.vehiculo import Vehiculo
from src.models.estacionamiento import Estacionamiento
from src.models.registro import RegistroMovimientos

__all__ = [
    'Vehiculo',
    'Estacionamiento',
    'RegistroMovimientos'
]