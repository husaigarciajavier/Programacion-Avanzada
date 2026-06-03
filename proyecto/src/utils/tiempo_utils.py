"""
Utilidades para manejo de tiempos y duraciones
"""

import math
from datetime import datetime
from src.config.constants import FORMATO_FECHA_HORA


class TiempoUtils:
    """Clase con funciones auxiliares para manejo de tiempo"""
    
    @staticmethod
    def obtener_tiempo_actual():
        return datetime.now().strftime(FORMATO_FECHA_HORA)
    
    @staticmethod
    def obtener_fecha_actual():
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def obtener_hora_actual():
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def calcular_duracion(fecha_ingreso, fecha_salida=None):
        """
        Calcula la duración entre dos fechas en horas.
        
        Args:
            fecha_ingreso: str con formato "YYYY-MM-DD HH:MM:SS"
            fecha_salida: str opcional (usa actual si None)
        
        Returns:
            float: Horas con 2 decimales
        """
        ingreso = datetime.strptime(fecha_ingreso, FORMATO_FECHA_HORA)
        salida = datetime.strptime(fecha_salida, FORMATO_FECHA_HORA) if fecha_salida else datetime.now()
        
        diferencia = salida - ingreso
        horas = diferencia.total_seconds() / 3600
        
        return round(horas, 2)
    
    @staticmethod
    def formatear_duracion(horas):
        """
        Convierte horas a formato legible.
        
        Args:
            horas: float (ej: 2.75)
        
        Returns:
            str: "2 horas, 45 minutos" o "45 minutos" o "0 minutos"
        """
        if horas <= 0:
            return "0 minutos"
        
        horas_enteras = int(horas)
        minutos = int((horas - horas_enteras) * 60)
        
        if horas_enteras == 0:
            return f"{minutos} minutos"
        elif minutos == 0:
            return f"{horas_enteras} horas"
        else:
            return f"{horas_enteras} horas, {minutos} minutos"
    
    @staticmethod
    def calcular_horas_a_cobrar(horas):
        """
        Calcula las horas a cobrar redondeando hacia arriba.
        
        Args:
            horas: float (horas reales de estadía)
        
        Returns:
            int: Horas a cobrar (siempre redondeado hacia arriba, mínimo 1)
        
        Ejemplos:
            - 0.5 horas (30 min) -> 1 hora
            - 1.05 horas (1h 3min) -> 2 horas
            - 1.75 horas (1h 45min) -> 2 horas
            - 4.92 horas (4h 55min) -> 5 horas
        """
        if horas <= 0:
            return 0
        
        # Redondear hacia arriba usando math.ceil
        horas_a_cobrar = math.ceil(horas)
        
        # Mínimo 1 hora
        if horas_a_cobrar < 1:
            horas_a_cobrar = 1
        
        return horas_a_cobrar
    
    @staticmethod
    def calcular_total_a_pagar(horas, precio_por_hora):
        """
        Calcula el monto total a pagar REDONDEANDO HACIA ARRIBA.
        
        Args:
            horas: float (horas reales de estadía)
            precio_por_hora: float (precio por hora)
        
        Returns:
            float: Monto total redondeado a 2 decimales
        
        Ejemplos (precio $5/hora):
            - 30 minutos (0.5h) -> 1 hora -> $5.00
            - 1h 3min (1.05h) -> 2 horas -> $10.00
            - 1h 45min (1.75h) -> 2 horas -> $10.00
            - 4h 55min (4.92h) -> 5 horas -> $25.00
        """
        horas_a_cobrar = TiempoUtils.calcular_horas_a_cobrar(horas)
        total = horas_a_cobrar * precio_por_hora
        return round(total, 2)