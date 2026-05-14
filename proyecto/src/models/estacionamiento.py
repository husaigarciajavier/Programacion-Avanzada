"""
Clase Estacionamiento - Gestiona la lógica del estacionamiento
"""

import re
from src.models.vehiculo import Vehiculo
from src.utils.config_manager import ConfigManager
from src.config.constants import PLACA_REGEX

class Estacionamiento:
    """Clase principal que gestiona el estacionamiento"""
    
    def __init__(self):
        """Inicializa el estacionamiento con la configuración actual"""
        self.config_manager = ConfigManager()
        self.capacidad_maxima = self.config_manager.obtener_capacidad()
        self.vehiculos = {}  # Diccionario {id_unico: Vehiculo}
        self._espacios_ocupados = 0
    
    def _validar_placa(self, placa):
        """
        Valida que la placa tenga un formato correcto
        
        Args:
            placa: str
        
        Returns:
            bool: True si es válida
        """
        if not placa or not isinstance(placa, str):
            return False
        return bool(re.match(PLACA_REGEX, placa.upper().strip()))
    
    def _vehiculo_ya_esta_dentro(self, placa):
        """
        Verifica si un vehículo con esa placa ya está dentro
        
        Args:
            placa: str
        
        Returns:
            bool: True si ya está estacionado
        """
        for vehiculo in self.vehiculos.values():
            if vehiculo.esta_dentro() and vehiculo.placa == placa.upper().strip():
                return True
        return False
    
    def hay_espacio(self):
        """
        Verifica si hay espacios disponibles
        
        Returns:
            bool: True si hay espacio
        """
        return len(self.obtener_vehiculos_activos()) < self.capacidad_maxima
    
    def registrar_ingreso(self, placa):
        """
        Registra el ingreso de un nuevo vehículo
        
        Args:
            placa: str (placa del vehículo)
        
        Returns:
            tuple: (éxito: bool, mensaje: str, vehiculo: Vehiculo o None)
        """
        # Validar placa
        if not self._validar_placa(placa):
            return False, f"Placa inválida. Formato: 6-7 caracteres alfanuméricos (ej: ABC123)", None
        
        # Verificar si ya está dentro
        if self._vehiculo_ya_esta_dentro(placa):
            return False, f"El vehículo con placa {placa} ya se encuentra dentro del estacionamiento", None
        
        # Verificar espacio
        if not self.hay_espacio():
            return False, f"Estacionamiento lleno. Capacidad máxima: {self.capacidad_maxima} vehículos", None
        
        # Registrar ingreso
        nuevo_vehiculo = Vehiculo(placa)
        self.vehiculos[nuevo_vehiculo.id_unico] = nuevo_vehiculo
        
        return True, f"Vehículo {placa} ingresado con ID: {nuevo_vehiculo.id_unico}", nuevo_vehiculo
    
    def registrar_salida(self, id_unico, precio_por_hora=None):
        """
        Registra la salida de un vehículo
        
        Args:
            id_unico: str (ID del vehículo)
            precio_por_hora: float (opcional, usa el actual si no se especifica)
        
        Returns:
            tuple: (éxito: bool, mensaje: str, cobro: dict o None)
        """
        # Buscar vehículo
        vehiculo = self.vehiculos.get(id_unico)
        
        if not vehiculo:
            return False, f"No se encontró ningún vehículo con ID: {id_unico}", None
        
        if not vehiculo.esta_dentro():
            return False, f"El vehículo con ID {id_unico} ya salió del estacionamiento", None
        
        # Usar precio actual si no se especifica
        if precio_por_hora is None:
            precio_por_hora = self.config_manager.obtener_precio()
        
        # Registrar salida y calcular cobro
        cobro = vehiculo.registrar_salida(precio_por_hora)
        
        return True, f"Salida registrada. Total a pagar: ${cobro['total_pagado']:.2f}", cobro
    
    def obtener_vehiculos_activos(self):
        """
        Retorna lista de vehículos actualmente dentro
        
        Returns:
            list: Vehículos activos
        """
        return [v for v in self.vehiculos.values() if v.esta_dentro()]
    
    def obtener_vehiculos_historial(self):
        """
        Retorna lista de todos los vehículos (incluyendo los que salieron)
        
        Returns:
            list: Todos los vehículos
        """
        return list(self.vehiculos.values())
    
    def obtener_espacios_disponibles(self):
        """
        Retorna el número de espacios disponibles
        
        Returns:
            int: Espacios libres
        """
        return self.capacidad_maxima - len(self.obtener_vehiculos_activos())
    
    def obtener_ocupacion(self):
        """
        Retorna el porcentaje de ocupación
        
        Returns:
            float: Porcentaje ocupado
        """
        if self.capacidad_maxima == 0:
            return 0
        return (len(self.obtener_vehiculos_activos()) / self.capacidad_maxima) * 100
    
    def actualizar_capacidad(self, nueva_capacidad):
        """
        Actualiza la capacidad máxima del estacionamiento
        
        Args:
            nueva_capacidad: int
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        vehiculos_activos = len(self.obtener_vehiculos_activos())
        
        exito, mensaje = self.config_manager.actualizar_capacidad(nueva_capacidad, vehiculos_activos)
        
        if exito:
            self.capacidad_maxima = nueva_capacidad
        
        return exito, mensaje
    
    def actualizar_precio(self, nuevo_precio):
        """
        Actualiza el precio por hora
        
        Args:
            nuevo_precio: float
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        return self.config_manager.actualizar_precio(nuevo_precio)
    
    def obtener_precio_actual(self):
        """Retorna el precio por hora actual"""
        return self.config_manager.obtener_precio()
    
    def obtener_configuracion(self):
        """Retorna la configuración actual"""
        return {
            'capacidad_maxima': self.capacidad_maxima,
            'precio_por_hora': self.config_manager.obtener_precio(),
            'vehiculos_activos': len(self.obtener_vehiculos_activos()),
            'espacios_disponibles': self.obtener_espacios_disponibles(),
            'ocupacion': self.obtener_ocupacion()
        }
    
    def buscar_vehiculo_por_placa(self, placa):
        """
        Busca un vehículo por su placa
        
        Args:
            placa: str
        
        Returns:
            Vehiculo or None: El vehículo encontrado
        """
        placa_normalizada = placa.upper().strip()
        for vehiculo in self.vehiculos.values():
            if vehiculo.placa == placa_normalizada:
                return vehiculo
        return None
    
    def buscar_vehiculo_por_id(self, id_unico):
        """
        Busca un vehículo por su ID único
        
        Args:
            id_unico: str
        
        Returns:
            Vehiculo or None: El vehículo encontrado
        """
        return self.vehiculos.get(id_unico)
    
    def to_dict(self):
        """
        Convierte el estado del estacionamiento a diccionario
        """
        return {
            'capacidad_maxima': self.capacidad_maxima,
            'vehiculos': [v.to_dict() for v in self.vehiculos.values()]
        }
    
    def cargar_datos(self, vehiculos_dict):
        """
        Carga vehículos desde diccionario
        """
        self.vehiculos = {}
        for v_data in vehiculos_dict:
            vehiculo = Vehiculo.from_dict(v_data)
            self.vehiculos[vehiculo.id_unico] = vehiculo