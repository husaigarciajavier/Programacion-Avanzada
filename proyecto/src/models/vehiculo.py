"""
Clase Vehículo - Representa un vehículo en el estacionamiento
"""

from datetime import datetime
from src.utils.id_generator import GeneradorID
from src.utils.tiempo_utils import TiempoUtils
from src.config.constants import FORMATO_FECHA_HORA

class Vehiculo:
    """Clase que representa un vehículo estacionado"""
    
    def __init__(self, placa, id_unico=None, hora_ingreso=None):
        """
        Inicializa un nuevo vehículo
        
        Args:
            placa: str (placa del vehículo)
            id_unico: str (opcional, si no se proporciona se genera automático)
            hora_ingreso: str (opcional, si no se proporciona usa hora actual)
        """
        self.placa = placa.upper().strip()
        self.id_unico = id_unico if id_unico else GeneradorID.generar_id_unico()
        self.hora_ingreso = hora_ingreso if hora_ingreso else TiempoUtils.obtener_tiempo_actual()
        self.hora_salida = None
        self.total_pagado = None
        
    def registrar_salida(self, precio_por_hora):
        """
        Registra la salida del vehículo y calcula el total a pagar
        
        Args:
            precio_por_hora: float (precio por hora actual)
        
        Returns:
            dict: Información del cobro
        """
        self.hora_salida = TiempoUtils.obtener_tiempo_actual()
        horas = self.obtener_duracion()
        self.total_pagado = TiempoUtils.calcular_total_a_pagar(horas, precio_por_hora)
        
        return {
            'id_unico': self.id_unico,
            'placa': self.placa,
            'hora_ingreso': self.hora_ingreso,
            'hora_salida': self.hora_salida,
            'horas_estadia': horas,
            'total_pagado': self.total_pagado,
            'precio_por_hora': precio_por_hora
        }
    
    def obtener_duracion(self):
        """
        Calcula el tiempo que lleva (o estuvo) el vehículo en el estacionamiento
        
        Returns:
            float: Horas de estadía
        """
        return TiempoUtils.calcular_duracion(self.hora_ingreso, self.hora_salida)
    
    def obtener_tiempo_formateado(self):
        """
        Retorna el tiempo de estadía en formato legible
        """
        horas = self.obtener_duracion()
        return TiempoUtils.formatear_duracion(horas)
    
    def esta_dentro(self):
        """
        Verifica si el vehículo sigue dentro del estacionamiento
        
        Returns:
            bool: True si aún está dentro, False si ya salió
        """
        return self.hora_salida is None
    
    def to_dict(self):
        """
        Convierte el vehículo a diccionario para guardar en JSON
        
        Returns:
            dict: Representación del vehículo
        """
        return {
            'id_unico': self.id_unico,
            'placa': self.placa,
            'hora_ingreso': self.hora_ingreso,
            'hora_salida': self.hora_salida,
            'total_pagado': self.total_pagado
        }
    
    @classmethod
    def from_dict(cls, datos):
        """
        Crea un vehículo desde un diccionario (para cargar desde JSON)
        
        Args:
            datos: dict con los datos del vehículo
        
        Returns:
            Vehiculo: Instancia del vehículo
        """
        vehiculo = cls(
            placa=datos['placa'],
            id_unico=datos['id_unico'],
            hora_ingreso=datos['hora_ingreso']
        )
        vehiculo.hora_salida = datos.get('hora_salida')
        vehiculo.total_pagado = datos.get('total_pagado')
        return vehiculo
    
    def __str__(self):
        """Representación en string del vehículo"""
        estado = "Dentro" if self.esta_dentro() else "Fuera"
        return f"Vehículo {self.placa} (ID: {self.id_unico}) - {estado}"
    
    def __repr__(self):
        return self.__str__()