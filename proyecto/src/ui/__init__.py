"""
Módulo de interfaz de usuario del proyecto Estacionamiento
"""

from src.ui.ventana_principal import VentanaPrincipal
from src.ui.registro_vehiculo import VentanaRegistroVehiculo
from src.ui.pago_vehiculo import VentanaPagoVehiculo
from src.ui.reportes import VentanaReportes
from src.ui.configuracion import VentanaConfiguracion

__all__ = [
    'VentanaPrincipal',
    'VentanaRegistroVehiculo',
    'VentanaPagoVehiculo',
    'VentanaReportes',
    'VentanaConfiguracion'
]