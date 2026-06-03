"""
Manejador de Base de Datos - Persistencia de datos
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from src.config.constants import (
    DATABASE_DIR, VEHICULOS_ACTIVOS_FILE, HISTORIAL_FILE, FORMATO_FECHA_HORA
)
from src.models.vehiculo import Vehiculo


class DatabaseManager:
    """Maneja la persistencia de datos"""
    
    def __init__(self):
        DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # ==================== VEHÍCULOS ACTIVOS ====================
    
    def guardar_vehiculos_activos(self, estacionamiento) -> bool:
        """Guarda los vehículos activos"""
        try:
            datos = {
                'fecha_guardado': datetime.now().strftime(FORMATO_FECHA_HORA),
                'vehiculos': [v.to_dict() for v in estacionamiento.vehiculos_activos]
            }
            with open(VEHICULOS_ACTIVOS_FILE, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def cargar_vehiculos_activos(self, estacionamiento) -> bool:
        """Carga los vehículos activos"""
        if not VEHICULOS_ACTIVOS_FILE.exists():
            return False
        
        try:
            with open(VEHICULOS_ACTIVOS_FILE, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            estacionamiento._vehiculos = {}
            if hasattr(estacionamiento, '_placas_activas'):
                estacionamiento._placas_activas.clear()
            
            for v_data in datos.get('vehiculos', []):
                v = Vehiculo.from_dict(v_data)
                estacionamiento._vehiculos[v.id_unico] = v
                if hasattr(estacionamiento, '_placas_activas') and v.esta_dentro:
                    estacionamiento._placas_activas.add(v.placa)
            return True
        except Exception:
            return False
    
    # ==================== BACKUP (SIMPLIFICADO) ====================
    
    def crear_backup(self) -> str | None:
        """Crea una copia de seguridad"""
        try:
            backup_dir = DATABASE_DIR / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"backup_{timestamp}"
            backup_path.mkdir()
            
            for archivo in [VEHICULOS_ACTIVOS_FILE, HISTORIAL_FILE]:
                if archivo.exists():
                    shutil.copy2(archivo, backup_path / archivo.name)
            return str(backup_path)
        except Exception:
            return None
    
    # ==================== HISTORIAL ====================
    
    def guardar_historial(self, movimiento: dict) -> bool:
        """Guarda un movimiento en el historial"""
        try:
            historial = self.cargar_historial_completo()
            movimiento['fecha_registro'] = datetime.now().strftime(FORMATO_FECHA_HORA)
            historial.append(movimiento)
            
            # Mantener últimos 5000 movimientos
            if len(historial) > 5000:
                historial = historial[-5000:]
            
            with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
                json.dump(historial, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def cargar_historial_completo(self) -> list:
        """Carga todo el historial"""
        if not HISTORIAL_FILE.exists():
            return []
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    # ==================== ESTADO COMPLETO ====================
    
    def guardar_estado_completo(self, estacionamiento, registro_movimientos) -> bool:
        """Guarda el estado completo"""
        exito = self.guardar_vehiculos_activos(estacionamiento)
        for m in registro_movimientos.obtener_movimientos_hoy()[-20:]:
            self.guardar_historial(m)
        self.crear_backup()
        return exito
    
    # ==================== ESTADÍSTICAS ====================
    
    def obtener_estadisticas(self) -> dict:
        """Obtiene estadísticas básicas"""
        historial = self.cargar_historial_completo()
        ingresos = [m for m in historial if m.get('tipo') == 'INGRESO']
        salidas = [m for m in historial if m.get('tipo') == 'SALIDA']
        total = sum(m.get('total_pagado', 0) for m in salidas)
        
        return {
            'total_ingresos': len(ingresos),
            'total_salidas': len(salidas),
            'total_recaudado': round(total, 2),
            'promedio': round(total / len(salidas), 2) if salidas else 0
        }
    
    # ==================== MANTENIMIENTO ====================
    
    def limpiar_datos(self, confirmar=False) -> bool:
        """Limpia todos los datos"""
        if not confirmar:
            return False
        try:
            for archivo in [VEHICULOS_ACTIVOS_FILE, HISTORIAL_FILE]:
                if archivo.exists():
                    archivo.unlink()
            return True
        except Exception:
            return False