# Chat Punto a Punto Wi-Fi con Transferencia de Archivos

Proyecto académico de redes y programación en Python. Aplicación de chat bidireccional por Wi-Fi entre dos laptops usando **sockets TCP**, con mejora opcional de **transferencia de archivos** y verificación de integridad mediante **SHA-256**.


## Tabla de Contenidos

- [Descripción](#descripción)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación y Ejecución](#instalación-y-ejecución)
  - [Paso 1: Iniciar el Servidor](#paso-1-iniciar-el-servidor)
  - [Paso 2: Conectar el Cliente](#paso-2-conectar-el-cliente)
  - [Paso 3: Chatear](#paso-3-chatear)
  - [Paso 4: Transferir Archivos](#paso-4-transferir-archivos-opcional)
- [Métodos de Conexión](#métodos-de-conexión)
- [Solución de Problemas](#solución-de-problemas)
- [Documentación](#documentación)

## Descripción

**Objetivo:** Desarrollar una aplicación en Python que permita la comunicación entre dos laptops conectadas por Wi-Fi mediante un chat simple cliente/servidor, con la mejora opcional de transferencia de archivos.

**Funcionalidades implementadas:**

| Funcionalidad | Estado |
| :--- | :--- |
| 
| Comunicación por sockets TCP | ✅ Completado |
| Transferencia de archivos (< 10 MB) | ✅ Completado |
| Verificación de integridad SHA-256 | ✅ Completado |
| Logging de eventos en archivo | ✅ Completado |
| Conexión por misma red Wi-Fi | ✅ Completado |
| Conexión por Hotspot | ✅ Completado |
| Visualización formateada en consola | ✅ Completado |

---

##  Estructura del Proyecto

```
Chat Wifi/
├── README.md               ← Este archivo
├── requirements.txt        ← Guía de instalación y uso
├── CHANGELOG.md            ← Historial de cambios
├── .gitignore              ← Archivos excluidos del repositorio
│
├── src/                    ← CÓDIGO FUENTE
│   ├── server_chat.py      ← Servidor TCP (escucha conexiones)
│   ├── client_chat.py      ← Cliente TCP (se conecta al servidor)
│   ├── file_transfer.py    ← Lógica de hash y metadatos
│   └── utils.py            ← Funciones auxiliares reutilizables
│
├── docs/                   ← DOCUMENTACIÓN TÉCNICA
│   ├── THEORY.md           ← Teoría de sockets, TCP vs UDP, NAT
│   ├── DECISION.md         ← Decisiones técnicas y problemas resueltos
│   └── LEARNED_PYTHON.md   ← Conceptos de Python aprendidos
│
├── images/
│   └── tests/              ← Capturas de pantalla de pruebas
│
├── results/
│   ├── logs/               ← Logs de ejecución (.log)
│   └── received/           ← Archivos recibidos en transferencias
```

##  Requisitos

### Software
- **Python 3.8 o superior** (sin paquetes externos)
- Windows 10+, Linux o macOS

### Hardware
- Dos laptops con Wi-Fi
- Acceso a una red Wi-Fi común o capacidad de crear hotspot

### Seguridad
-  Este proyecto transmite mensajes en **texto plano** (sin cifrado)
- Usar solo en redes privadas
- Cerrar el hotspot después de las pruebas


##  Instalación y Ejecución

### Paso 1: Iniciar el Servidor

En la **Laptop A** (servidor), abre una terminal y ejecuta:

```bash
python src/server_chat.py --port 5000
```

**Salida esperada:**
```
==================================================
  SERVIDOR DE CHAT PUNTO A PUNTO - Wi-Fi
==================================================
  [Estado] ESCUCHANDO
  [Direccion] 0.0.0.0:5000
  [IP Local] 192.168.1.65
--------------------------------------------------
  Esperando conexion entrante...
==================================================
```

> **Anota la IP Local** (ej. `192.168.1.65`). La necesitarás para el cliente.

> Si el Firewall de Windows pregunta, selecciona **"Permitir acceso"**.

---

### Paso 2: Conectar el Cliente

En la **Laptop B** (cliente), abre una terminal y ejecuta:

```bash
python src/client_chat.py --host <IP_DEL_SERVIDOR> --port 5000
```

**Ejemplo real:**
```bash
python src/client_chat.py --host 192.168.1.65 --port 5000
```

**Salida esperada:**
```
==================================================
  CLIENTE DE CHAT PUNTO A PUNTO - Wi-Fi
==================================================
  [Conectando a] 192.168.1.65:5000
  [Estado] CONECTADO
--------------------------------------------------
  Comandos disponibles:
    mensaje        Enviar texto al servidor
    /enviar RUTA   Enviar archivo al servidor
    salir          Finalizar chat
==================================================
  [TU] > _
```

---

### Paso 3: Chatear

Escribe mensajes en cualquiera de las dos laptops y presiona **Enter**.

```
  [TU] > Hola, ¿cómo estás?
  [SERVIDOR] Bien, probando el chat punto a punto
  [TU] > ¡Funciona perfectamente!
```

Para salir, escribe:
```
  [TU] > salir
```

---

### Paso 4: Transferir Archivos (Opcional)

**Limitación:** Solo archivos **menores a 10 MB**.

Desde el **cliente**, usa el comando `/enviar` seguido de la ruta del archivo:

```bash
  [TU] > /enviar C:\Users\TuNombre\Desktop\documento.pdf
```

**También puedes arrastrar el archivo directamente a la terminal CMD** y la ruta se pegará automáticamente:

```bash
  [TU] > /enviar "C:\Users\TuNombre\Desktop\arrastrado_aqui.pdf"
```

**Progreso en pantalla:**
```
--------------------------------------------------
  ENVIANDO ARCHIVO
==================================================
  [Nombre] documento.pdf
  [Tamaño] 2.3 MB
  [Hash SHA256] a1b2c3d4e5f6...
--------------------------------------------------
  [Servidor] Listo para recibir
  [PROGRESO] 100% (2.3 MB / 2.3 MB)
  [Resultado] OK_VERIFIED
  [Transferencia] EXITOSA - Archivo verificado por el servidor
```

**El archivo se guarda en:** `results/received/documento.pdf`


##  Métodos de Conexión

### Método 1: Misma Red Wi-Fi (Recomendado para casas)

1. Conecta **ambas laptops al mismo router** Wi-Fi.
2. Ejecuta `ipconfig` en la laptop servidora para obtener su IP.
3. Usa esa IP en el cliente.

**Limitación:** Algunos routers universitarios bloquean la comunicación entre dispositivos (Client Isolation).

---

### Método 2: Hotspot (Alternativa confiable)

1. En la laptop servidora, ejecuta:
   ```bash
   scripts/create_hotspot_win.bat
   ```
2. Sigue las instrucciones para crear la red `ChatWiFi`.
3. Conecta la laptop cliente a esa red Wi-Fi.
4. La IP del servidor será `192.168.137.1` (Windows).

**Ventaja:** No depende de routers externos. Funciona en cualquier lugar.


##  Solución de Problemas

| Error | Causa probable | Solución |
| :--- | :--- | :--- |
| `ConnectionRefusedError` | El servidor no está corriendo o firewall bloquea | Verifica que el servidor esté iniciado y el firewall permita el puerto 5000 |
| `Connection timed out` | IP incorrecta o redes diferentes | Ejecuta `ipconfig` en el servidor y verifica la IP |
| `UnicodeEncodeError` | Caracteres especiales en CMD | Usa la versión más reciente del código (corregida) |
| `FileNotFoundError` al usar `/enviar` | Ruta con espacios sin comillas | Usa comillas: `"C:\Mi Carpeta\archivo.pdf"` |
| Archivo no se transfiere | Archivo > 10 MB | Comprime el archivo o divídelo |
| Cliente no recibe mensajes | Modo carácter de Telnet | Usa `client_chat.py`, no Telnet para pruebas |

---

##  Documentación

Toda la documentación técnica se encuentra en la carpeta `docs/`:

| Documento | Contenido |
| :--- | :--- |
| [`THEORY.md`](docs/THEORY.md) | Fundamentos teóricos: sockets, TCP vs UDP, NAT, firewalls |
| [`DECISION.md`](docs/DECISION.md) | Decisiones técnicas: método híbrido, problemas resueltos, comandos |
| [`LEARNED_PYTHON.md`](docs/LEARNED_PYTHON.md) | Bitácora de aprendizaje: funciones, conceptos y buenas prácticas |


## Licencia

Este proyecto es de uso exclusivamente académico para la materia de Programacion Avanzada.

