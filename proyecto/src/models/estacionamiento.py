"""
Clase Estacionamiento - Gestiona la lógica del estacionamiento
Optimizado con búsqueda O(1) y mejor encapsulamiento
"""

import re
from datetime import datetime
from src.models.vehiculo import Vehiculo
from src.utils.config_manager import ConfigManager
from src.config.constants import PLACA_REGEX, MAX_CAPACIDAD

class Estacionamiento:
    """Clase principal que gestiona el estacionamiento"""
    
    def __init__(self):
        """Inicializa el estacionamiento con la configuración actual"""
        self._config_manager = ConfigManager()
        self._capacidad_maxima = self._config_manager.obtener_capacidad()
        self._vehiculos = {}  # {id_unico: Vehiculo}
        self._placas_activas = set()  # NUEVO: set para búsqueda O(1)
        self._eventos_callbacks = []  # NUEVO: para eventos (ingreso/salida)
    
    # ==================== PROPIEDADES ====================
    
    @property
    def capacidad_maxima(self):
        return self._capacidad_maxima
    
    @property
    def vehiculos_activos(self):
        """Retorna lista de vehículos actualmente dentro (cálculo en tiempo real)"""
        return [v for v in self._vehiculos.values() if v.esta_dentro]
    
    @property
    def total_vehiculos(self):
        """Número de vehículos actualmente dentro"""
        return len(self.vehiculos_activos)
    
    @property
    def espacios_disponibles(self):
        """Número de espacios libres"""
        return self._capacidad_maxima - self.total_vehiculos
    
    @property
    def ocupacion_porcentaje(self):
        """Porcentaje de ocupación (0-100)"""
        if self._capacidad_maxima == 0:
            return 0
        return (self.total_vehiculos / self._capacidad_maxima) * 100
    
    @property
    def esta_lleno(self):
        """bool: True si no hay espacios disponibles"""
        return self.espacios_disponibles <= 0
    
    # ==================== EVENTOS ====================
    
    def registrar_evento(self, callback):
        """
        Registra una función callback para eventos (ingreso/salida)
        
        Args:
            callback: función que recibe (tipo_evento, datos)
        """
        self._eventos_callbacks.append(callback)
    
    def _notificar_evento(self, tipo, datos):
        """Notifica a todos los callbacks registrados"""
        for callback in self._eventos_callbacks:
            try:
                callback(tipo, datos)
            except Exception as e:
                print(f"Error en callback: {e}")
    
    # ==================== MÉTODOS PRINCIPALES ====================
    
    def hay_espacio(self):
        """Verifica si hay espacios disponibles"""
        return not self.esta_lleno
    
    def registrar_ingreso(self, placa):
        """
        Registra el ingreso de un nuevo vehículo
        
        Returns:
            tuple: (éxito: bool, mensaje: str, vehiculo: Vehiculo o None)
        """
        # Verificar espacio
        if not self.hay_espacio():
            return False, f"Estacionamiento lleno. Capacidad: {self._capacidad_maxima}", None
        
        # Validar placa (ahora el vehículo mismo la valida)
        try:
            vehiculo = Vehiculo(placa)
        except ValueError as e:
            return False, str(e), None
        
        # Verificar si ya está dentro (búsqueda O(1) con set)
        if vehiculo.placa in self._placas_activas:
            return False, f"El vehículo {placa} ya está dentro", None
        
        # Registrar ingreso
        self._vehiculos[vehiculo.id_unico] = vehiculo
        self._placas_activas.add(vehiculo.placa)
        
        # Notificar evento
        self._notificar_evento('INGRESO', {
            'placa': vehiculo.placa,
            'id': vehiculo.id_unico,
            'hora': vehiculo.hora_ingreso
        })
        
        return True, f"✅ Vehículo {placa} ingresado. ID: {vehiculo.id_unico}", vehiculo
    
    def registrar_salida(self, id_unico, precio_por_hora=None):
        """
        Registra la salida de un vehículo
        
        Returns:
            tuple: (éxito: bool, mensaje: str, cobro: dict o None)
        """
        # Buscar vehículo
        vehiculo = self._vehiculos.get(id_unico)
        
        if not vehiculo:
            return False, f"❌ No se encontró vehículo con ID: {id_unico}", None
        
        if not vehiculo.esta_dentro:
            return False, f"❌ El vehículo {vehiculo.placa} ya salió", None
        
        # Usar precio actual si no se especifica
        if precio_por_hora is None:
            precio_por_hora = self._config_manager.obtener_precio()
        
        # Registrar salida
        try:
            cobro = vehiculo.registrar_salida(precio_por_hora)
            self._placas_activas.discard(vehiculo.placa)  # Remover del set
            
            # Notificar evento
            self._notificar_evento('SALIDA', cobro)
            
            return True, f"✅ Salida registrada. Total: ${cobro['total_pagado']:.2f}", cobro
        except ValueError as e:
            return False, str(e), None
    
    def buscar_por_placa(self, placa):
        """
        Busca un vehículo por su placa (búsqueda O(n) pero con early exit)
        
        Returns:
            Vehiculo or None
        """
        placa_normalizada = placa.upper().strip()
        for vehiculo in self._vehiculos.values():
            if vehiculo.placa == placa_normalizada:
                return vehiculo
        return None
    
    def buscar_por_id(self, id_unico):
        """Busca un vehículo por ID (búsqueda O(1) en diccionario)"""
        return self._vehiculos.get(id_unico)
    
    def obtener_todos_vehiculos(self):
        """Retorna todos los vehículos (historial completo)"""
        return list(self._vehiculos.values())
    
    # ==================== CONFIGURACIÓN ====================
    
    def obtener_precio_actual(self):
        """Retorna el precio por hora actual"""
        return self._config_manager.obtener_precio()
    
    def obtener_configuracion(self):
        """Retorna la configuración actual completa"""
        return {
            'capacidad_maxima': self._capacidad_maxima,
            'precio_por_hora': self._config_manager.obtener_precio(),
            'vehiculos_activos': self.total_vehiculos,
            'espacios_disponibles': self.espacios_disponibles,
            'ocupacion': self.ocupacion_porcentaje
        }
    
    def actualizar_capacidad(self, nueva_capacidad):
        """
        Actualiza la capacidad máxima del estacionamiento
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if nueva_capacidad < self.total_vehiculos:
            return False, f"❌ No se puede reducir a {nueva_capacidad} (hay {self.total_vehiculos} vehículos)"
        
        exito, mensaje = self._config_manager.actualizar_capacidad(nueva_capacidad, self.total_vehiculos)
        
        if exito:
            self._capacidad_maxima = nueva_capacidad
        
        return exito, mensaje
    
    def actualizar_precio(self, nuevo_precio):
        """Actualiza el precio por hora"""
        return self._config_manager.actualizar_precio(nuevo_precio)
    
    # ==================== SERIALIZACIÓN ====================
    
    def to_dict(self):
        """Convierte el estado a diccionario"""
        return {
            'capacidad_maxima': self._capacidad_maxima,
            'vehiculos': [v.to_dict() for v in self._vehiculos.values()]
        }
    
    def cargar_datos(self, vehiculos_dict):
        """Carga vehículos desde diccionario"""
        self._vehiculos = {}
        self._placas_activas = set()
        
        for v_data in vehiculos_dict:
            vehiculo = Vehiculo.from_dict(v_data)
            self._vehiculos[vehiculo.id_unico] = vehiculo
            if vehiculo.esta_dentro:
                self._placas_activas.add(vehiculo.placa)