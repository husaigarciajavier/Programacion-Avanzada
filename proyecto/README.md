## `README.md` 
Tabla de Contenidos

- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Cómo Usar](#cómo-usar)
- [Base de Datos](#base-de-datos)
- [Política de Cobro](#política-de-cobro)
- [Autores](#autores)
- [Versiones](#versiones)

---

## Características

### Funcionalidades Principales
| Función | Descripción |
|---------|-------------|
|  **Registro de Ingreso** | Asigna ID único automático al vehículo |
|  **Registro de Salida** | Calcula tiempo y cobra según tarifa |
|  **Capacidad Configurable** | Ajustable por el usuario (1-100 vehículos) |
|  **Precio por Hora** | Modificable en tiempo real ($0.50 - $50.00) |
|  **Reportes Diarios** | Exporta movimientos a TXT y JSON |
|  **Persistencia de Datos** | Guardado automático por día |



##  Requisitos

### Sistema Operativo
- Windows 10/11
- Linux (Ubuntu/Debian)
- macOS

### Software Necesario
```bash
Python 3.8 o superior
Git (opcional, para clonar)
```

### Dependencias
**¡No requiere librerías externas!** Solo biblioteca estándar de Python:
- `tkinter` - Interfaz gráfica
- `datetime` - Manejo de fechas
- `json` - Persistencia de datos
- `uuid` - Generación de IDs
- `pathlib` - Manejo de rutas

---

##  Instalación

### Opción 1: Clonar con Git
```bash
git clone https://github.com/husaigarciajavier/Programacion-Avanzada.git
cd Programacion-Avanzada
```

### Opción 2: Descargar ZIP
1. Ir a: `https://github.com/husaigarciajavier/Programacion-Avanzada`
2. Click en "Code" → "Download ZIP"
3. Extraer en una carpeta



##  Ejecución

### Comando Principal
```bash
cd Programacion-Avanzada
python run.py
```

### Alternativas
```bash
# Desde la carpeta del proyecto
cd proyecto
python -m src.main

# Directo al archivo principal
python proyecto/src/main.py
```

### Salida Esperada
```
=========================================
🅿️ SISTEMA DE ESTACIONAMIENTO v1.1
=========================================
✅ Directorios listos
✅ Aplicación iniciada
```

---

##  Cómo Usar

### 1. Registrar Ingreso
```
1. Click en "Registrar Ingreso"
2. Ingresar placa (ejemplo: ABC123)
3. Click en "Registrar" o presionar Enter
4. Se asigna ID único automático
```

### 2. Registrar Salida
```
1. Click en "Registrar Salida"
2. Seleccionar vehículo de la lista
3. Ver total a pagar
4. Click en "Confirmar Pago" o presionar Enter
5. Recibir recibo
```

### 3. Configurar Estacionamiento
```
1. Click en "Configuración" o presionar Ctrl+C
2. Ajustar capacidad máxima (1-100)
3. Modificar precio por hora ($0.50 - $50.00)
4. Click en "Guardar" o presionar Enter
```

### 4. Generar Reportes
```
1. Click en "Reportes"
2. Ver movimientos del día
3. Click en "Exportar a TXT"
4. Elegir ubicación de guardado
```

### Atajos de Teclado
| Ventana | Atajo | Acción |
|---------|-------|--------|
| Todas | `Enter` | Confirmar / Guardar |
| Todas | `Esc` | Cancelar / Cerrar |
| Principal | `F5` | Refrescar (próximamente) |

---

##  Base de Datos

### Formato de Archivos

**JSON (estructurado):**
```json
{
  "fecha": "2026-06-03",
  "total_ingresos": 5,
  "total_salidas": 3,
  "total_recaudado": 45.00,
  "movimientos": [...],
  "ultima_actualizacion": "2026-06-03 17:30:00"
}
```

**TXT (legible):**
```
[2026-06-03 09:15:30] INGRESO | Placa: ABC123 | ID: a1b2c3d4 | Libres: 31
[2026-06-03 11:00:00] SALIDA | Placa: ABC123 | ID: a1b2c3d4 | Horas: 1.75 | Total: $10.00 | Libres: 32
```

### Archivos Generados
| Archivo | Contenido | Formato |
|---------|-----------|---------|
| `movimientos_YYYY-MM-DD.json` | Todos los movimientos | JSON |
| `movimientos_YYYY-MM-DD.txt` | Movimientos en texto plano | TXT |
| `reporte_YYYY-MM-DD.txt` | Reporte con estadísticas | TXT |
| `config_estacionamiento.json` | Capacidad y precio | JSON |

---

##  Política de Cobro

### Regla: Redondeo Siempre Hacia Arriba

| Tiempo Real | Horas Decimal | Horas a Cobrar | Total ($5/hora) |
|-------------|---------------|----------------|-----------------|
| 0 - 59 minutos | 0.00 - 0.98 | 1 hora | $5.00 |
| 1 hora 0 min | 1.00 | 1 hora | $5.00 |
| 1 hora 1 min | 1.02 | 2 horas | $10.00 |
| 1 hora 30 min | 1.50 | 2 horas | $10.00 |
| 1 hora 59 min | 1.98 | 2 horas | $10.00 |
| 2 horas 0 min | 2.00 | 2 horas | $10.00 |
| 2 horas 1 min | 2.02 | 3 horas | $15.00 |

---

## Autores

**Eunice Husai Garcia Javier**
- GitHub: [@husaigarciajavier](https://github.com/husaigarciajavier)

**Joel Aldair Morales Martinez**
- GitHub: 

**Anessa Miranda Peredo Garcia**
- GitHub: 




## Versiones

### v1.1 (Actual)
- ✅ Persistencia por día (JSON + TXT)
- ✅ Redondeo hacia arriba en cobros
- ✅ Optimización del código (-39% líneas)
- ✅ Atajos de teclado (Enter/Esc)
- ✅ Validación de entradas
- ✅ Mejora en manejo de errores

### v1.0 (Base)
- ✅ Funcionalidades básicas
- ✅ Interfaz gráfica funcional
- ✅ Registro de ingresos/salidas

---

## Licencia

Este proyecto es de uso educativo. Puede ser utilizado y modificado para fines académicos.

---
**¡Gracias por usar el Sistema de Gestión de Estacionamiento!** 