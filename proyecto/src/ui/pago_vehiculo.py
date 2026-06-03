"""
Ventana para procesar pago y salida
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import COLOR_FONDO, COLOR_BOTON, COLOR_BOTON_PELIGRO
from src.utils.tiempo_utils import TiempoUtils


class VentanaPagoVehiculo:
    """Ventana para registrar salida y pago"""
    
    def __init__(self, parent, estacionamiento, registro_movimientos, callback_actualizar=None):
        self.parent = parent
        self.estacionamiento = estacionamiento
        self.registro_movimientos = registro_movimientos
        self.callback_actualizar = callback_actualizar
        self.vehiculo_seleccionado = None
        
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("Registrar Salida")
        self.ventana.geometry("600x550")
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(False, False)
        self.ventana.transient(parent)
        self.ventana.grab_set()
        
        self.ventana.bind('<Return>', lambda e: self._procesar_pago())
        self.ventana.bind('<Escape>', lambda e: self.ventana.destroy())
        
        self._crear_widgets()
        self._actualizar_lista()
    
    def _crear_widgets(self):
        main = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main, text="Registrar Salida", font=("Arial", 14, "bold"), 
                bg=COLOR_FONDO).pack(pady=(0, 20))
        
        # Lista de vehículos
        frame_lista = tk.LabelFrame(main, text="Vehículos estacionados", bg=COLOR_FONDO, padx=10, pady=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        columns = ("ID", "Placa", "Ingreso", "Tiempo")
        self.tree = ttk.Treeview(frame_lista, columns=columns, show="headings", height=6)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=150)
        self.tree.column("Placa", width=80)
        self.tree.column("Ingreso", width=130)
        self.tree.column("Tiempo", width=120)
        
        scroll = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_seleccion)
        
        # Información del vehículo
        frame_info = tk.LabelFrame(main, text="Información", bg=COLOR_FONDO, padx=10, pady=10)
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = tk.Text(frame_info, height=6, font=("Arial", 9))
        self.info_text.pack(fill=tk.X)
        self.info_text.config(state=tk.DISABLED)
        
        # Total a pagar
        frame_total = tk.Frame(main, bg=COLOR_FONDO)
        frame_total.pack(fill=tk.X, pady=(0, 15))
        
        self.total_label = tk.Label(frame_total, text="", font=("Arial", 14, "bold"), 
                                    fg="green", bg=COLOR_FONDO)
        self.total_label.pack()
        
        # Botones
        frame_btns = tk.Frame(main, bg=COLOR_FONDO)
        frame_btns.pack(fill=tk.X)
        
        self.btn_pagar = tk.Button(frame_btns, text="✅ Confirmar Pago (Enter)", 
                                   bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                                   command=self._procesar_pago, state=tk.DISABLED)
        self.btn_pagar.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(frame_btns, text="Actualizar", command=self._actualizar_lista).pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(frame_btns, text="❌ Cancelar (Esc)", bg=COLOR_BOTON_PELIGRO, 
                 fg="white", command=self.ventana.destroy).pack(side=tk.LEFT)
        
        tk.Label(main, text="💡 Seleccione un vehículo → Confirme el pago", 
                bg=COLOR_FONDO, font=("Arial", 9, "italic")).pack(pady=(10, 0))
    
    def _actualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for v in self.estacionamiento.vehiculos_activos:
            self.tree.insert("", tk.END, values=(
                v.id_unico[:16] + "...", v.placa, v.hora_ingreso, v.tiempo_formateado))
        
        self.btn_pagar.config(state=tk.DISABLED)
        self.vehiculo_seleccionado = None
    
    def _on_seleccion(self, event):
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        valores = self.tree.item(seleccion[0], "values")
        placa = valores[1]
        self.vehiculo_seleccionado = self.estacionamiento.buscar_por_placa(placa)
        
        if self.vehiculo_seleccionado:
            v = self.vehiculo_seleccionado
            horas = v.tiempo_estadia
            precio = self.estacionamiento.obtener_precio_actual()
            total = TiempoUtils.calcular_total_a_pagar(horas, precio)
            
            info = f"Placa: {v.placa}\nID: {v.id_unico}\nIngreso: {v.hora_ingreso}\nTiempo: {v.tiempo_formateado}\nTarifa: ${precio:.2f}/hora"
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)
            self.info_text.config(state=tk.DISABLED)
            
            self.total_label.config(text=f"TOTAL: ${total:.2f} MXN")
            self.btn_pagar.config(state=tk.NORMAL)
    
    def _procesar_pago(self):
        if not self.vehiculo_seleccionado:
            return
        
        v = self.vehiculo_seleccionado
        total = TiempoUtils.calcular_total_a_pagar(v.tiempo_estadia, 
                                                   self.estacionamiento.obtener_precio_actual())
        
        if not messagebox.askyesno("Confirmar", f"Confirmar salida de {v.placa}\nTotal: ${total:.2f}"):
            return
        
        exito, msg, cobro = self.estacionamiento.registrar_salida(v.id_unico)
        
        if exito:
            self.registro_movimientos.registrar_salida(cobro['placa'], cobro['id_unico'],
                                                       cobro['horas_estadia'], cobro['total_pagado'],
                                                       self.estacionamiento.espacios_disponibles)
            
            recibo = f"""
╔═════════════════════════════════════╗
║         RECIBO DE PAGO                ║
╠═════════════════════════════════════╣
║ Placa: {cobro['placa']}
║ Horas: {cobro['horas_estadia']:.2f}
║ Total: ${cobro['total_pagado']:.2f}
║ Tarifa: ${cobro['precio_por_hora']:.2f}/h
╚═════════════════════════════════════╝
"""
            messagebox.showinfo("Recibo", recibo)
            
            if self.callback_actualizar:
                self.callback_actualizar()
            
            self._actualizar_lista()
            self.info_text.config(state=tk.NORMAL)
            self.info_text.delete(1.0, tk.END)
            self.info_text.config(state=tk.DISABLED)
            self.total_label.config(text="")
        else:
            messagebox.showerror("Error", msg)