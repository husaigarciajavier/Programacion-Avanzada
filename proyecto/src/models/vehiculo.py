"""
Clase Vehículo - Representa un vehículo en el estacionamiento
Optimizado con properties y mejor validación
"""

import re
from datetime import datetime
from src.utils.id_generator import GeneradorID
from src.utils.tiempo_utils import TiempoUtils
from src.config.constants import FORMATO_FECHA_HORA, PLACA_REGEX

class Vehiculo:
    """Clase que representa un vehículo estacionado"""
    
    def __init__(self, placa, id_unico=None, hora_ingreso=None):
        """
        Inicializa un nuevo vehículo
        
        Args:
            placa: str (placa del vehículo)
            id_unico: str (opcional, se genera automático)
            hora_ingreso: str (opcional, usa hora actual)
        """
        self._placa = self._validar_y_normalizar_placa(placa)
        self._id_unico = id_unico if id_unico else GeneradorID.generar_id_unico()
        self._hora_ingreso = hora_ingreso if hora_ingreso else TiempoUtils.obtener_tiempo_actual()
        self._hora_salida = None
        self._total_pagado = None
    
    @staticmethod
    def _validar_y_normalizar_placa(placa):
        """
        Valida y normaliza la placa del vehículo
        
        Args:
            placa: str
        
        Returns:
            str: Placa normalizada en mayúsculas
        
        Raises:
            ValueError: Si la placa no es válida
        """
        if not placa or not isinstance(placa, str):
            raise ValueError("La placa no puede estar vacía")
        
        placa_normalizada = placa.upper().strip()
        
        if not re.match(PLACA_REGEX, placa_normalizada):
            raise ValueError(f"Placa inválida. Formato: 6-7 caracteres alfanuméricos (ej: ABC123)")
        
        return placa_normalizada
    
    # ==================== PROPERTIES (GETTERS) ====================
    
    @property
    def placa(self):
        """Retorna la placa del vehículo"""
        return self._placa
    
    @property
    def id_unico(self):
        """Retorna el ID único del vehículo"""
        return self._id_unico
    
    @property
    def hora_ingreso(self):
        """Retorna la hora de ingreso"""
        return self._hora_ingreso
    
    @property
    def hora_salida(self):
        """Retorna la hora de salida (None si está dentro)"""
        return self._hora_salida
    
    @property
    def total_pagado(self):
        """Retorna el total pagado (None si no ha salido)"""
        return self._total_pagado
    
    @property
    def esta_dentro(self):
        """bool: True si el vehículo sigue dentro del estacionamiento"""
        return self._hora_salida is None
    
    @property
    def tiempo_estadia(self):
        """float: Horas que lleva (o estuvo) el vehículo en el estacionamiento"""
        return self.obtener_duracion()
    
    @property
    def tiempo_formateado(self):
        """str: Tiempo de estadía en formato legible"""
        return self.obtener_tiempo_formateado()
    
    # ==================== MÉTODOS PRINCIPALES ====================
    
    def registrar_salida(self, precio_por_hora):
        """
        Registra la salida del vehículo y calcula el total a pagar
        
        Args:
            precio_por_hora: float (precio por hora actual)
        
        Returns:
            dict: Información del cobro
        """
        if not self.esta_dentro:
            raise ValueError(f"El vehículo {self._placa} ya salió del estacionamiento")
        
        self._hora_salida = TiempoUtils.obtener_tiempo_actual()
        horas = self.obtener_duracion()
        self._total_pagado = TiempoUtils.calcular_total_a_pagar(horas, precio_por_hora)
        
        return {
            'id_unico': self._id_unico,
            'placa': self._placa,
            'hora_ingreso': self._hora_ingreso,
            'hora_salida': self._hora_salida,
            'horas_estadia': horas,
            'total_pagado': self._total_pagado,
            'precio_por_hora': precio_por_hora
        }
    
    def obtener_duracion(self):
        """
        Calcula el tiempo que lleva (o estuvo) el vehículo
        
        Returns:
            float: Horas de estadía (mínimo 0.1)
        """
        return TiempoUtils.calcular_duracion(self._hora_ingreso, self._hora_salida)
    
    def obtener_tiempo_formateado(self):
        """Retorna el tiempo de estadía en formato legible"""
        return TiempoUtils.formatear_duracion(self.obtener_duracion())
    
    # ==================== SERIALIZACIÓN ====================
    
    def to_dict(self):
        """
        Convierte el vehículo a diccionario para guardar en JSON
        
        Returns:
            dict: Representación completa del vehículo
        """
        return {
            'id_unico': self._id_unico,
            'placa': self._placa,
            'hora_ingreso': self._hora_ingreso,
            'hora_salida': self._hora_salida,
            'total_pagado': self._total_pagado
        }
    
    @classmethod
    def from_dict(cls, datos):
        """
        Crea un vehículo desde un diccionario
        
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
        vehiculo._hora_salida = datos.get('hora_salida')
        vehiculo._total_pagado = datos.get('total_pagado')
        return vehiculo
    
    # ==================== MÉTODOS ESPECIALES ====================
    
    def __str__(self):
        """Representación amigable del vehículo"""
        estado = "🟢 Dentro" if self.esta_dentro else "🔴 Fuera"
        return f"🚗 {self._placa} | ID: {self._id_unico[:8]}... | {estado}"
    
    def __repr__(self):
        """Representación detallada para depuración"""
        return f"Vehiculo(placa='{self._placa}', id='{self._id_unico}', dentro={self.esta_dentro})"
    
    def __eq__(self, other):
        """Compara dos vehículos por ID único"""
        if not isinstance(other, Vehiculo):
            return False
        return self._id_unico == other._id_unico
    
    def __hash__(self):
        """Hash basado en ID único para usar en sets/dicts"""
        return hash(self._id_unico)