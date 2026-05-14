"""
Ventana principal del sistema de estacionamiento
Interfaz principal que une todos los módulos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.config.constants import (
    VENTANA_TITULO, VENTANA_SIZE, COLOR_FONDO, 
    COLOR_BOTON, COLOR_BOTON_PELIGRO, COLOR_BOTON_INFO
)
from src.models.estacionamiento import Estacionamiento
from src.models.registro import RegistroMovimientos
from src.database import DatabaseManager
from src.ui.registro_vehiculo import VentanaRegistroVehiculo
from src.ui.pago_vehiculo import VentanaPagoVehiculo
from src.ui.reportes import VentanaReportes
from src.ui.configuracion import VentanaConfiguracion

class VentanaPrincipal:
    """Ventana principal del sistema de estacionamiento"""
    
    def __init__(self):
        """Inicializa la ventana principal y todos los componentes"""
        self.estacionamiento = Estacionamiento()
        self.registro_movimientos = RegistroMovimientos()
        self.db_manager = DatabaseManager()
        
        # Cargar datos guardados
        self._cargar_datos_guardados()
        
        # Crear ventana
        self.ventana = tk.Tk()
        self.ventana.title(VENTANA_TITULO)
        self.ventana.geometry(VENTANA_SIZE)
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(True, True)
        
        # Configurar cierre seguro
        self.ventana.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        
        self._crear_menu()
        self._crear_widgets()
        self._actualizar_info()
        
        # Actualizar información cada minuto
        self._programar_actualizacion()
    
    def _cargar_datos_guardados(self):
        """Carga los datos guardados al iniciar la aplicación"""
        try:
            # Cargar vehículos activos
            self.db_manager.cargar_vehiculos_activos(self.estacionamiento)
            print(f"✅ Datos cargados: {len(self.estacionamiento.obtener_vehiculos_activos())} vehículos activos")
        except Exception as e:
            print(f"⚠️ No se pudieron cargar datos previos: {e}")
    
    def _guardar_datos(self):
        """Guarda los datos actuales"""
        try:
            self.db_manager.guardar_vehiculos_activos(self.estacionamiento)
            self.db_manager.guardar_estado_completo(self.estacionamiento, self.registro_movimientos)
        except Exception as e:
            print(f"⚠️ Error al guardar datos: {e}")
    
    def _cerrar_aplicacion(self):
        """Maneja el cierre seguro de la aplicación"""
        if messagebox.askyesno("Salir", "¿Está seguro que desea salir?\nLos datos se guardarán automáticamente."):
            self._guardar_datos()
            self.ventana.quit()
            self.ventana.destroy()
    
    def _crear_menu(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.ventana)
        self.ventana.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="💾 Guardar ahora", command=self._guardar_datos)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="❌ Salir", command=self._cerrar_aplicacion)
        
        # Menú Operaciones
        menu_operaciones = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🚗 Operaciones", menu=menu_operaciones)
        menu_operaciones.add_command(label="✅ Registrar Ingreso", command=self._abrir_registro)
        menu_operaciones.add_command(label="💰 Registrar Salida", command=self._abrir_pago)
        menu_operaciones.add_separator()
        menu_operaciones.add_command(label="⚙️ Configuración", command=self._abrir_configuracion)
        
        # Menú Reportes
        menu_reportes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📊 Reportes", menu=menu_reportes)
        menu_reportes.add_command(label="📄 Ver Reportes", command=self._abrir_reportes)
        menu_reportes.add_command(label="💾 Exportar Movimientos", command=self._exportar_movimientos)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="❓ Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="ℹ️ Acerca de", command=self._mostrar_acerca_de)
        menu_ayuda.add_command(label="📖 Instrucciones", command=self._mostrar_instrucciones)
    
    def _crear_widgets(self):
        """Crea los widgets de la ventana principal"""
        
        # Frame principal
        main_frame = tk.Frame(self.ventana, bg=COLOR_FONDO, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(main_frame, text="🅿️ Sistema de Gestión de Estacionamiento", 
                         font=("Arial", 18, "bold"), bg=COLOR_FONDO, fg="#2c3e50")
        titulo.pack(pady=(0, 20))
        
        # Frame de información (panel superior)
        frame_info = tk.LabelFrame(main_frame, text="Estado Actual", 
                                   bg=COLOR_FONDO, padx=15, pady=10, font=("Arial", 12, "bold"))
        frame_info.pack(fill=tk.X, pady=(0, 15))
        
        # Grid de información
        self.info_labels = {}
        info_items = [
            ("🅿️ Capacidad:", "capacidad"),
            ("🚗 Vehículos dentro:", "activos"),
            ("✅ Espacios libres:", "disponibles"),
            ("📊 Ocupación:", "ocupacion"),
            ("💰 Tarifa:", "precio"),
            ("💵 Recaudación hoy:", "recaudacion"),
            ("📝 Movimientos hoy:", "movimientos")
        ]
        
        for i, (texto, key) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2
            tk.Label(frame_info, text=texto, bg=COLOR_FONDO, font=("Arial", 10, "bold")).grid(
                row=row, column=col, sticky=tk.W, padx=(10, 5), pady=5)
            self.info_labels[key] = tk.Label(frame_info, text="---", bg=COLOR_FONDO, 
                                              font=("Arial", 10), fg="#2980b9")
            self.info_labels[key].grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=5)
        
        # Frame de vehículos activos
        frame_vehiculos = tk.LabelFrame(main_frame, text="Vehículos Estacionados", 
                                        bg=COLOR_FONDO, padx=10, pady=10, font=("Arial", 12, "bold"))
        frame_vehiculos.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview para mostrar vehículos
        columns = ("ID", "Placa", "Hora Ingreso", "Tiempo", "Estado")
        self.tree = ttk.Treeview(frame_vehiculos, columns=columns, show="headings", height=10)
        
        self.tree.heading("ID", text="ID Vehículo")
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("Hora Ingreso", text="Hora Ingreso")
        self.tree.heading("Tiempo", text="Tiempo Estacionado")
        self.tree.heading("Estado", text="Estado")
        
        self.tree.column("ID", width=150)
        self.tree.column("Placa", width=100)
        self.tree.column("Hora Ingreso", width=130)
        self.tree.column("Tiempo", width=120)
        self.tree.column("Estado", width=80)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_vehiculos, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame de botones de acción rápida
        frame_botones = tk.Frame(main_frame, bg=COLOR_FONDO)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        btn_ingreso = tk.Button(frame_botones, text="✅ Registrar Ingreso", 
                               bg=COLOR_BOTON, fg="white", font=("Arial", 10, "bold"),
                               command=self._abrir_registro, padx=15, pady=5)
        btn_ingreso.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_salida = tk.Button(frame_botones, text="💰 Registrar Salida", 
                              bg=COLOR_BOTON_INFO, fg="white", font=("Arial", 10, "bold"),
                              command=self._abrir_pago, padx=15, pady=5)
        btn_salida.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_reportes = tk.Button(frame_botones, text="📊 Ver Reportes", 
                                bg=COLOR_BOTON_INFO, fg="white", font=("Arial", 10, "bold"),
                                command=self._abrir_reportes, padx=15, pady=5)
        btn_reportes.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_config = tk.Button(frame_botones, text="⚙️ Configuración", 
                              bg=COLOR_BOTON_INFO, fg="white", font=("Arial", 10, "bold"),
                              command=self._abrir_configuracion, padx=15, pady=5)
        btn_config.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_refrescar = tk.Button(frame_botones, text="🔄 Refrescar", 
                                 bg=COLOR_BOTON_INFO, fg="white", font=("Arial", 10, "bold"),
                                 command=self._actualizar_info, padx=15, pady=5)
        btn_refrescar.pack(side=tk.LEFT)
        
        # Barra de estado
        self.status_bar = tk.Label(self.ventana, text="Sistema listo", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _actualizar_info(self):
        """Actualiza toda la información mostrada en la ventana"""
        # Actualizar info del estacionamiento
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
        
        # Actualizar labels
        self.info_labels['capacidad'].config(text=f"{capacidad} lugares")
        self.info_labels['activos'].config(text=f"{activos}")
        self.info_labels['disponibles'].config(text=f"{disponibles}")
        self.info_labels['ocupacion'].config(text=f"{ocupacion:.1f}%")
        self.info_labels['precio'].config(text=f"${precio:.2f}/hora")
        self.info_labels['recaudacion'].config(text=f"${total_recaudado:.2f}")
        self.info_labels['movimientos'].config(text=f"{len(movimientos_hoy)}")
        
        # Cambiar color según ocupación
        if ocupacion > 80:
            self.info_labels['ocupacion'].config(fg="red")
        elif ocupacion > 50:
            self.info_labels['ocupacion'].config(fg="orange")
        else:
            self.info_labels['ocupacion'].config(fg="green")
        
        # Actualizar lista de vehículos activos
        self._actualizar_lista_vehiculos()
        
        # Actualizar barra de estado
        self.status_bar.config(text=f"Última actualización: {self._obtener_hora_actual()} | "
                                    f"Espacios libres: {disponibles}/{capacidad}")
    
    def _actualizar_lista_vehiculos(self):
        """Actualiza el treeview con los vehículos activos"""
        # Limpiar tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        vehiculos = self.estacionamiento.obtener_vehiculos_activos()
        
        if not vehiculos:
            self.tree.insert("", tk.END, values=("---", "No hay vehículos", "---", "---", "---"))
            return
        
        for v in vehiculos:
            tiempo_formateado = v.obtener_tiempo_formateado()
            estado = "🟢 Activo"
            self.tree.insert("", tk.END, values=(v.id_unico[:16] + "...", v.placa, v.hora_ingreso, tiempo_formateado, estado))
    
    def _obtener_hora_actual(self):
        """Retorna la hora actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _programar_actualizacion(self):
        """Programa actualizaciones periódicas de la interfaz"""
        self._actualizar_info()
        self.ventana.after(30000, self._programar_actualizacion)  # Cada 30 segundos
    
    def _abrir_registro(self):
        """Abre la ventana de registro de vehículos"""
        VentanaRegistroVehiculo(self.ventana, self.estacionamiento, self.registro_movimientos, self._actualizar_info)
    
    def _abrir_pago(self):
        """Abre la ventana de pago y salida"""
        VentanaPagoVehiculo(self.ventana, self.estacionamiento, self.registro_movimientos, self._actualizar_info)
    
    def _abrir_reportes(self):
        """Abre la ventana de reportes"""
        VentanaReportes(self.ventana, self.estacionamiento, self.registro_movimientos)
    
    def _abrir_configuracion(self):
        """Abre la ventana de configuración"""
        VentanaConfiguracion(self.ventana, self.estacionamiento, self._actualizar_info)
    
    def _exportar_movimientos(self):
        """Exporta los movimientos del día"""
        if not self.registro_movimientos.hay_movimientos():
            messagebox.showwarning("Advertencia", "No hay movimientos registrados hoy para exportar")
            return
        
        ruta = self.registro_movimientos.exportar_reporte_diario()
        if ruta:
            messagebox.showinfo("Éxito", f"✅ Movimientos exportados a:\n{ruta}")
    
    def _mostrar_acerca_de(self):
        """Muestra información acerca del software"""
        acerca = """
        🅿️ SISTEMA DE GESTIÓN DE ESTACIONAMIENTO
        
        Versión: 1.0.0
        Desarrollado para: Programación Avanzada
        
        Características:
        • Capacidad configurable por el usuario
        • Registro automático de tiempos
        • Precio por hora ajustable
        • Guardado automático de datos
        • Generación de reportes en TXT
        • Interfaz gráfica amigable
        
        © 2026 - Todos los derechos reservados
        """
        messagebox.showinfo("Acerca de", acerca)
    
    def _mostrar_instrucciones(self):
        """Muestra instrucciones de uso"""
        instrucciones = """
        📖 INSTRUCCIONES DE USO
        
        1. REGISTRAR INGRESO:
           - Haga clic en "Registrar Ingreso"
           - Ingrese la placa del vehículo
           - El sistema asignará un ID automático
        
        2. REGISTRAR SALIDA:
           - Seleccione el vehículo de la lista
           - Haga clic en "Registrar Salida"
           - Confirme el cobro
        
        3. CONFIGURACIÓN:
           - Ajuste capacidad máxima y precio/hora
           - Los cambios se guardan automáticamente
        
        4. REPORTES:
           - Vea movimientos del día
           - Exporte reportes a archivos TXT
        
        5. GUARDADO:
           - Todo se guarda automáticamente
           - Al cerrar la app se guarda todo
        
        ¡El sistema es intuitivo y fácil de usar!
        """
        messagebox.showinfo("Instrucciones", instrucciones)
    
    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()