"""
Gestor de configuración del estacionamiento
Maneja la carga/guardado de capacidad máxima y precio por hora
"""

import json
import os
from datetime import datetime
from src.config.constants import (
    CONFIG_FILE,
    CAPACIDAD_MAXIMA_DEFECTO,
    PRECIO_POR_HORA_DEFECTO,
    MIN_CAPACIDAD,
    MAX_CAPACIDAD,
    MIN_PRECIO,
    MAX_PRECIO,
    FORMATO_FECHA_HORA
)

class ConfigManager:
    """Clase para gestionar la configuración del estacionamiento"""
    
    def __init__(self):
        self._config = self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """
        Carga la configuración desde el archivo JSON
        Si no existe, crea una con valores por defecto
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Validar datos cargados
                if not self._validar_configuracion(config):
                    return self._crear_configuracion_defecto()
                
                return config
            except (json.JSONDecodeError, KeyError):
                return self._crear_configuracion_defecto()
        else:
            return self._crear_configuracion_defecto()
    
    def _crear_configuracion_defecto(self):
        """Crea configuración con valores por defecto"""
        return {
            'capacidad_maxima': CAPACIDAD_MAXIMA_DEFECTO,
            'precio_por_hora': PRECIO_POR_HORA_DEFECTO,
            'ultima_modificacion': datetime.now().strftime(FORMATO_FECHA_HORA)
        }
    
    def _validar_configuracion(self, config):
        """Valida que la configuración tenga valores correctos"""
        capacidad = config.get('capacidad_maxima', CAPACIDAD_MAXIMA_DEFECTO)
        precio = config.get('precio_por_hora', PRECIO_POR_HORA_DEFECTO)
        
        return (MIN_CAPACIDAD <= capacidad <= MAX_CAPACIDAD and 
                MIN_PRECIO <= precio <= MAX_PRECIO)
    
    def guardar_configuracion(self, capacidad_maxima, precio_por_hora):
        """
        Guarda la configuración en el archivo JSON
        
        Args:
            capacidad_maxima: int (nueva capacidad)
            precio_por_hora: float (nuevo precio)
        
        Returns:
            bool: True si se guardó correctamente, False si hay error
        """
        # Validar valores
        if not (MIN_CAPACIDAD <= capacidad_maxima <= MAX_CAPACIDAD):
            raise ValueError(f"Capacidad debe estar entre {MIN_CAPACIDAD} y {MAX_CAPACIDAD}")
        
        if not (MIN_PRECIO <= precio_por_hora <= MAX_PRECIO):
            raise ValueError(f"Precio debe estar entre ${MIN_PRECIO} y ${MAX_PRECIO}")
        
        self._config = {
            'capacidad_maxima': capacidad_maxima,
            'precio_por_hora': precio_por_hora,
            'ultima_modificacion': datetime.now().strftime(FORMATO_FECHA_HORA)
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def obtener_capacidad(self):
        """Retorna la capacidad máxima actual"""
        return self._config['capacidad_maxima']
    
    def obtener_precio(self):
        """Retorna el precio por hora actual"""
        return self._config['precio_por_hora']
    
    def actualizar_capacidad(self, nueva_capacidad, vehiculos_activos=0):
        """
        Actualiza la capacidad máxima, validando que no sea menor a vehículos activos
        
        Args:
            nueva_capacidad: int
            vehiculos_activos: int (cantidad de vehículos actualmente estacionados)
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if nueva_capacidad < vehiculos_activos:
            return False, f"No se puede reducir la capacidad a {nueva_capacidad} porque hay {vehiculos_activos} vehículos estacionados"
        
        if not (MIN_CAPACIDAD <= nueva_capacidad <= MAX_CAPACIDAD):
            return False, f"La capacidad debe estar entre {MIN_CAPACIDAD} y {MAX_CAPACIDAD}"
        
        exito = self.guardar_configuracion(nueva_capacidad, self.obtener_precio())
        if exito:
            return True, f"Capacidad actualizada a {nueva_capacidad} lugares"
        else:
            return False, "Error al guardar la configuración"
    
    def actualizar_precio(self, nuevo_precio):
        """
        Actualiza el precio por hora
        
        Args:
            nuevo_precio: float
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if not (MIN_PRECIO <= nuevo_precio <= MAX_PRECIO):
            return False, f"El precio debe estar entre ${MIN_PRECIO} y ${MAX_PRECIO}"
        
        exito = self.guardar_configuracion(self.obtener_capacidad(), nuevo_precio)
        if exito:
            return True, f"Precio actualizado a ${nuevo_precio:.2f} por hora"
        else:
            return False, "Error al guardar la configuración"