"""
Ventana para procesar pago y salida de vehículos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_PELIGRO, COLOR_BOTON_INFO
from src.utils.tiempo_utils import TiempoUtils
from src.utils.precio_utils import PrecioUtils

class VentanaPagoVehiculo:
    """Ventana para procesar la salida y pago de un vehículo"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos, callback_actualizar=None):
        """
        Inicializa la ventana de pago
        
        Args:
            parent: Ventana padre
            estacionamiento: Instancia de Estacionamiento
            registro_movimientos: Instancia de RegistroMovimientos
            callback_actualizar: Función a llamar después del pago
        """
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        self.callback_actualizar = callback_actualizar
        self.vehiculo_seleccionado = None
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Registrar Salida y Pago")
        self.ventana.geometry("550x600")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        
        # Centrar ventana
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self._crear_widgets()
        self._actualizar_lista_vehiculos()
    
    def _crear_widgets(self):
        """Crea los widgets de la ventana"""
        
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="💰 Registro de Salida y Pago", 
                         font=("Arial", 14, "bold"), bg=COLOR_FONDO)
        titulo.pack(pady=(0, 20))
        
        # Frame de lista de vehículos
        frame_lista = tk.LabelFrame(main_frame, text="Vehículos Estacionados", 
                                    bg=COLOR_FONDO, padx=10, pady=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview para mostrar vehículos
        columns = ("ID", "Placa", "Ingreso", "Tiempo")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=8)
        
        self.tree.heading("ID", text="ID Vehículo")
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("Ingreso", text="Hora Ingreso")
        self.tree.heading("Tiempo", text="Tiempo Actual")
        
        self.tree.column("ID", width=120)
        self.tree.column("Placa", width=80)
        self.tree.column("Ingreso", width=130)
        self.tree.column("Tiempo", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selección
        self.tree.bind('<<TreeviewSelect>>', self._on_vehiculo_seleccionado)
        
        # Frame de información del vehículo seleccionado
        frame_info = tk.LabelFrame(main_frame, text="Información del Vehículo Seleccionado", 
                                   bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=6, width=50, font=("Arial", 9))
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        # Frame de cálculo de pago
        frame_pago = tk.LabelFrame(main_frame, text="Cálculo de Pago", 
                                   bg=COLOR_FONDO, padx=10, pady=10)
        frame_pago.pack(fill=tk.X, pady=(0, 15))
        
        # Precio por hora
        precio_actual = self.estacionamiento.obtener_precio_actual()
        tk.Label(frame_pago, text=f"Tarifa actual: ${precio_actual:.2f} por hora", 
                bg=COLOR_FONDO, font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Frame de resultado
        frame_resultado = tk.Frame(frame_pago, bg=COLOR_FONDO)
        frame_resultado.pack(fill=tk.X, pady=(10, 0))
        
        self.total_label = tk.Label(frame_resultado, text="", 
                                   bg=COLOR_FONDO, font=("Arial", 14, "bold"), fg="green")
        self.total_label.pack()
        
        # Botones
        frame_botones = tk.Frame(main_frame, bg=COLOR_FONDO)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        self.btn_procesar = tk.Button(frame_botones, text="💵 Procesar Pago y Salida", 
                                     bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                                     command=self._procesar_pago, state=tk.DISABLED)
        self.btn_procesar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_actualizar = tk.Button(frame_botones, text="🔄 Actualizar Lista", 
                                  bg=COLOR_BOTON_INFO, fg="white",
                                  command=self._actualizar_lista_vehiculos)
        btn_actualizar.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_cancelar = tk.Button(frame_botones, text="❌ Cancelar", 
                                bg=COLOR_BOTON_PELIGRO, fg="white",
                                command=self.ventana.destroy)
        btn_cancelar.pack(side=tk.LEFT)
        
        # Actualizar tiempos cada minuto
        self._actualizar_tiempos()
    
    def _actualizar_lista_vehiculos(self):
        """Actualiza la lista de vehículos estacionados"""
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener vehículos activos
        vehiculos = self.estacionamiento.obtener_vehiculos_activos()
        
        if not vehiculos:
            self.tree.insert("", tk.END, values=("---", "No hay vehículos", "---", "---"))
            self.btn_procesar.config(state=tk.DISABLED)
            return
        
        for v in vehiculos:
            tiempo_actual = v.obtener_tiempo_formateado()
            self.tree.insert("", tk.END, values=(v.id_unico[:12] + "...", v.placa, v.hora_ingreso, tiempo_actual))
        
        self.btn_procesar.config(state=tk.NORMAL if self.vehiculo_seleccionado else tk.DISABLED)
    
    def _actualizar_tiempos(self):
        """Actualiza los tiempos mostrados en la lista"""
        for idx, item in enumerate(self.tree.get_children()):
            valores = self.tree.item(item, "values")
            if valores and valores[0] != "---":
                # Buscar el vehículo por placa (primeros caracteres)
                vehiculos = self.estacionamiento.obtener_vehiculos_activos()
                for v in vehiculos:
                    if v.placa == valores[1]:
                        tiempo_actual = v.obtener_tiempo_formateado()
                        self.tree.item(item, values=(valores[0], valores[1], valores[2], tiempo_actual))
                        break
        
        # Actualizar info del vehículo seleccionado si existe
        if self.vehiculo_seleccionado:
            self._actualizar_info_vehiculo(self.vehiculo_seleccionado)
        
        # Programar próxima actualización (cada 30 segundos)
        self.ventana.after(30000, self._actualizar_tiempos)
    
    def _on_vehiculo_seleccionado(self, event):
        """Maneja la selección de un vehículo de la lista"""
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        valores = self.tree.item(seleccion[0], "values")
        if valores[0] == "---":
            return
        
        # Buscar el vehículo completo por placa
        placa = valores[1]
        self.vehiculo_seleccionado = self.estacionamiento.buscar_vehiculo_por_placa(placa)
        
        if self.vehiculo_seleccionado:
            self._actualizar_info_vehiculo(self.vehiculo_seleccionado)
            self.btn_procesar.config(state=tk.NORMAL)
    
    def _actualizar_info_vehiculo(self, vehiculo):
        """Actualiza la información mostrada del vehículo seleccionado"""
        horas = vehiculo.obtener_duracion()
        tiempo_formateado = vehiculo.obtener_tiempo_formateado()
        precio_actual = self.estacionamiento.obtener_precio_actual()
        total_estimado = TiempoUtils.calcular_total_a_pagar(horas, precio_actual)
        
        info = f"🆔 ID: {vehiculo.id_unico}\n"
        info += f"🚗 Placa: {vehiculo.placa}\n"
        info += f"⏰ Hora de ingreso: {vehiculo.hora_ingreso}\n"
        info += f"⏱️ Tiempo estacionado: {tiempo_formateado} ({horas:.2f} horas)\n"
        info += f"💰 Tarifa: ${precio_actual:.2f}/hora\n"
        info += f"{'='*40}\n"
        info += f"💵 TOTAL ESTIMADO: ${total_estimado:.2f} MXN"
        
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
        
        self.total_label.config(text=f"Total a pagar: ${total_estimado:.2f} MXN")
    
    def _procesar_pago(self):
        """Procesa el pago y registra la salida del vehículo"""
        if not self.vehiculo_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor selecciona un vehículo")
            return
        
        # Confirmar con el usuario
        horas = self.vehiculo_seleccionado.obtener_duracion()
        precio = self.estacionamiento.obtener_precio_actual()
        total = TiempoUtils.calcular_total_a_pagar(horas, precio)
        
        respuesta = messagebox.askyesno(
            "Confirmar Salida",
            f"¿Desea registrar la salida del vehículo?\n\n"
            f"🚗 Placa: {self.vehiculo_seleccionado.placa}\n"
            f"⏱️ Tiempo: {self.vehiculo_seleccionado.obtener_tiempo_formateado()}\n"
            f"💰 Total a pagar: ${total:.2f}\n\n"
            f"¿Confirmar cobro y salida?"
        )
        
        if not respuesta:
            return
        
        # Registrar salida
        exito, mensaje, cobro = self.estacionamiento.registrar_salida(self.vehiculo_seleccionado.id_unico)
        
        if exito:
            # Registrar en movimientos del día
            espacios_disponibles = self.estacionamiento.obtener_espacios_disponibles()
            self.registro_movimientos.registrar_salida(
                cobro['placa'],
                cobro['id_unico'],
                cobro['horas_estadia'],
                cobro['total_pagado'],
                espacios_disponibles
            )
            
            # Mostrar recibo
            self._mostrar_recibo(cobro)
            
            # Actualizar callback
            if self.callback_actualizar:
                self.callback_actualizar()
            
            # Limpiar selección y actualizar lista
            self.vehiculo_seleccionado = None
            self._actualizar_lista_vehiculos()
            
            # Limpiar info
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
            self.total_label.config(text="")
            self.btn_procesar.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", f"No se pudo procesar la salida:\n{mensaje}")
    
    def _mostrar_recibo(self, cobro):
        """Muestra un recibo del pago"""
        recibo = f"""
╔══════════════════════════════════════════════════════════╗
║                    🧾 RECIBO DE PAGO                     ║
╠══════════════════════════════════════════════════════════╣
║  Estacionamiento - Sistema Automatizado                 ║
║                                                          ║
║  Fecha y hora: {cobro['hora_salida']}
║                                                          ║
║  🆔 ID Vehículo: {cobro['id_unico']}
║  🚗 Placa: {cobro['placa']}
║                                                          ║
║  ⏰ Ingreso: {cobro['hora_ingreso']}
║  ⏰ Salida:  {cobro['hora_salida']}
║                                                          ║
║  ⏱️ Tiempo total: {cobro['horas_estadia']:.2f} horas
║  💰 Tarifa: ${cobro['precio_por_hora']:.2f}/hora
║                                                          ║
║  ────────────────────────────────────────────────────   ║
║  💵 TOTAL A PAGAR: ${cobro['total_pagado']:.2f} MXN
║  ────────────────────────────────────────────────────   ║
║                                                          ║
║  ¡Gracias por usar nuestro servicio!                     ║
║  Que tenga un excelente día.                             ║
╚══════════════════════════════════════════════════════════╝
"""
        messagebox.showinfo("Recibo de Pago", recibo)