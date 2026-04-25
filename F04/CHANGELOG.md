# CHANGELOG.md

## [1.1.0] - 2026-03-27

### Añadido
- **Mediana móvil**: Filtro con ventana de 5 muestras para eliminar ruido impulsivo en temperatura y LDR
- **Calibración por offset**: Sistema de calibración automática usando mediana de N muestras iniciales (configurable con `--cal-samples`)
- **Almacenamiento dual**: CSV ahora incluye columnas `temp_calibrated` y `ldr_calibrated` junto a los datos crudos
- **Estadística de mediana**: Cálculo de mediana para todas las variables en el resumen final
- **Nuevo argumento CLI**: `--cal-samples` para definir número de muestras de calibración
- **Información de calibración en metadata**: Registro de offsets aplicados y muestras utilizadas
- **Gráfica comparativa**: Subplots que muestran raw vs calibrado para temperatura y LDR

### Modificado
- **Estructura CSV**: De 3 columnas (`timestamp`, `temp_raw`, `ldr_raw`) a 5 columnas con datos procesados
- **Función `acquire_data`**: Ahora retorna tupla con readings y objeto calibrator
- **Estadísticas**: Separadas para datos raw y calibrados en metadata y resumen
- **Visualización**: Gráfica mejorada con dos subplots y comparación directa
- **Manejo de errores**: Mejor tolerancia a valores NaN durante calibración y filtrado

### Corregido
- Error al obtener `__version__` de matplotlib.pyplot en `save_environment()`

---

## [1.0.1] - 2026-03-26

### Corregido
- Bug en `simulate_reading()`: reemplazo de `random.sin()` por `math.sin()`

---

## [1.0.0] - 2026-03-25

### Añadido
- Adquisición de datos en modo simulación y serial
- Guardado de datos en CSV con timestamp ISO 8601
- Estadísticas básicas (media, min, max, std)
- Generación de gráfica con matplotlib
- Metadata en JSON con configuración y estadísticas
- Escritura atómica de archivos
- Argumentos CLI: `--mode`, `--port`, `--baud`, `--duration`, `--interval`
