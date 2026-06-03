"""
Ventana principal del sistema de estacionamiento
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import (
    VENTANA_TITULO, VENTANA_SIZE, COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO
)
from src.models.estacionamiento import Estacionamiento
from src.models.registro import RegistroMovimientos
from src.database import DatabaseManager
from src.ui.registro_vehiculo import VentanaRegistroVehiculo
from src.ui.pago_vehiculo import VentanaPagoVehiculo
from src.ui.reportes import VentanaReportes
from src.ui.configuracion import VentanaConfiguracion


class VentanaPrincipal:
    """Ventana principal del sistema"""
    
    def __init__(self):
        self.estacionamiento = Estacionamiento()
        self.registro_movimientos = RegistroMovimientos()
        self.db_manager = DatabaseManager()
        
        self.db_manager.cargar_vehiculos_activos(self.estacionamiento)
        
        self.ventana = tk.Tk()
        self.ventana.title(VENTANA_TITULO)
        self.ventana.geometry(VENTANA_SIZE)
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar)
        
        self._crear_menu()
        self._crear_widgets()
        self._actualizar()
        
        self.ventana.after(30000, self._actualizar)
    
    def _crear_menu(self):
        menubar = tk.Menu(self.ventana)
        self.ventana.config(menu=menubar)
        
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="💾 Guardar ahora", command=self._guardar)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="❌ Salir", command=self._cerrar)
        
        menu_operaciones = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🚗 Operaciones", menu=menu_operaciones)
        menu_operaciones.add_command(label="Registrar Ingreso", command=self._abrir_registro)
        menu_operaciones.add_command(label="Registrar Salida", command=self._abrir_pago)
        menu_operaciones.add_separator()
        menu_operaciones.add_command(label="Configuración", command=self._abrir_config)
        
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Reportes", menu=menu_reportes)
        menu_reportes.add_command(label="Ver Reportes", command=self._abrir_reportes)
        
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="ℹ️ Acerca de", command=self._acerca_de)
    
    def _crear_widgets(self):
        main = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="Sistema de Estacionamiento", font=("Arial", 18, "bold"), 
                bg=COLOR_FONDO).pack(pady=(0, 20))
        
        # Panel de información
        frame_info = tk.LabelFrame(main, text="Estado actual", bg=COLOR_FONDO, padx=15, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_labels = {}
        items = [(" Capacidad:", "cap"), (" Vehículos:", "act"), (" Libres:", "lib"),
                 (" Ocupación:", "ocu"), (" Tarifa:", "pre"), (" Recaudación:", "rec")]
        
        for i, (texto, key) in enumerate(items):
            row, col = i // 2, (i % 2) * 2
            tk.Label(frame_info, text=texto, bg=COLOR_FONDO, font=("Arial", 10, "bold")).grid(
                row=row, column=col, sticky=tk.W, padx=10, pady=5)
            self.info_labels[key] = tk.Label(frame_info, text="---", bg=COLOR_FONDO, font=("Arial", 10))
            self.info_labels[key].grid(row=row, column=col+1, sticky=tk.W, padx=10, pady=5)
        
        # Lista de vehículos
        frame_vehiculos = tk.LabelFrame(main, text="Vehículos estacionados", bg=COLOR_FONDO, padx=10, pady=10)
        frame_vehiculos.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        columns = ("ID", "Placa", "Ingreso", "Tiempo")
        self.tree = ttk.Treeview(frame_vehiculos, columns=columns, show="headings", height=8)
        
        for col, width in zip(columns, [150, 80, 130, 120]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        scroll = ttk.Scrollbar(frame_vehiculos, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        frame_btns = tk.Frame(main, bg=COLOR_FONDO)
        frame_btns.pack(fill=tk.X)
        
        tk.Button(frame_btns, text="✅ Registrar Ingreso", bg=COLOR_BOTON, fg="white",
                 command=self._abrir_registro).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="Registrar Salida", bg=COLOR_BOTON_INFO, fg="white",
                 command=self._abrir_pago).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="📊 Reportes", bg=COLOR_BOTON_INFO, fg="white",
                 command=self._abrir_reportes).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="⚙️ Configuración", bg=COLOR_BOTON_INFO, fg="white",
                 command=self._abrir_config).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="🔄 Refrescar", command=self._actualizar).pack(side=tk.LEFT)
        
        # Barra de estado
        self.status_bar = tk.Label(self.ventana, text="Sistema listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _actualizar(self):
        config = self.estacionamiento.obtener_configuracion()
        movimientos = self.registro_movimientos.obtener_movimientos_hoy()
        salidas = [m for m in movimientos if m['tipo'] == 'SALIDA']
        total = sum(m.get('total_pagado', 0) for m in salidas)
        
        self.info_labels['cap'].config(text=f"{config['capacidad_maxima']}")
        self.info_labels['act'].config(text=f"{config['vehiculos_activos']}")
        self.info_labels['lib'].config(text=f"{config['espacios_disponibles']}")
        self.info_labels['ocu'].config(text=f"{config['ocupacion']:.1f}%")
        self.info_labels['pre'].config(text=f"${config['precio_por_hora']:.2f}")
        self.info_labels['rec'].config(text=f"${total:.2f}")
        
        # Actualizar lista
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for v in self.estacionamiento.vehiculos_activos:
            self.tree.insert("", tk.END, values=(v.id_unico[:12] + "...", v.placa, v.hora_ingreso, v.tiempo_formateado))
        
        self.status_bar.config(text=f"Actualizado: {self._hora()} | Libres: {config['espacios_disponibles']}")
        self.ventana.after(30000, self._actualizar)
    
    def _hora(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _guardar(self):
        self.db_manager.guardar_estado_completo(self.estacionamiento, self.registro_movimientos)
        messagebox.showinfo("Guardado", "Datos guardados correctamente")
    
    def _cerrar(self):
        if messagebox.askyesno("Salir", "¿Guardar datos antes de salir?"):
            self._guardar()
        self.ventana.quit()
        self.ventana.destroy()
    
    def _abrir_registro(self):
        VentanaRegistroVehiculo(self.ventana, self.estacionamiento, self.registro_movimientos, self._actualizar)
    
    def _abrir_pago(self):
        VentanaPagoVehiculo(self.ventana, self.estacionamiento, self.registro_movimientos, self._actualizar)
    
    def _abrir_reportes(self):
        VentanaReportes(self.ventana, self.estacionamiento, self.registro_movimientos)
    
    def _abrir_config(self):
        VentanaConfiguracion(self.ventana, self.estacionamiento, self._actualizar)
    
    def _acerca_de(self):
        messagebox.showinfo("Acerca de", "Sistema de Estacionamiento v1.0\nDesarrollado para Programación Avanzada")
    
    def ejecutar(self):
        self.ventana.mainloop()