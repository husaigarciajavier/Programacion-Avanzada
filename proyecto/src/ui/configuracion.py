"""
Ventana de configuración del estacionamiento
Permite ajustar capacidad máxima y precio por hora
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import (
    MIN_CAPACIDAD, MAX_CAPACIDAD, MIN_PRECIO, MAX_PRECIO,
    COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO
)
from src.utils.config_manager import ConfigManager

class VentanaConfiguracion:
    """Ventana para configurar el estacionamiento"""
    
    def __init__(self, parent, estacionamiento, callback_actualizar=None):
        """
        Inicializa la ventana de configuración
        
        Args:
            parent: Ventana padre
            estacionamiento: Instancia de Estacionamiento
            callback_actualizar: Función a llamar cuando se actualice la config
        """
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.callback_actualizar = callback_actualizar
        self.config_manager = ConfigManager()
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Configuración del Estacionamiento")
        self.ventana.geometry("450x350")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        
        # Centrar ventana
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self._crear_widgets()
        self._cargar_valores_actuales()
    
    def _crear_widgets(self):
        """Crea los widgets de la ventana"""
        
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="⚙️ Configuración del Estacionamiento", 
                         font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        titulo.pack(pady=(0, 20))
        
        # Frame de capacidad
        frame_capacidad = tk.LabelFrame(main_frame, text="Capacidad del Estacionamiento", 
                                        bg=COLOR_FONDO, padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_capacidad.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_capacidad, text="Número máximo de vehículos:", 
                bg=COLOR_FONDO).pack(anchor=tk.W)
        
        self.capacidad_var = tk.IntVar()
        self.capacidad_spinbox = tk.Spinbox(frame_capacidad, from_=MIN_CAPACIDAD, to=MAX_CAPACIDAD,
                                            textvariable=self.capacidad_var, width=10, font=("Arial", 12))
        self.capacidad_spinbox.pack(anchor=tk.W, pady=(5, 0))
        
        # Label de advertencia
        self.advertencia_label = tk.Label(frame_capacidad, text="", 
                                          bg=COLOR_FONDO, fg="orange", font=("Arial", 8))
        self.advertencia_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Frame de precio
        frame_precio = tk.LabelFrame(main_frame, text="Tarifas", 
                                     bg=COLOR_FONDO, padx=10, pady=10, font=("Arial", 10, "bold"))
        frame_precio.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_precio, text="Precio por hora (MXN):", 
                bg=COLOR_FONDO).pack(anchor=tk.W)
        
        self.precio_var = tk.DoubleVar()
        self.precio_entry = tk.Entry(frame_precio, textvariable=self.precio_var, 
                                     width=15, font=("Arial", 12))
        self.precio_entry.pack(anchor=tk.W, pady=(5, 0))
        
        tk.Label(frame_precio, text=f"Rango permitido: ${MIN_PRECIO} - ${MAX_PRECIO}", 
                bg=COLOR_FONDO, font=("Arial", 8)).pack(anchor=tk.W, pady=(5, 0))
        
        # Frame de información
        frame_info = tk.LabelFrame(main_frame, text="Información Actual", 
                                   bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=4, width=40, font=("Arial", 9))
        self.info_text.pack()
        self.info_text.config(state=tk.DISABLED)
        
        # Botones
        frame_botones = tk.Frame(main_frame, bg=COLOR_FONDO)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        btn_guardar = tk.Button(frame_botones, text="💾 Guardar Cambios", 
                               bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                               command=self._guardar_configuracion)
        btn_guardar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", 
                                bg=COLOR_BOTON_INFO, fg="white",
                                command=self.ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT)
    
    def _cargar_valores_actuales(self):
        """Carga los valores actuales de configuración"""
        capacidad = self.estacionamiento.obtener_configuracion()['capacidad_maxima']
        precio = self.estacionamiento.obtener_precio_actual()
        activos = len(self.estacionamiento.obtener_vehiculos_activos())
        
        self.capacidad_var.set(capacidad)
        self.precio_var.set(precio)
        
        # Actualizar información
        info = f"Capacidad actual: {capacidad} lugares\n"
        info += f"Vehículos estacionados: {activos}\n"
        info += f"Espacios disponibles: {capacidad - activos}\n"
        info += f"Precio por hora: ${precio:.2f} MXN"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
        # Actualizar advertencia
        if capacidad - activos < 5:
            self.advertencia_label.config(text=f"⚠️ Solo quedan {capacidad - activos} espacios libres")
        else:
            self.advertencia_label.config(text="")
    
    def _guardar_configuracion(self):
        """Guarda la configuración y aplica cambios"""
        try:
            nueva_capacidad = self.capacidad_var.get()
            nuevo_precio = self.precio_var.get()
            
            # Validar precio
            if nuevo_precio < MIN_PRECIO or nuevo_precio > MAX_PRECIO:
                messagebox.showerror("Error", f"El precio debe estar entre ${MIN_PRECIO} y ${MAX_PRECIO}")
                return
            
            # Actualizar capacidad (con validación de vehículos activos)
            activos = len(self.estacionamiento.obtener_vehiculos_activos())
            if nueva_capacidad < activos:
                messagebox.showerror("Error", f"No puedes reducir la capacidad a {nueva_capacidad} porque hay {activos} vehículos estacionados.\nPrimero retira los vehículos.")
                return
            
            # Actualizar capacidad
            exito_cap, msg_cap = self.estacionamiento.actualizar_capacidad(nueva_capacidad)
            if not exito_cap:
                messagebox.showerror("Error", msg_cap)
                return
            
            # Actualizar precio
            exito_precio, msg_precio = self.estacionamiento.actualizar_precio(nuevo_precio)
            if not exito_precio:
                messagebox.showerror("Error", msg_precio)
                return
            
            messagebox.showinfo("Éxito", f"Configuración actualizada:\n{msg_cap}\n{msg_precio}")
            
            # Actualizar información mostrada
            self._cargar_valores_actuales()
            
            # Llamar callback si existe
            if self.callback_actualizar:
                self.callback_actualizar()
            
            # Cerrar ventana después de guardar
            self.ventana.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa valores válidos")