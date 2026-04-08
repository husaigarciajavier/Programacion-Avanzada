# Mejoras Implementadas en el Sistema de Adquisición de Datos

El código original ha sido mejorado con tres funcionalidades principales que aumentan la calidad y confiabilidad de los datos adquiridos:

---

## 1. Mediana Móvil (Moving Median)

### ¿Qué hace?
Aplica un filtro de mediana móvil con ventana deslizante sobre las lecturas de temperatura y LDR después de la adquisición.

### ¿Cómo funciona?
- Para cada muestra, toma una ventana de 5 lecturas (2 anteriores, la actual y 2 siguientes)
- Calcula la mediana de esa ventana (valor central cuando se ordenan)
- Reemplaza el valor original por esta mediana

### Ventajas
- Elimina picos espurios y valores atípicos (*outliers*) de forma efectiva
- Preserva mejor los bordes y transiciones que un filtro de promedio móvil
- Es especialmente útil para sensores que pueden tener lecturas erráticas ocasionales
- Mantiene la integridad de las tendencias reales mientras reduce ruido impulsivo

### Ejemplo práctico
Si el sensor LDR registra un pico repentino de 900 (por un destello de luz) rodeado de valores de 450, la mediana móvil lo reemplazará por un valor cercano a 450, eliminando la anomalía.

---

## 2. Calibración por Offset con Muestras Iniciales

### ¿Qué hace?
Utiliza las primeras N muestras (configurables) para determinar un offset de calibración que corrige el sesgo sistemático de los sensores.

### ¿Cómo funciona?
1. Durante la fase inicial de adquisición, recolecta N muestras sin aplicar calibración
2. Calcula la mediana de estas muestras (más robusta que el promedio)
3. Compara esta mediana con valores de referencia esperados:
   - **Temperatura:** 22°C (temperatura ambiente típica)
   - **LDR:** 500 ADC (valor medio típico)
4. Calcula el offset necesario: `offset = valor_esperado - mediana_muestras`
5. Aplica este offset a todas las lecturas posteriores

### Ventajas
- Compensa variaciones entre sensores (tolerancias de fabricación)
- Corrige sesgos de instalación o condiciones iniciales
- Usa mediana en lugar de promedio para evitar que valores atípicos en calibración distorsionen el offset
- Proporciona trazabilidad de la calibración en los metadatos

### Ejemplo práctico
Si un sensor de temperatura lee sistemáticamente 21.5°C cuando en realidad hay 22°C, el sistema detecta este desfase durante la calibración y suma automáticamente +0.5°C a todas las lecturas.

---

## 3. Columnas Crudas y Filtradas en CSV

### ¿Qué hace?
El archivo CSV ahora contiene simultáneamente los datos originales (crudos) y los datos procesados (calibrados + filtrados).

### Estructura del CSV

| Columna | Descripción |
|---------|-------------|
| `timestamp` | Marca de tiempo ISO 8601 |
| `temp_raw` | Temperatura cruda sin procesar |
| `ldr_raw` | LDR crudo sin procesar |
| `temp_calibrated` | Temperatura calibrada + mediana móvil |
| `ldr_calibrated` | LDR calibrado + mediana móvil |

### Ventajas
- **Transparencia:** Permite verificar el efecto de la calibración y filtrado
- **Flexibilidad:** El usuario puede aplicar sus propios algoritmos de procesamiento sobre los datos crudos
- **Auditoría:** Facilita la detección de problemas en los sensores o en el procesamiento
- **Reprocesamiento:** Si se mejora el algoritmo de filtrado, se pueden re-procesar los datos crudos sin re-adquirir

---

## Mejoras Adicionales Implementadas

### Visualización Mejorada
- Gráfica con dos subplots que comparan lado a lado datos crudos vs procesados
- Curvas superpuestas para evaluar visualmente el efecto del filtrado

### Estadísticas Completas
- Se añadió cálculo de mediana en el resumen estadístico
- Estadísticas separadas para datos crudos y calibrados

### Metadata Enriquecida
- Incluye información detallada de calibración (offset aplicado, muestras usadas)
- Permite reproducir el experimento con las mismas condiciones de calibración

### Nuevo Parámetro CLI
- `--cal-samples`: Permite al usuario definir cuántas muestras usar para calibración

---

## Resumen de Argumentos

| Argumento | Descripción | Valor por Defecto |
|-----------|-------------|------------------|
| `--mode` | Modo de adquisición (`sim` o `serial`) | `sim` |
| `--port` | Puerto serial (ej: COM3 o /dev/ttyUSB0) | `None` |
| `--baud` | Baudrate para serial | `115200` |
| `--duration` | Duración total en segundos | `60` |
| `--interval` | Intervalo entre muestras en segundos | `1` |
| `--cal-samples` | Número de muestras iniciales para calibración | `10` |

