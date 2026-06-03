"""
Clase Registro - Maneja el historial de movimientos del día
Guardado persistente en archivos por día
"""

import json
from datetime import datetime
from collections import deque
from pathlib import Path
from src.config.constants import LOGS_DIR
from src.utils.tiempo_utils import TiempoUtils


class RegistroMovimientos:
    """Clase para registrar y gestionar movimientos - Persistente por día"""
    
    def __init__(self):
        """
        Inicializa el registro de movimientos
        """
        self._fecha_actual = TiempoUtils.obtener_fecha_actual()
        self._movimientos = []  # Almacenar todos los movimientos del día
        self._total_ingresos_hoy = 0
        self._total_salidas_hoy = 0
        self._total_recaudado_hoy = 0.0
        
        # Cargar movimientos existentes de hoy si hay
        self._cargar_movimientos_hoy()
    
    # ==================== ARCHIVOS ====================
    
    def _obtener_ruta_archivo(self, fecha=None):
        """
        Obtiene la ruta del archivo para una fecha específica
        Formato: logs/movimientos_2026-06-03.json
        """
        if fecha is None:
            fecha = self._fecha_actual
        return LOGS_DIR / f"movimientos_{fecha}.json"
    
    def _cargar_movimientos_hoy(self):
        """Carga los movimientos del día desde el archivo JSON"""
        archivo = self._obtener_ruta_archivo()
        
        if archivo.exists():
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                
                self._movimientos = datos.get('movimientos', [])
                self._total_ingresos_hoy = datos.get('total_ingresos', 0)
                self._total_salidas_hoy = datos.get('total_salidas', 0)
                self._total_recaudado_hoy = datos.get('total_recaudado', 0.0)
                
                print(f"📂 Cargados {len(self._movimientos)} movimientos de {archivo.name}")
            except Exception as e:
                print(f"⚠️ Error al cargar movimientos: {e}")
                self._iniciar_dia_nuevo()
        else:
            self._iniciar_dia_nuevo()
    
    def _guardar_movimientos(self):
        """Guarda todos los movimientos del día en el archivo JSON"""
        archivo = self._obtener_ruta_archivo()
        
        datos = {
            'fecha': self._fecha_actual,
            'total_ingresos': self._total_ingresos_hoy,
            'total_salidas': self._total_salidas_hoy,
            'total_recaudado': self._total_recaudado_hoy,
            'movimientos': self._movimientos,
            'ultima_actualizacion': TiempoUtils.obtener_tiempo_actual()
        }
        
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error al guardar movimientos: {e}")
            return False
    
    def _iniciar_dia_nuevo(self):
        """Inicia un nuevo día (reinicia contadores)"""
        self._movimientos = []
        self._total_ingresos_hoy = 0
        self._total_salidas_hoy = 0
        self._total_recaudado_hoy = 0.0
        print(f"📅 Nuevo día: {self._fecha_actual}")
    
    def _verificar_cambio_dia(self):
        """Verifica si cambió el día y crea nuevo archivo"""
        fecha_nueva = TiempoUtils.obtener_fecha_actual()
        
        if fecha_nueva != self._fecha_actual:
            # Guardar el día anterior
            self._guardar_movimientos()
            
            # Cambiar al nuevo día
            self._fecha_actual = fecha_nueva
            self._iniciar_dia_nuevo()
            
            # Crear nuevo archivo vacío
            self._guardar_movimientos()
            print(f"📅 Cambio de día: {fecha_nueva}")
            
            return True
        return False
    
    # ==================== REGISTRO DE MOVIMIENTOS ====================
    
    def registrar_ingreso(self, placa, id_unico, espacios_disponibles):
        """
        Registra un ingreso en el historial
        """
        self._verificar_cambio_dia()
        
        movimiento = {
            'tipo': 'INGRESO',
            'fecha_hora': TiempoUtils.obtener_tiempo_actual(),
            'placa': placa.upper(),
            'id_unico': id_unico,
            'espacios_disponibles': espacios_disponibles
        }
        
        self._movimientos.append(movimiento)
        self._total_ingresos_hoy += 1
        
        # Guardar inmediatamente en archivo
        self._guardar_movimientos()
        
        # También guardar en TXT legible
        self._guardar_en_txt(movimiento)
        
        return True
    
    def registrar_salida(self, placa, id_unico, horas_estadia, total_pagado, espacios_disponibles):
        """
        Registra una salida en el historial
        """
        self._verificar_cambio_dia()
        
        movimiento = {
            'tipo': 'SALIDA',
            'fecha_hora': TiempoUtils.obtener_tiempo_actual(),
            'placa': placa.upper(),
            'id_unico': id_unico,
            'horas_estadia': round(horas_estadia, 2),
            'total_pagado': total_pagado,
            'espacios_disponibles': espacios_disponibles
        }
        
        self._movimientos.append(movimiento)
        self._total_salidas_hoy += 1
        self._total_recaudado_hoy += total_pagado
        
        # Guardar inmediatamente en archivo
        self._guardar_movimientos()
        
        # También guardar en TXT legible
        self._guardar_en_txt(movimiento)
        
        return True
    
    def _guardar_en_txt(self, movimiento):
        """
        Guarda el movimiento también en un archivo TXT legible
        (misma fecha, formato amigable)
        """
        archivo_txt = LOGS_DIR / f"movimientos_{self._fecha_actual}.txt"
        
        try:
            with open(archivo_txt, 'a', encoding='utf-8') as f:
                if movimiento['tipo'] == 'INGRESO':
                    linea = (f"[{movimiento['fecha_hora']}] INGRESO | "
                            f"Placa: {movimiento['placa']} | "
                            f"ID: {movimiento['id_unico']} | "
                            f"Libres: {movimiento['espacios_disponibles']}\n")
                else:
                    linea = (f"[{movimiento['fecha_hora']}] SALIDA | "
                            f"Placa: {movimiento['placa']} | "
                            f"ID: {movimiento['id_unico']} | "
                            f"Horas: {movimiento['horas_estadia']:.2f} | "
                            f"Total: ${movimiento['total_pagado']:.2f} | "
                            f"Libres: {movimiento['espacios_disponibles']}\n")
                
                f.write(linea)
        except Exception as e:
            print(f"⚠️ Error al guardar en TXT: {e}")
    
    # ==================== CONSULTAS ====================
    
    def obtener_movimientos_hoy(self):
        """Retorna todos los movimientos del día"""
        self._verificar_cambio_dia()
        return self._movimientos.copy()
    
    def obtener_ingresos_hoy(self):
        """Retorna solo los ingresos del día"""
        return [m for m in self._movimientos if m['tipo'] == 'INGRESO']
    
    def obtener_salidas_hoy(self):
        """Retorna solo las salidas del día"""
        return [m for m in self._movimientos if m['tipo'] == 'SALIDA']
    
    def obtener_movimientos_fecha(self, fecha):
        """
        Obtiene los movimientos de una fecha específica
        
        Args:
            fecha: str formato YYYY-MM-DD
        
        Returns:
            list: Movimientos de esa fecha
        """
        archivo = self._obtener_ruta_archivo(fecha)
        
        if not archivo.exists():
            return []
        
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            return datos.get('movimientos', [])
        except Exception:
            return []
    
    def listar_fechas_disponibles(self):
        """
        Lista todas las fechas con movimientos guardados
        
        Returns:
            list: Fechas disponibles
        """
        fechas = []
        for archivo in LOGS_DIR.glob("movimientos_*.json"):
            # Extraer fecha del nombre: movimientos_2026-06-03.json
            fecha = archivo.stem.replace("movimientos_", "")
            fechas.append(fecha)
        return sorted(fechas, reverse=True)
    
    # ==================== REPORTES ====================
    
    def exportar_reporte_diario(self, ruta_archivo=None):
        """
        Exporta un reporte completo del día a un archivo de texto
        """
        # Verificar cambio de día
        self._verificar_cambio_dia()
        
        # Si no hay movimientos, crear archivo con solo encabezado
        if ruta_archivo is None:
            ruta_archivo = LOGS_DIR / f"reporte_{self._fecha_actual}.txt"
        
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("=" * 70 + "\n")
                f.write(f"📊 REPORTE DE MOVIMIENTOS - {self._fecha_actual}\n")
                f.write("=" * 70 + "\n\n")
                
                # Resumen
                f.write("📈 RESUMEN DEL DÍA:\n")
                f.write("-" * 40 + "\n")
                f.write(f"  🚗 Ingresos: {self._total_ingresos_hoy}\n")
                f.write(f"  🚗 Salidas:  {self._total_salidas_hoy}\n")
                f.write(f"  💰 Recaudado: ${self._total_recaudado_hoy:.2f} MXN\n")
                if self._total_salidas_hoy > 0:
                    promedio = self._total_recaudado_hoy / self._total_salidas_hoy
                    f.write(f"  📊 Promedio por vehículo: ${promedio:.2f}\n")
                f.write("\n")
                
                # Detalle de movimientos
                f.write("📋 DETALLE DE MOVIMIENTOS:\n")
                f.write("-" * 40 + "\n\n")
                
                if not self._movimientos:
                    f.write("  No hay movimientos registrados hoy.\n\n")
                else:
                    for m in self._movimientos:
                        if m['tipo'] == 'INGRESO':
                            f.write(f"  [{m['fecha_hora']}] 🟢 INGRESO\n")
                            f.write(f"      Placa: {m['placa']}\n")
                            f.write(f"      ID: {m['id_unico']}\n")
                            f.write(f"      Espacios libres: {m['espacios_disponibles']}\n\n")
                        else:
                            f.write(f"  [{m['fecha_hora']}] 🔴 SALIDA\n")
                            f.write(f"      Placa: {m['placa']}\n")
                            f.write(f"      ID: {m['id_unico']}\n")
                            f.write(f"      Horas: {m['horas_estadia']:.2f}\n")
                            f.write(f"      Total: ${m['total_pagado']:.2f}\n")
                            f.write(f"      Espacios libres: {m['espacios_disponibles']}\n\n")
                
                # Pie
                f.write("=" * 70 + "\n")
                f.write(f"📅 Reporte generado: {TiempoUtils.obtener_tiempo_actual()}\n")
                f.write("=" * 70 + "\n")
            
            return str(ruta_archivo)
        except Exception as e:
            print(f"❌ Error al exportar reporte: {e}")
            return None
    
    # ==================== PROPIEDADES ====================
    
    @property
    def fecha_actual(self):
        return self._fecha_actual
    
    @property
    def total_movimientos_hoy(self):
        return len(self._movimientos)
    
    @property
    def total_ingresos_hoy(self):
        return self._total_ingresos_hoy
    
    @property
    def total_salidas_hoy(self):
        return self._total_salidas_hoy
    
    @property
    def total_recaudado_hoy(self):
        return self._total_recaudado_hoy
    
    @property
    def hay_movimientos(self):
        return len(self._movimientos) > 0
    
    # ==================== MANTENIMIENTO ====================
    
    def guardar_y_cerrar(self):
        """Guarda todos los datos antes de cerrar la aplicación"""
        self._guardar_movimientos()
        print(f"Datos guardados para {self._fecha_actual}")