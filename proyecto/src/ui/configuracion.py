"""
Ventana de configuración - Capacidad y precio
"""

import tkinter as tk
from tkinter import messagebox
from src.config.constants import (
    MIN_CAPACIDAD, MAX_CAPACIDAD, MIN_PRECIO, MAX_PRECIO,
    COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO
)


class VentanaConfiguracion:
    """Ventana para configurar capacidad y precio"""
    
    def __init__(self, parent, estacionamiento, callback_actualizar=None):
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.callback_actualizar = callback_actualizar
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("⚙️ Configuración")
        self.ventana.geometry("450x420")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.ventana.bind('<Return>', lambda e: self._guardar())
        self.ventana.bind('<Escape>', lambda e: self.ventana.destroy())
        
        self._crear_widgets()
        self._cargar_valores()
    
    def _crear_widgets(self):
        main = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="Configuración", font=("Arial", 14, "bold"), 
                bg=COLOR_FONDO).pack(pady=(0, 20))
        
        # Capacidad
        frame_cap = tk.LabelFrame(main, text="Capacidad", bg=COLOR_FONDO, padx=10, pady=10)
        frame_cap.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_cap, text="Máximo de vehículos:", bg=COLOR_FONDO).pack(anchor=tk.W)
        
        frame_spin = tk.Frame(frame_cap, bg=COLOR_FONDO)
        frame_spin.pack(anchor=tk.W, pady=5)
        
        self.capacidad_var = tk.StringVar(value="32")  # CAMBIADO: StringVar en lugar de IntVar
        self.spinbox = tk.Spinbox(frame_spin, from_=MIN_CAPACIDAD, to=MAX_CAPACIDAD,
                                  textvariable=self.capacidad_var, width=10, font=("Arial", 12))
        self.spinbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # NUEVO: Función segura para modificar capacidad
        def modificar_capacidad(delta):
            try:
                valor = int(self.capacidad_var.get()) if self.capacidad_var.get().strip() else MIN_CAPACIDAD
                nuevo = max(MIN_CAPACIDAD, min(MAX_CAPACIDAD, valor + delta))
                self.capacidad_var.set(str(nuevo))
            except ValueError:
                self.capacidad_var.set(str(MIN_CAPACIDAD))
        
        tk.Button(frame_spin, text="+10", width=4, command=lambda: modificar_capacidad(10)).pack(side=tk.LEFT, padx=2)
        tk.Button(frame_spin, text="-10", width=4, command=lambda: modificar_capacidad(-10)).pack(side=tk.LEFT, padx=2)
        
        # Precio
        frame_precio = tk.LabelFrame(main, text="Tarifa", bg=COLOR_FONDO, padx=10, pady=10)
        frame_precio.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_precio, text="Precio por hora (MXN):", bg=COLOR_FONDO).pack(anchor=tk.W)
        
        frame_precio_btns = tk.Frame(frame_precio, bg=COLOR_FONDO)
        frame_precio_btns.pack(anchor=tk.W, pady=5)
        
        self.precio_var = tk.StringVar(value="5.0")  # CAMBIADO: StringVar
        self.precio_entry = tk.Entry(frame_precio_btns, textvariable=self.precio_var, width=10, 
                                      font=("Arial", 12))
        self.precio_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # NUEVO: Función segura para modificar precio
        def modificar_precio(valor):
            self.precio_var.set(str(valor))
        
        for precio in [5, 10, 15]:
            tk.Button(frame_precio_btns, text=f"${precio}", width=4,
                     command=lambda p=precio: modificar_precio(p)).pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_precio, text=f"Rango: ${MIN_PRECIO} - ${MAX_PRECIO}", 
                bg=COLOR_FONDO, font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 0))
        
        # Información actual
        frame_info = tk.LabelFrame(main, text="Estado actual", bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=4, font=("Arial", 9))
        self.info_text.pack()
        self.info_text.config(state=tk.DISABLED)
        
        # Botones
        frame_btns = tk.Frame(main, bg=COLOR_FONDO)
        frame_btns.pack(fill=tk.X)
        
        tk.Button(frame_btns, text="💾 Guardar (Enter)", bg=COLOR_BOTON, fg="white",
                 command=self._guardar).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="❌ Cancelar (Esc)", bg=COLOR_BOTON_INFO, fg="white",
                 command=self.ventana.destroy).pack(side=tk.LEFT)
    
    def _cargar_valores(self):
        config = self.estacionamiento.obtener_configuracion()
        activos = config['vehiculos_activos']
        capacidad = config['capacidad_maxima']
        precio = self.estacionamiento.obtener_precio_actual()
        
        self.capacidad_var.set(str(capacidad))
        self.precio_var.set(str(precio))
        
        info = f"Capacidad: {capacidad} lugares\nVehículos: {activos}\nLibres: {capacidad - activos}"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def _guardar(self):
        try:
            # Obtener y validar capacidad
            capacidad_str = self.capacidad_var.get().strip()
            if not capacidad_str:
                messagebox.showerror("Error", "Ingrese una capacidad válida")
                return
            
            nueva_capacidad = int(capacidad_str)
            
            # Obtener y validar precio
            precio_str = self.precio_var.get().strip()
            if not precio_str:
                messagebox.showerror("Error", "Ingrese un precio válido")
                return
            
            nuevo_precio = float(precio_str)
            
            # Validar rangos
            if nueva_capacidad < MIN_CAPACIDAD or nueva_capacidad > MAX_CAPACIDAD:
                messagebox.showerror("Error", f"Capacidad debe estar entre {MIN_CAPACIDAD} y {MAX_CAPACIDAD}")
                return
            
            if nuevo_precio < MIN_PRECIO or nuevo_precio > MAX_PRECIO:
                messagebox.showerror("Error", f"Precio debe estar entre ${MIN_PRECIO} y ${MAX_PRECIO}")
                return
            
            # Validar que no se reduzca por debajo de vehículos activos
            activos = self.estacionamiento.total_vehiculos
            if nueva_capacidad < activos:
                messagebox.showerror("Error", f"Hay {activos} vehículos. Retírelos primero antes de reducir capacidad.")
                return
            
            # Actualizar capacidad
            exito, msg = self.estacionamiento.actualizar_capacidad(nueva_capacidad)
            if not exito:
                messagebox.showerror("Error", msg)
                return
            
            # Actualizar precio
            exito, msg = self.estacionamiento.actualizar_precio(nuevo_precio)
            if not exito:
                messagebox.showerror("Error", msg)
                return
            
            messagebox.showinfo("Éxito", f"Configuración guardada:\nCapacidad: {nueva_capacidad}\nPrecio: ${nuevo_precio:.2f}/hora")
            
            if self.callback_actualizar:
                self.callback_actualizar()
            
            self.ventana.destroy()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Valores inválidos.\nUse números enteros para capacidad y decimales para precio.\nError: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {e}")