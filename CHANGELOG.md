# Changelog - Chat Punto a Punto Wi-Fi

Todos los cambios significativos del proyecto serán documentados en este archivo.

## [0.2.0] - 2026-04-24

### Añadido (Added)
- **Transferencia de archivos:** Implementación del módulo `file_transfer.py` con funciones:
  - `calculate_sha256()`: Cálculo de hash SHA-256 por bloques para verificación de integridad.
  - `get_file_metadata()`: Obtención de nombre, tamaño y checksum para el encabezado de transferencia.
- **Protocolo de archivo en servidor:** El servidor detecta automáticamente mensajes `FILE_CMD|` y los procesa como transferencia de archivos.
- **Protocolo de archivo en cliente:** Comando `/enviar <ruta>` para iniciar transferencia de archivos al servidor.
- **Barra de progreso:** Indicador visual de porcentaje durante el envío de archivos.
- **Verificación de integridad:** El servidor calcula SHA-256 del archivo recibido y lo compara con el hash enviado por el cliente.
- **Visualización mejorada en consola:**
  - Separadores y encabezados estructurados con `=`, `-`.
  - Formato de etiquetas `[CLIENTE]`, `[TU]`, `[ESTADO]`.
  - Tamaños de archivo en formato legible (B, KB, MB).
  - Hashes truncados a 32 caracteres para mejor legibilidad.
- **Funciones auxiliares de formato:**
  - `print_separator()`: Líneas divisorias configurables.
  - `print_header()`: Títulos formateados.
  - `print_info()`: Información con formato etiqueta: valor.
  - `format_size()`: Conversión de bytes a unidades legibles.

### Cambiado (Changed)
- **Rutas corregidas:** `RECEIVED_DIR` y `LOGS_DIR` ahora usan doble `os.path.dirname()` para apuntar correctamente a la raíz del proyecto (`Chat Wifi/`).
- **Buffer de recepción:** Aumentado de 1024 a 4096 bytes para manejar mensajes más largos.
- **Estructura del servidor:** Separación de responsabilidades con `handle_file_reception()` dedicado exclusivamente a transferencias.

### Corregido (Fixed)
- **Logs no se guardaban:** Solucionado error de ruta relativa que impedía crear `results/logs/` correctamente.
- **Carpeta `received` mal ubicada:** Ya no se crea dentro de `src/` sino en la raíz del proyecto.
- **Visualización de archivos entrantes:** Ahora muestra nombre, tamaño formateado y hash truncado antes de la transferencia.
- **Mensajes de error claros:** El cliente muestra mensajes específicos cuando un archivo no existe o la transferencia falla.

## [0.1.0] - 2026-04-20

### Añadido (Added)
- Estructura inicial del repositorio con carpetas `src/`, `docs/`, `images/`, `results/`, `scripts/`.
- Archivo `src/server_chat.py`: Servidor TCP funcional con soporte para chat bidireccional.
  - Escucha en `0.0.0.0:5000` por defecto.
  - Soporte para múltiples mensajes usando hilos (`threading`).
  - Logging de eventos en consola y archivo `results/logs/server.log`.

- Archivo `src/client_chat.py`: Cliente TCP funcional para conectar al servidor.
  - Conexión configurable vía `--host` y `--port`.
  - Chat bidireccional con hilos.
  - Logging en `results/logs/client.log`.
- Archivo `docs/THEORY.md`: Documentación teórica sobre sockets, TCP vs UDP, NAT y firewalls.

