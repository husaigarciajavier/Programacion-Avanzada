# Bitácora de Aprendizaje Python 

## 1. Sockets y Funciones Clave

### Concepto aprendido: ¿Qué es un socket?

Un **socket** es un punto final de comunicación entre dos programas que se ejecutan en una red. Funciona como un "enchufe virtual": el servidor "enchufa" su socket a un puerto y espera; el cliente "enchufa" el suyo para conectarse.

### Funciones principales utilizadas

| Función | ¿Qué hace? | ¿Dónde se usó? |
| :--- | :--- | :--- |
| `socket.socket()` | Crea un nuevo socket (TCP o UDP) | `server_chat.py`, `client_chat.py` |
| `socket.bind()` | Asocia el socket a una IP y puerto | `server_chat.py` |
| `socket.listen()` | Pone el socket en modo "escucha" | `server_chat.py` |
| `socket.accept()` | Acepta una conexión entrante | `server_chat.py` |
| `socket.connect()` | Conecta a un servidor remoto | `client_chat.py` |
| `socket.sendall()` | Envía TODOS los bytes (no solo parte) | `client_chat.py` (chat + archivos) |
| `socket.recv()` | Recibe datos del otro extremo | Ambos |
| `socket.setsockopt()` | Configura opciones del socket | `server_chat.py` |
| `socket.settimeout()` | Establece tiempo máximo de espera | Versión optimizada |
| `socket.shutdown()` | Cierra la conexión de forma controlada | `stop()` en ambos |

### Ejemplo simplificado de lo aprendido

```python
# Servidor
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 + TCP
s.bind(('0.0.0.0', 5000))
s.listen(1)
conn, addr = s.accept()
data = conn.recv(1024)
conn.sendall(b"Hola cliente!")
conn.close()
s.close()
```

### Diferencia clave aprendida: `send()` vs `sendall()`

- **`send()`**: Puede enviar solo parte de los datos. Retorna cuántos bytes envió realmente.
- **`sendall()`**: Garantiza que todos los bytes se envíen. Si falla, lanza excepción.

**Lección:** Para archivos y mensajes completos, **siempre usar `sendall()`**.


## 2. Manejo de Archivos

### Apertura y lectura por bloques

```python
# Lectura por bloques para archivos grandes (evita MemoryError)
with open("archivo_grande.pdf", "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
        # Procesar cada bloque de 4 KB
        socket.sendall(chunk)
```

### Concepto aprendido: `iter()` con `lambda`

La construcción `iter(lambda: f.read(4096), b"")` crea un iterador que:
1. Llama a `f.read(4096)` repetidamente.
2. Se detiene cuando devuelve `b""` (fin del archivo).

**Lección:** Así se leen archivos de cualquier tamaño sin cargarlos completos en RAM.

### Escritura controlada por tamaño restante

```python
# En lugar de escribir todo de golpe, se controla cuánto falta
with open(save_path, "wb") as f:
    remaining = size
    while remaining > 0:
        chunk = conn.recv(min(remaining, 4096))
        f.write(chunk)
        remaining -= len(chunk)
```

**Lección:** `min(remaining, BUFFER_SIZE)` evita leer más bytes de los necesarios al final del archivo.

---

## 3. Hashing con `hashlib`

### SHA-256 para verificación de integridad

```python
import hashlib

# Inicializar el algoritmo
sha = hashlib.sha256()

# Alimentar con datos en bloques
with open("archivo.bin", "rb") as f:
    for bloque in iter(lambda: f.read(4096), b""):
        sha.update(bloque)

# Obtener hash final (64 caracteres hex)
hash_final = sha.hexdigest()
print(hash_final)  # ej: "a1b2c3d4e5f6..."
```

### Concepto aprendido

- **`hashlib.sha256()`**: Inicializa el algoritmo SHA-256.
- **`.update()`**: Agrega datos al cálculo (puede llamarse múltiples veces).
- **`.hexdigest()`**: Devuelve el hash como cadena hexadecimal de 64 caracteres.

**Lección:** SHA-256 es determinista: el mismo archivo **siempre** produce el mismo hash. Si el hash del servidor coincide con el del cliente, el archivo llegó íntegro.

---

## 4. Logging con `logging`

### Configuración dual: consola + archivo

```python
import logging
import os

os.makedirs("results/logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('results/logs/server.log'),
        logging.StreamHandler()
    ]
)
```

### Conceptos aprendidos

| Elemento | Propósito |
| :--- | :--- |
| `basicConfig()` | Configuración global del sistema de logging |
| `FileHandler()` | Escribe los logs en un archivo |
| `StreamHandler()` | Muestra los logs en consola |
| `%(asctime)s` | Inserta la fecha/hora automáticamente |
| `level=logging.INFO` | Filtra mensajes con prioridad INFO o superior |
| `exist_ok=True` | No lanza error si la carpeta ya existe |

**Lección:** `print()` es para el usuario final; `logging` es para el desarrollador. Separarlos permite depurar sin ensuciar la interfaz.

---

## 5. Argumentos de Línea de Comandos con `argparse`

### Implementación aprendida

```python
import argparse

parser = argparse.ArgumentParser(description='Servidor de Chat')
parser.add_argument('--host', default='0.0.0.0', help='IP del servidor')
parser.add_argument('--port', type=int, default=5000, help='Puerto')

args = parser.parse_args()

# Uso: python server_chat.py --host 192.168.1.65 --port 6000
print(args.host)  # '192.168.1.65'
print(args.port)  # 6000
```

### Ventaja aprendida

Con `argparse`, el mismo código funciona sin modificaciones en cualquier máquina:
- **Desarrollo local:** `python server_chat.py` (usa defaults).
- **Producción:** `python server_chat.py --host 192.168.1.65 --port 9999`.

---

## 6. Concurrencia Básica con `threading`

### Problema resuelto

Sin hilos, el servidor **no puede recibir y enviar al mismo tiempo**. Si está esperando `input()`, se bloquea y no recibe mensajes entrantes.

### Solución implementada

```python
import threading

# Hilo Demonio: muere cuando el programa principal termina
receive_thread = threading.Thread(target=self.receive_messages)
receive_thread.daemon = True
receive_thread.start()

# El hilo principal sigue con input() para enviar
```

### Conceptos aprendidos

| Concepto | Explicación |
| :--- | :--- |
| `Thread(target=funcion)` | Crea un hilo que ejecutará `funcion` |
| `.daemon = True` | El hilo se cierra automáticamente al salir del programa |
| `.start()` | Inicia la ejecución del hilo |
| `flush=True` en `print()` | Fuerza mostrar texto sin esperar salto de línea |

**Lección:** `threading` es suficiente para un chat simple. Para aplicaciones masivas, se investigaría `asyncio` o `select`.


## 7. Buenas Prácticas Aprendidas

### 1. Enviar metadatos antes que datos
En la transferencia de archivos, el cliente envía `NOMBRE|TAMAÑO|HASH` antes del contenido binario. El servidor sabe exactamente qué esperar.

### 2. Manejo de excepciones específicas
```python
# Malo: captura todo
except Exception:

# Bueno: captura errores concretos
except ConnectionResetError:
    logging.warning("Cliente desconectado abruptamente")
except ConnectionRefusedError:
    logging.error("Servidor no disponible")
```

### 3. Contexto `with` para recursos
```python
# El socket/archivo se cierra automáticamente al salir del bloque
with socket.socket(...) as s:
    s.connect(...)
    # No necesita s.close()
```

### 4. Mensajes de commit significativos
Formato estándar: `tipo: descripción breve — Autor`
- `feat:` Nueva funcionalidad.
- `fix:` Corrección de error.
- `docs:` Documentación.
- `test:` Evidencias y pruebas.
- `chore:` Tareas de mantenimiento.

---

## 8. Comparativa de Herramientas Exploradas

| Herramienta | ¿Cuándo usarla? | ¿Se usó en el proyecto? |
| :--- | :--- | :--- |
| `telnet` | Probar servidores TCP manualmente | ✅ Sí, para verificar el servidor |
| `ncat` / `nc` | Alternativa moderna a telnet | ⬜ Mencionado como opción |
| `ipconfig` | Verificar IP local en Windows | ✅ Sí, en DECISION.md |
| `netsh` | Crear hotspot desde terminal | ✅ Sí, en scripts |
| `pyinstaller` | Crear .exe desde Python | ⬜ Investigado, no implementado |
| `git` | Control de versiones | ✅ Sí, durante todo el proyecto |

