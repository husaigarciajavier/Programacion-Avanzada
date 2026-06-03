"""
Ventana para registrar ingreso de vehículos
"""

import tkinter as tk
from tkinter import messagebox
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO


class VentanaRegistroVehiculo:
    """Ventana para registrar ingreso"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos, callback_actualizar=None):
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        self.callback_actualizar = callback_actualizar
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Registrar Ingreso")
        self.ventana.geometry("400x400")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.ventana.bind('<Return>', lambda e: self._registrar())
        self.ventana.bind('<Escape>', lambda e: self.ventana.destroy())
        
        self._crear_widgets()
        self._actualizar_info()
    
    def _crear_widgets(self):
        main = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="Registrar Ingreso", font=("Arial", 14, "bold"), 
                bg=COLOR_FONDO).pack(pady=(0, 20))
        
        # Estado del estacionamiento
        frame_info = tk.LabelFrame(main, text="Estado", bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.ocupacion_label = tk.Label(frame_info, text="", bg=COLOR_FONDO)
        self.ocupacion_label.pack(anchor=tk.W)
        self.espacios_label = tk.Label(frame_info, text="", bg=COLOR_FONDO)
        self.espacios_label.pack(anchor=tk.W)
        self.precio_label = tk.Label(frame_info, text="", bg=COLOR_FONDO)
        self.precio_label.pack(anchor=tk.W)
        
        # Datos del vehículo
        frame_placa = tk.LabelFrame(main, text="Vehículo", bg=COLOR_FONDO, padx=10, pady=10)
        frame_placa.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_placa, text="Placa:", font=("Arial", 10, "bold"), 
                bg=COLOR_FONDO).pack(anchor=tk.W)
        
        self.placa_var = tk.StringVar()
        self.placa_entry = tk.Entry(frame_placa, textvariable=self.placa_var, 
                                    font=("Arial", 14), width=15, justify='center')
        self.placa_entry.pack(pady=5)
        self.placa_var.trace('w', lambda *args: self.placa_var.set(self.placa_var.get().upper()))
        self.placa_entry.focus()
        
        tk.Label(frame_placa, text="Ejemplo: ABC123", bg=COLOR_FONDO, 
                font=("Arial", 8, "italic")).pack()
        
        # ID generado
        frame_id = tk.LabelFrame(main, text="ID generado", bg=COLOR_FONDO, padx=10, pady=10)
        frame_id.pack(fill=tk.X, pady=(0, 15))
        
        self.id_label = tk.Label(frame_id, text="---", bg="white", font=("Arial", 10, "bold"),
                                 relief=tk.SUNKEN, padx=5, pady=5)
        self.id_label.pack(fill=tk.X)
        
        # Botones
        frame_btns = tk.Frame(main, bg=COLOR_FONDO)
        frame_btns.pack(fill=tk.X)
        
        tk.Button(frame_btns, text="✅ Registrar (Enter)", bg=COLOR_BOTON, fg="white",
                 command=self._registrar).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="❌ Cancelar (Esc)", bg=COLOR_BOTON_INFO, fg="white",
                 command=self.ventana.destroy).pack(side=tk.LEFT)
    
    def _actualizar_info(self):
        config = self.estacionamiento.obtener_configuracion()
        self.ocupacion_label.config(text=f"Ocupación: {config['vehiculos_activos']}/{config['capacidad_maxima']}")
        self.espacios_label.config(text=f"Libres: {config['espacios_disponibles']}")
        self.precio_label.config(text=f"Tarifa: ${config['precio_por_hora']:.2f}/hora")
    
    def _registrar(self):
        placa = self.placa_var.get().strip()
        if not placa:
            messagebox.showwarning("Advertencia", "Ingrese la placa")
            return
        
        exito, mensaje, vehiculo = self.estacionamiento.registrar_ingreso(placa)
        
        if exito:
            self.id_label.config(text=vehiculo.id_unico)
            self.registro_movimientos.registrar_ingreso(placa, vehiculo.id_unico, 
                                                        self.estacionamiento.espacios_disponibles)
            messagebox.showinfo("Éxito", f"Vehículo {placa} registrado\nID: {vehiculo.id_unico}")
            
            if self.callback_actualizar:
                self.callback_actualizar()
            
            self.placa_var.set("")
            self.id_label.config(text="---")
            self.placa_entry.focus()
            self._actualizar_info()
        else:
            messagebox.showerror("Error", mensaje)