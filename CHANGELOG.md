# Changelog - Chat Punto a Punto Wi-Fi

Todos los cambios significativos del proyecto serán documentados en este archivo.


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

