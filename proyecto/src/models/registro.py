"""
Clase Registro - Maneja el historial de movimientos del día
"""

from datetime import datetime
from src.config.constants import FORMATO_FECHA, FORMATO_FECHA_HORA, MOVIMIENTOS_DIA_FILE
from src.utils.tiempo_utils import TiempoUtils

class RegistroMovimientos:
    """Clase para registrar y gestionar movimientos del día"""
    
    def __init__(self):
        self.movimientos = []
        self.fecha_actual = TiempoUtils.obtener_fecha_actual()
    
    def _obtener_archivo_hoy(self):
        """
        Obtiene la ruta del archivo de movimientos para la fecha actual
        """
        # Usar el archivo fijo o crear uno por fecha
        return MOVIMIENTOS_DIA_FILE
    
    def registrar_ingreso(self, placa, id_unico, espacios_disponibles):
        """
        Registra un ingreso en el historial
        
        Args:
            placa: str
            id_unico: str
            espacios_disponibles: int
        """
        movimiento = {
            'tipo': 'INGRESO',
            'fecha_hora': TiempoUtils.obtener_tiempo_actual(),
            'placa': placa,
            'id_unico': id_unico,
            'espacios_disponibles': espacios_disponibles
        }
        self.movimientos.append(movimiento)
        self._guardar_movimiento_en_archivo(movimiento)
    
    def registrar_salida(self, placa, id_unico, horas_estadia, total_pagado, espacios_disponibles):
        """
        Registra una salida en el historial
        
        Args:
            placa: str
            id_unico: str
            horas_estadia: float
            total_pagado: float
            espacios_disponibles: int
        """
        movimiento = {
            'tipo': 'SALIDA',
            'fecha_hora': TiempoUtils.obtener_tiempo_actual(),
            'placa': placa,
            'id_unico': id_unico,
            'horas_estadia': horas_estadia,
            'total_pagado': total_pagado,
            'espacios_disponibles': espacios_disponibles
        }
        self.movimientos.append(movimiento)
        self._guardar_movimiento_en_archivo(movimiento)
    
    def _guardar_movimiento_en_archivo(self, movimiento):
        """
        Guarda un movimiento en el archivo de texto
        
        Args:
            movimiento: dict con el movimiento
        """
        try:
            with open(self._obtener_archivo_hoy(), 'a', encoding='utf-8') as f:
                if movimiento['tipo'] == 'INGRESO':
                    linea = (f"[{movimiento['fecha_hora']}] INGRESO - "
                            f"Placa: {movimiento['placa']} | "
                            f"ID: {movimiento['id_unico']} | "
                            f"Espacios libres: {movimiento['espacios_disponibles']}\n")
                else:
                    linea = (f"[{movimiento['fecha_hora']}] SALIDA - "
                            f"Placa: {movimiento['placa']} | "
                            f"ID: {movimiento['id_unico']} | "
                            f"Horas: {movimiento['horas_estadia']} | "
                            f"Total: ${movimiento['total_pagado']:.2f} | "
                            f"Espacios libres: {movimiento['espacios_disponibles']}\n")
                
                f.write(linea)
        except Exception as e:
            print(f"Error al guardar movimiento: {e}")
    
    def obtener_movimientos_hoy(self):
        """
        Retorna todos los movimientos del día
        
        Returns:
            list: Movimientos registrados
        """
        return self.movimientos
    
    def exportar_reporte_diario(self, ruta_archivo=None):
        """
        Exporta un reporte completo del día a un archivo de texto
        
        Args:
            ruta_archivo: str (ruta opcional, usa la predeterminada si no se especifica)
        
        Returns:
            str: Ruta del archivo generado
        """
        if ruta_archivo is None:
            ruta_archivo = self._obtener_archivo_hoy()
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("=" * 70 + "\n")
                f.write(f"REPORTE DE MOVIMIENTOS - {self.fecha_actual}\n")
                f.write("=" * 70 + "\n\n")
                
                # Resumen
                ingresos = [m for m in self.movimientos if m['tipo'] == 'INGRESO']
                salidas = [m for m in self.movimientos if m['tipo'] == 'SALIDA']
                total_recaudado = sum([m.get('total_pagado', 0) for m in salidas])
                
                f.write("RESUMEN DEL DÍA:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total de ingresos: {len(ingresos)}\n")
                f.write(f"Total de salidas: {len(salidas)}\n")
                f.write(f"Total recaudado: ${total_recaudado:.2f}\n")
                f.write("\n")
                
                # Detalle de movimientos
                f.write("DETALLE DE MOVIMIENTOS:\n")
                f.write("-" * 40 + "\n\n")
                
                for m in self.movimientos:
                    if m['tipo'] == 'INGRESO':
                        f.write(f"[{m['fecha_hora']}] INGRESO: {m['placa']} (ID: {m['id_unico']})\n")
                        f.write(f"  → Espacios disponibles: {m['espacios_disponibles']}\n\n")
                    else:
                        f.write(f"[{m['fecha_hora']}] SALIDA: {m['placa']} (ID: {m['id_unico']})\n")
                        f.write(f"  → Horas: {m['horas_estadia']:.2f} | Total: ${m['total_pagado']:.2f}\n")
                        f.write(f"  → Espacios disponibles: {m['espacios_disponibles']}\n\n")
                
                f.write("=" * 70 + "\n")
                f.write(f"Reporte generado: {TiempoUtils.obtener_tiempo_actual()}\n")
            
            return ruta_archivo
        except Exception as e:
            print(f"Error al exportar reporte: {e}")
            return None
    
    def limpiar_movimientos(self):
        """
        Limpia los movimientos del día (útil para nuevo día)
        """
        self.movimientos = []
        self.fecha_actual = TiempoUtils.obtener_fecha_actual()
    
    def hay_movimientos(self):
        """
        Verifica si hay movimientos registrados
        
        Returns:
            bool: True si hay al menos un movimiento
        """
        return len(self.movimientos) > 0