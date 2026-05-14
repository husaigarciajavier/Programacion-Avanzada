"""
Manejador de Base de Datos - Persistencia de datos
Guarda y carga automáticamente el estado del estacionamiento
"""

import json
import os
import shutil
from datetime import datetime
from src.config.constants import (
    DATABASE_DIR,
    VEHICULOS_ACTIVOS_FILE,
    HISTORIAL_FILE,
    FORMATO_FECHA_HORA
)
from src.models.vehiculo import Vehiculo

class DatabaseManager:
    """Clase para manejar la persistencia de datos"""
    
    def __init__(self):
        """Inicializa el manejador de base de datos"""
        self._verificar_directorios()
    
    def _verificar_directorios(self):
        """Verifica que los directorios necesarios existan"""
        if not DATABASE_DIR.exists():
            DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    def guardar_vehiculos_activos(self, estacionamiento):
        """
        Guarda los vehículos activos en un archivo JSON
        
        Args:
            estacionamiento: Instancia de Estacionamiento
        
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            vehiculos_activos = estacionamiento.obtener_vehiculos_activos()
            datos = {
                'fecha_guardado': datetime.now().strftime(FORMATO_FECHA_HORA),
                'cantidad_vehiculos': len(vehiculos_activos),
                'vehiculos': [v.to_dict() for v in vehiculos_activos]
            }
            
            with open(VEHICULOS_ACTIVOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error al guardar vehículos activos: {e}")
            return False
    
    def cargar_vehiculos_activos(self, estacionamiento):
        """
        Carga los vehículos activos desde el archivo JSON
        
        Args:
            estacionamiento: Instancia de Estacionamiento
        
        Returns:
            bool: True si se cargaron correctamente
        """
        if not VEHICULOS_ACTIVOS_FILE.exists():
            return False
        
        try:
            with open(VEHICULOS_ACTIVOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # Limpiar vehículos actuales
            estacionamiento.vehiculos.clear()
            
            # Cargar vehículos
            for v_data in datos.get('vehiculos', []):
                vehiculo = Vehiculo.from_dict(v_data)
                estacionamiento.vehiculos[vehiculo.id_unico] = vehiculo
            
            return True
        except Exception as e:
            print(f"Error al cargar vehículos activos: {e}")
            return False
    
    def guardar_historial(self, movimiento):
        """
        Guarda un movimiento en el historial completo
        
        Args:
            movimiento: dict con los datos del movimiento
        
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            # Cargar historial existente
            historial = self.cargar_historial_completo()
            
            # Agregar nuevo movimiento
            movimiento['fecha_registro'] = datetime.now().strftime(FORMATO_FECHA_HORA)
            historial.append(movimiento)
            
            # Guardar historial actualizado
            with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error al guardar en historial: {e}")
            return False
    
    def cargar_historial_completo(self):
        """
        Carga todo el historial de movimientos
        
        Returns:
            list: Lista de movimientos
        """
        if not HISTORIAL_FILE.exists():
            return []
        
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar historial: {e}")
            return []
    
    def guardar_estado_completo(self, estacionamiento, registro_movimientos):
        """
        Guarda el estado completo del sistema
        
        Args:
            estacionamiento: Instancia de Estacionamiento
            registro_movimientos: Instancia de RegistroMovimientos
        
        Returns:
            bool: True si todo se guardó correctamente
        """
        try:
            # Guardar vehículos activos
            exito1 = self.guardar_vehiculos_activos(estacionamiento)
            
            # Guardar configuración (ya lo hace ConfigManager automáticamente)
            
            # Guardar movimientos del día en historial
            for movimiento in registro_movimientos.obtener_movimientos_hoy():
                self.guardar_historial(movimiento)
            
            return exito1
        except Exception as e:
            print(f"Error al guardar estado completo: {e}")
            return False
    
    def crear_backup(self):
        """
        Crea una copia de seguridad de todos los datos
        
        Returns:
            str: Ruta del backup o None si hay error
        """
        try:
            # Crear carpeta de backups
            backup_dir = DATABASE_DIR / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # Nombre del backup con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Copiar archivos
            archivos = [VEHICULOS_ACTIVOS_FILE, HISTORIAL_FILE]
            for archivo in archivos:
                if archivo.exists():
                    shutil.copy2(archivo, backup_path / archivo.name)
            
            return str(backup_path)
        except Exception as e:
            print(f"Error al crear backup: {e}")
            return None
    
    def limpiar_datos(self, confirmar=False):
        """
        Limpia todos los datos guardados (reinicia el sistema)
        
        Args:
            confirmar: bool (debe ser True para ejecutar)
        
        Returns:
            bool: True si se limpiaron correctamente
        """
        if not confirmar:
            return False
        
        try:
            # Eliminar archivos de datos
            archivos = [VEHICULOS_ACTIVOS_FILE, HISTORIAL_FILE]
            for archivo in archivos:
                if archivo.exists():
                    archivo.unlink()
            
            return True
        except Exception as e:
            print(f"Error al limpiar datos: {e}")
            return False
    
    def obtener_estadisticas_historial(self):
        """
        Obtiene estadísticas del historial completo
        
        Returns:
            dict: Estadísticas
        """
        historial = self.cargar_historial_completo()
        
        ingresos = [m for m in historial if m.get('tipo') == 'INGRESO']
        salidas = [m for m in historial if m.get('tipo') == 'SALIDA']
        total_recaudado = sum([m.get('total_pagado', 0) for m in salidas])
        
        return {
            'total_ingresos_historicos': len(ingresos),
            'total_salidas_historicas': len(salidas),
            'total_recaudado_historico': total_recaudado,
            'ultimo_movimiento': historial[-1] if historial else None
        }