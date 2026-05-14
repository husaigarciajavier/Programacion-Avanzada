"""
Utilidades para manejo de tiempos y duraciones
"""

from datetime import datetime, timedelta
from src.config.constants import FORMATO_FECHA_HORA

class TiempoUtils:
    """Clase con funciones auxiliares para manejo de tiempo"""
    
    @staticmethod
    def obtener_tiempo_actual():
        """Retorna la fecha y hora actual en formato string"""
        return datetime.now().strftime(FORMATO_FECHA_HORA)
    
    @staticmethod
    def obtener_fecha_actual():
        """Retorna la fecha actual en formato string"""
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def calcular_duracion(fecha_ingreso, fecha_salida=None):
        """
        Calcula la duración entre dos fechas.
        
        Args:
            fecha_ingreso: String con fecha de ingreso
            fecha_salida: String con fecha de salida (opcional, usa actual si None)
        
        Returns:
            float: Duración en horas (con 2 decimales)
        """
        ingreso = datetime.strptime(fecha_ingreso, FORMATO_FECHA_HORA)
        
        if fecha_salida:
            salida = datetime.strptime(fecha_salida, FORMATO_FECHA_HORA)
        else:
            salida = datetime.now()
        
        diferencia = salida - ingreso
        horas = diferencia.total_seconds() / 3600
        
        # Redondear a 2 decimales
        return round(horas, 2)
    
    @staticmethod
    def formatear_duracion(horas):
        """
        Convierte horas a formato legible (horas y minutos)
        
        Args:
            horas: float (ej: 2.75)
        
        Returns:
            string: "2 horas, 45 minutos"
        """
        horas_enteras = int(horas)
        minutos = int((horas - horas_enteras) * 60)
        
        if horas_enteras == 0:
            return f"{minutos} minutos"
        elif minutos == 0:
            return f"{horas_enteras} horas"
        else:
            return f"{horas_enteras} horas, {minutos} minutos"
    
    @staticmethod
    def calcular_total_a_pagar(horas, precio_por_hora):
        """
        Calcula el monto total a pagar
        
        Args:
            horas: float (horas de estadía)
            precio_por_hora: float (precio por hora)
        
        Returns:
            float: Monto total (redondeado a 2 decimales)
        """
        # Si la estadía es menor a 1 hora, se cobra como 1 hora (mínimo)
        if horas < 1 and horas > 0:
            horas = 1
        
        total = horas * precio_por_hora
        return round(total, 2)