#!/usr/bin/env python3
"""
Sistema de Gestión de Estacionamiento
Archivo principal - Punto de entrada de la aplicación

Materia: Programación Avanzada
"""

import sys
import os

# Agregar el directorio padre (proyecto/) al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ahora importar desde src
from src.ui.ventana_principal import VentanaPrincipal
from src.config.constants import crear_directorios

def main():
    """
    Función principal que inicia la aplicación
    """
    print("=" * 60)
    print("🅿️ SISTEMA DE GESTIÓN DE ESTACIONAMIENTO")
    print("=" * 60)
    print("Iniciando aplicación...")
    
    # Crear directorios necesarios
    crear_directorios()
    print("✅ Directorios verificados/creados")
    
    # Iniciar la interfaz gráfica
    try:
        print("✅ Cargando interfaz gráfica...")
        app = VentanaPrincipal()
        print("✅ Aplicación iniciada correctamente")
        print("💡 Para cerrar la aplicación, cierre la ventana principal")
        app.ejecutar()
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()
        input("Presione Enter para salir...")
        sys.exit(1)

if __name__ == "__main__":
    main()