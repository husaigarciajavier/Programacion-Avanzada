#!/usr/bin/env python3
"""
Sistema de Gestión de Estacionamiento
Punto de entrada de la aplicación
"""

import sys
import os
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.ventana_principal import VentanaPrincipal
from src.config.constants import crear_directorios


def main():
    """Función principal que inicia la aplicación"""
    
    # Cabecera
    print("=" * 50)
    print("🅿️ SISTEMA DE ESTACIONAMIENTO v1.0")
    print("=" * 50)
    
    # Crear directorios necesarios
    crear_directorios()
    print("✅ Directorios listos")
    
    # Iniciar aplicación
    try:
        app = VentanaPrincipal()
        print("✅ Aplicación iniciada")
        app.ejecutar()
    except KeyboardInterrupt:
        print("\n⚠️ Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
        sys.exit(1)


if __name__ == "__main__":
    main()