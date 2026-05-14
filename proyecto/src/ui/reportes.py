"""
Ventana para generar reportes y archivos de texto
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO, MOVIMIENTOS_DIA_FILE, LOGS_DIR
from src.utils.tiempo_utils import TiempoUtils

class VentanaReportes:
    """Ventana para generar reportes de movimientos"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos):
        """
        Inicializa la ventana de reportes
        
        Args:
            parent: Ventana padre
            estacionamiento: Instancia de Estacionamiento
            registro_movimientos: Instancia de RegistroMovimientos
        """
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Reportes del Estacionamiento")
        self.ventana.geometry("600x550")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        
        # Centrar ventana
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self._crear_widgets()
        self._actualizar_info()
    
    def _crear_widgets(self):
        """Crea los widgets de la ventana"""
        
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="📊 Reportes y Estadísticas", 
                         font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        titulo.pack(pady=(0, 20))
        
        # Frame de información actual
        frame_info = tk.LabelFrame(main_frame, text="Información Actual", 
                                   bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=8, width=55, font=("Arial", 10))
        self.info_text.pack()
        self.info_text.config(state=tk.DISABLED)
        
        # Frame de movimientos del día
        frame_movimientos = tk.LabelFrame(main_frame, text="Movimientos del Día", 
                                          bg=COLOR_FONDO, padx=10, pady=10)
        frame_movimientos.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview para movimientos
        columns = ("Hora", "Tipo", "Placa", "ID", "Detalle")
        self.tree = ttk.Treeview(frame_movimientos, columns=columns, show="headings", height=8)
        
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Detalle", text="Detalle")
        
        self.tree.column("Hora", width=100)
        self.tree.column("Tipo", width=70)
        self.tree.column("Placa", width=80)
        self.tree.column("ID", width=120)
        self.tree.column("Detalle", width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_movimientos, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botones
        frame_botones = tk.Frame(main_frame, bg=COLOR_FONDO)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        btn_exportar_txt = tk.Button(frame_botones, text="📄 Exportar a TXT", 
                                    bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                                    command=self._exportar_reporte_txt)
        btn_exportar_txt.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_exportar_completo = tk.Button(frame_botones, text="📋 Exportar Reporte Completo", 
                                         bg=COLOR_BOTON_INFO, fg="white",
                                         command=self._exportar_reporte_completo)
        btn_exportar_completo.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_guardar_ubicacion = tk.Button(frame_botones, text="💾 Guardar en ubicación...", 
                                         bg=COLOR_BOTON_INFO, fg="white",
                                         command=self._guardar_en_ubicacion)
        btn_guardar_ubicacion.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_refrescar = tk.Button(frame_botones, text="🔄 Refrescar", 
                                 bg=COLOR_BOTON_INFO, fg="white",
                                 command=self._actualizar_info)
        btn_refrescar.pack(side=tk.LEFT)
        
        # Botón cerrar
        btn_cerrar = tk.Button(frame_botones, text="❌ Cerrar", 
                              bg="#f44336", fg="white",
                              command=self.ventana.destroy)
        btn_cerrar.pack(side=tk.RIGHT)
    
    def _actualizar_info(self):
        """Actualiza la información mostrada"""
        # Actualizar información del estacionamiento
        config = self.estacionamiento.obtener_configuracion()
        activos = config['vehiculos_activos']
        capacidad = config['capacidad_maxima']
        disponibles = config['espacios_disponibles']
        ocupacion = config['ocupacion']
        precio = config['precio_por_hora']
        
        # Calcular recaudación del día
        movimientos_hoy = self.registro_movimientos.obtener_movimientos_hoy()
        salidas_hoy = [m for m in movimientos_hoy if m['tipo'] == 'SALIDA']
        total_recaudado = sum([m.get('total_pagado', 0) for m in salidas_hoy])
        
        info = f"📊 ESTADO ACTUAL DEL ESTACIONAMIENTO\n"
        info += f"{'='*40}\n"
        info += f"🅿️ Capacidad total: {capacidad} lugares\n"
        info += f"🚗 Vehículos estacionados: {activos}\n"
        info += f"✅ Espacios disponibles: {disponibles}\n"
        info += f"📈 Ocupación: {ocupacion:.1f}%\n"
        info += f"💰 Tarifa actual: ${precio:.2f} por hora\n"
        info += f"{'='*40}\n"
        info += f"💵 Total recaudado hoy: ${total_recaudado:.2f} MXN\n"
        info += f"📝 Movimientos registrados hoy: {len(movimientos_hoy)}\n"
        info += f"   - Ingresos: {len([m for m in movimientos_hoy if m['tipo'] == 'INGRESO'])}\n"
        info += f"   - Salidas: {len(salidas_hoy)}"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
        # Actualizar lista de movimientos
        self._actualizar_lista_movimientos()
    
    def _actualizar_lista_movimientos(self):
        """Actualiza la lista de movimientos del día"""
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        movimientos = self.registro_movimientos.obtener_movimientos_hoy()
        
        if not movimientos:
            self.tree.insert("", tk.END, values=("---", "---", "No hay movimientos", "---", "---"))
            return
        
        for m in movimientos:
            hora = m['fecha_hora'].split()[1] if ' ' in m['fecha_hora'] else m['fecha_hora']
            
            if m['tipo'] == 'INGRESO':
                detalle = f"Espacios libres: {m['espacios_disponibles']}"
                self.tree.insert("", 0, values=(hora, "🚗 INGRESO", m['placa'], m['id_unico'][:12] + "...", detalle))
            else:
                detalle = f"{m['horas_estadia']:.1f}h - ${m['total_pagado']:.2f}"
                self.tree.insert("", 0, values=(hora, "💰 SALIDA", m['placa'], m['id_unico'][:12] + "...", detalle))
    
    def _exportar_reporte_txt(self):
        """Exporta el reporte del día a un archivo TXT"""
        if not self.registro_movimientos.hay_movimientos():
            messagebox.showwarning("Advertencia", "No hay movimientos registrados hoy para exportar")
            return
        
        # Usar la función existente de RegistroMovimientos
        ruta = self.registro_movimientos.exportar_reporte_diario()
        
        if ruta:
            messagebox.showinfo("Éxito", f"✅ Reporte exportado correctamente\n\n📁 Ubicación: {ruta}")
        else:
            messagebox.showerror("Error", "No se pudo exportar el reporte")
    
    def _exportar_reporte_completo(self):
        """Exporta un reporte completo con estadísticas detalladas"""
        if not self.registro_movimientos.hay_movimientos():
            messagebox.showwarning("Advertencia", "No hay movimientos registrados hoy para exportar")
            return
        
        try:
            # Crear archivo con fecha
            fecha = TiempoUtils.obtener_fecha_actual()
            nombre_archivo = f"reporte_completo_{fecha}.txt"
            ruta_archivo = LOGS_DIR / nombre_archivo
            
            movimientos = self.registro_movimientos.obtener_movimientos_hoy()
            ingresos = [m for m in movimientos if m['tipo'] == 'INGRESO']
            salidas = [m for m in movimientos if m['tipo'] == 'SALIDA']
            total_recaudado = sum([m.get('total_pagado', 0) for m in salidas])
            
            config = self.estacionamiento.obtener_configuracion()
            
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                # Encabezado
                f.write("=" * 80 + "\n")
                f.write(f"REPORTE COMPLETO DEL ESTACIONAMIENTO\n")
                f.write(f"Fecha: {fecha}\n")
                f.write(f"Hora de generación: {TiempoUtils.obtener_tiempo_actual()}\n")
                f.write("=" * 80 + "\n\n")
                
                # Resumen ejecutivo
                f.write("RESUMEN EJECUTIVO\n")
                f.write("-" * 40 + "\n")
                f.write(f"Capacidad del estacionamiento: {config['capacidad_maxima']} lugares\n")
                f.write(f"Vehículos actualmente estacionados: {config['vehiculos_activos']}\n")
                f.write(f"Espacios disponibles: {config['espacios_disponibles']}\n")
                f.write(f"Ocupación: {config['ocupacion']:.1f}%\n")
                f.write(f"Tarifa por hora: ${config['precio_por_hora']:.2f} MXN\n")
                f.write("\n")
                
                # Estadísticas del día
                f.write("ESTADÍSTICAS DEL DÍA\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total de ingresos: {len(ingresos)}\n")
                f.write(f"Total de salidas: {len(salidas)}\n")
                f.write(f"Total recaudado: ${total_recaudado:.2f} MXN\n")
                f.write(f"Promedio por vehículo: ${total_recaudado/len(salidas) if salidas else 0:.2f} MXN\n")
                f.write("\n")
                
                # Detalle de movimientos
                f.write("DETALLE DE MOVIMIENTOS\n")
                f.write("-" * 40 + "\n\n")
                
                for m in movimientos:
                    if m['tipo'] == 'INGRESO':
                        f.write(f"[{m['fecha_hora']}] INGRESO\n")
                        f.write(f"  Placa: {m['placa']}\n")
                        f.write(f"  ID: {m['id_unico']}\n")
                        f.write(f"  Espacios disponibles después: {m['espacios_disponibles']}\n\n")
                    else:
                        f.write(f"[{m['fecha_hora']}] SALIDA\n")
                        f.write(f"  Placa: {m['placa']}\n")
                        f.write(f"  ID: {m['id_unico']}\n")
                        f.write(f"  Horas de estadía: {m['horas_estadia']:.2f}\n")
                        f.write(f"  Total pagado: ${m['total_pagado']:.2f}\n")
                        f.write(f"  Espacios disponibles después: {m['espacios_disponibles']}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("Fin del reporte\n")
            
            messagebox.showinfo("Éxito", f"✅ Reporte completo exportado correctamente\n\n📁 Ubicación: {ruta_archivo}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el reporte:\n{str(e)}")
    
    def _guardar_en_ubicacion(self):
        """Permite al usuario elegir dónde guardar el reporte"""
        if not self.registro_movimientos.hay_movimientos():
            messagebox.showwarning("Advertencia", "No hay movimientos registrados hoy para exportar")
            return
        
        # Abrir diálogo para elegir ubicación
        fecha = TiempoUtils.obtener_fecha_actual()
        nombre_default = f"reporte_estacionamiento_{fecha}.txt"
        
        ruta = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            initialfile=nombre_default,
            title="Guardar reporte como..."
        )
        
        if ruta:
            # Exportar en la ubicación seleccionada
            resultado = self.registro_movimientos.exportar_reporte_diario(ruta)
            if resultado:
                messagebox.showinfo("Éxito", f"✅ Reporte guardado en:\n{ruta}")
            else:
                messagebox.showerror("Error", "No se pudo guardar el reporte")