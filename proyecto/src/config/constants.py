"""
Constantes globales del proyecto Estacionamiento
Todas las configuraciones fijas del sistema
"""

import os
from pathlib import Path

# ==================== RUTAS DEL SISTEMA ====================
PROYECTO_RAIZ = Path(__file__).parent.parent.parent
SRC_DIR = PROYECTO_RAIZ / "src"
DATABASE_DIR = SRC_DIR / "database" / "data"
LOGS_DIR = PROYECTO_RAIZ / "logs"

# Archivos de datos
CONFIG_FILE = DATABASE_DIR / "config_estacionamiento.json"
VEHICULOS_ACTIVOS_FILE = DATABASE_DIR / "vehiculos_activos.json"
HISTORIAL_FILE = DATABASE_DIR / "historial.json"
MOVIMIENTOS_DIA_FILE = LOGS_DIR / "movimientos_dia.txt"

# ==================== VALORES POR DEFECTO ====================
CAPACIDAD_MAXIMA_DEFECTO = 32
PRECIO_POR_HORA_DEFECTO = 5.0

# ==================== RANGOS PERMITIDOS ====================
MIN_CAPACIDAD = 1
MAX_CAPACIDAD = 100
MIN_PRECIO = 0.5
MAX_PRECIO = 50.0

# ==================== FORMATOS ====================
FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M:%S"
FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M:%S"

# ==================== VALIDACIONES ====================
# Formato de placa: 6-7 caracteres alfanuméricos (letras mayúsculas y números)
PLACA_REGEX = r'^[A-Z0-9]{6,7}$'

# ==================== CONFIGURACIÓN UI ====================
VENTANA_TITULO = "Sistema de Gestión de Estacionamiento"
VENTANA_SIZE = "900x600"
COLOR_FONDO = "#f0f0f0"
COLOR_BOTON = "#4CAF50"
COLOR_BOTON_PELIGRO = "#f44336"
COLOR_BOTON_INFO = "#2196F3"
COLOR_TEXTO = "#333333"

# ==================== FUNCIONES AUXILIARES ====================
def crear_directorios():
    """Crea los directorios necesarios si no existen"""
    directorios = [DATABASE_DIR, LOGS_DIR]
    for directorio in directorios:
        if not directorio.exists():
            directorio.mkdir(parents=True, exist_ok=True)
            print(f" Directorio creado: {directorio}")

def limpiar_consola():
    """Limpia la consola (útil para depuración)"""
    os.system('cls' if os.name == 'nt' else 'clear')