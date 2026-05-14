"""
Ventana para registrar ingreso de vehículos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_INFO

class VentanaRegistroVehiculo:
    """Ventana para registrar el ingreso de un nuevo vehículo"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos, callback_actualizar=None):
        """
        Inicializa la ventana de registro
        
        Args:
            parent: Ventana padre
            estacionamiento: Instancia de Estacionamiento
            registro_movimientos: Instancia de RegistroMovimientos
            callback_actualizar: Función a llamar después de registrar
        """
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        self.callback_actualizar = callback_actualizar
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Registrar Ingreso de Vehículo")
        self.ventana.geometry("450x400")
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
        titulo = tk.Label(main_frame, text="🚗 Registro de Ingreso", 
                         font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        titulo.pack(pady=(0, 20))
        
        # Frame de información del estacionamiento
        frame_info = tk.LabelFrame(main_frame, text="Estado del Estacionamiento", 
                                   bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.ocupacion_label = tk.Label(frame_info, text="", bg=COLOR_FONDO, font=("Arial", 10))
        self.ocupacion_label.pack(anchor=tk.W)
        
        self.espacios_label = tk.Label(frame_info, text="", bg=COLOR_FONDO, font=("Arial", 10))
        self.espacios_label.pack(anchor=tk.W)
        
        self.precio_label = tk.Label(frame_info, text="", bg=COLOR_FONDO, font=("Arial", 10))
        self.precio_label.pack(anchor=tk.W)
        
        # Frame de ingreso de placa
        frame_placa = tk.LabelFrame(main_frame, text="Datos del Vehículo", 
                                    bg=COLOR_FONDO, padx=10, pady=10)
        frame_placa.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame_placa, text="Número de Placa:", 
                bg=COLOR_FONDO, font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.placa_var = tk.StringVar()
        self.placa_entry = tk.Entry(frame_placa, textvariable=self.placa_var, 
                                    font=("Arial", 14), width=15, justify='center')
        self.placa_entry.pack(pady=(5, 10))
        self.placa_entry.focus()
        
        # Convertir a mayúsculas automáticamente
        self.placa_var.trace('w', lambda *args: self.placa_var.set(self.placa_var.get().upper()))
        
        # Ejemplo de formato
        tk.Label(frame_placa, text="Ejemplo: ABC123", 
                bg=COLOR_FONDO, font=("Arial", 8, "italic")).pack()
        
        # Frame de ID generado
        frame_id = tk.LabelFrame(main_frame, text="ID Generado (Automático)", 
                                 bg=COLOR_FONDO, padx=10, pady=10)
        frame_id.pack(fill=tk.X, pady=(0, 15))
        
        self.id_generado_label = tk.Label(frame_id, text="---", 
                                          bg="white", font=("Arial", 10, "bold"), 
                                          relief=tk.SUNKEN, padx=5, pady=5)
        self.id_generado_label.pack(fill=tk.X)
        
        # Botones
        frame_botones = tk.Frame(main_frame, bg=COLOR_FONDO)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        btn_registrar = tk.Button(frame_botones, text="✅ Registrar Ingreso", 
                                 bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                                 command=self._registrar_ingreso)
        btn_registrar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", 
                                bg=COLOR_BOTON_INFO, fg="white",
                                command=self.ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT)
        
        # Atajo de teclado Enter
        self.ventana.bind('<Return>', lambda e: self._registrar_ingreso())
    
    def _actualizar_info(self):
        """Actualiza la información del estacionamiento"""
        config = self.estacionamiento.obtener_configuracion()
        activos = config['vehiculos_activos']
        capacidad = config['capacidad_maxima']
        disponibles = config['espacios_disponibles']
        precio = config['precio_por_hora']
        ocupacion = config['ocupacion']
        
        self.ocupacion_label.config(text=f"📊 Ocupación: {activos}/{capacidad} vehículos ({ocupacion:.1f}%)")
        self.espacios_label.config(text=f"🅿️ Espacios disponibles: {disponibles}")
        self.precio_label.config(text=f"💰 Tarifa: ${precio:.2f} por hora")
        
        # Cambiar color según ocupación
        if ocupacion > 80:
            self.ocupacion_label.config(fg="red")
        elif ocupacion > 50:
            self.ocupacion_label.config(fg="orange")
        else:
            self.ocupacion_label.config(fg="green")
    
    def _registrar_ingreso(self):
        """Registra el ingreso del vehículo"""
        placa = self.placa_var.get().strip()
        
        if not placa:
            messagebox.showwarning("Advertencia", "Por favor ingresa la placa del vehículo")
            self.placa_entry.focus()
            return
        
        # Registrar ingreso
        exito, mensaje, vehiculo = self.estacionamiento.registrar_ingreso(placa)
        
        if exito:
            # Mostrar ID generado
            self.id_generado_label.config(text=vehiculo.id_unico)
            
            # Registrar en movimientos del día
            espacios_disponibles = self.estacionamiento.obtener_espacios_disponibles()
            self.registro_movimientos.registrar_ingreso(
                placa, 
                vehiculo.id_unico, 
                espacios_disponibles
            )
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", 
                               f"✅ Vehículo registrado correctamente\n\n"
                               f"🚗 Placa: {placa}\n"
                               f"🆔 ID: {vehiculo.id_unico}\n"
                               f"⏰ Hora ingreso: {vehiculo.hora_ingreso}\n\n"
                               f"Espacios disponibles: {espacios_disponibles}")
            
            # Actualizar callback
            if self.callback_actualizar:
                self.callback_actualizar()
            
            # Limpiar campos para próximo registro
            self.placa_var.set("")
            self.placa_entry.focus()
            self.id_generado_label.config(text="---")
            
            # Actualizar información
            self._actualizar_info()
        else:
            messagebox.showerror("Error", f"❌ No se pudo registrar el vehículo\n\n{mensaje}")
    
    def _generar_id_ejemplo(self):
        """Genera un ID de ejemplo (solo para mostrar)"""
        from src.utils.id_generator import GeneradorID
        ejemplo = GeneradorID.generar_id_corto()
        self.id_generado_label.config(text=f"Ejemplo: {ejemplo}")