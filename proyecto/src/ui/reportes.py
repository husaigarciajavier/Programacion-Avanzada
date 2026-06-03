"""
Ventana de reportes y estadísticas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO
from src.utils.tiempo_utils import TiempoUtils


class VentanaReportes:
    """Ventana para generar reportes"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos):
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("📊 Reportes")
        self.ventana.geometry("650x550")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self._crear_widgets()
        self._actualizar()
    
    def _crear_widgets(self):
        main = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="📊 Reportes", font=("Arial", 14, "bold"), 
                bg=COLOR_FONDO).pack(pady=(0, 20))
        
        # Información actual
        frame_info = tk.LabelFrame(main, text="Estado actual", bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=6, font=("Arial", 10))
        self.info_text.pack()
        self.info_text.config(state=tk.DISABLED)
        
        # Movimientos del día
        frame_mov = tk.LabelFrame(main, text="Movimientos del día", bg=COLOR_FONDO, padx=10, pady=10)
        frame_mov.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        columns = ("Hora", "Tipo", "Placa", "Detalle")
        self.tree = ttk.Treeview(frame_mov, columns=columns, show="headings", height=8)
        
        for col, width in zip(columns, [100, 80, 100, 200]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scroll = ttk.Scrollbar(frame_mov, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        frame_btns = tk.Frame(main, bg=COLOR_FONDO)
        frame_btns.pack(fill=tk.X)
        
        tk.Button(frame_btns, text="Exportar a TXT", bg=COLOR_BOTON, fg="white",
                 command=self._exportar).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="Refrescar", bg=COLOR_BOTON_INFO, fg="white",
                 command=self._actualizar).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="❌ Cerrar", bg=COLOR_BOTON_INFO, fg="white",
                 command=self.ventana.destroy).pack(side=tk.LEFT)
    
    def _actualizar(self):
        config = self.estacionamiento.obtener_configuracion()
        movimientos = self.registro_movimientos.obtener_movimientos_hoy()
        salidas = [m for m in movimientos if m['tipo'] == 'SALIDA']
        total = sum(m.get('total_pagado', 0) for m in salidas)
        
        info = f"Capacidad: {config['capacidad_maxima']}\n"
        info += f"Ocupación: {config['vehiculos_activos']}/{config['capacidad_maxima']}\n"
        info += f"Libres: {config['espacios_disponibles']}\n"
        info += f"Recaudado hoy: ${total:.2f}\n"
        info += f"Movimientos: {len(movimientos)}"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
        # Actualizar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for m in movimientos[-20:]:
            hora = m['fecha_hora'].split()[1] if ' ' in m['fecha_hora'] else m['fecha_hora']
            if m['tipo'] == 'INGRESO':
                self.tree.insert("", 0, values=(hora, "INGRESO", m['placa'], f"Libres: {m['espacios_disponibles']}"))
            else:
                self.tree.insert("", 0, values=(hora, "SALIDA", m['placa'], f"${m['total_pagado']:.2f}"))
    
    def _exportar(self):
        if not self.registro_movimientos.hay_movimientos:
            messagebox.showwarning("Advertencia", "No hay movimientos para exportar")
            return
        
        ruta = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if ruta:
            resultado = self.registro_movimientos.exportar_reporte_diario(ruta)
            if resultado:
                messagebox.showinfo("Éxito", f"Reporte guardado en:\n{ruta}")