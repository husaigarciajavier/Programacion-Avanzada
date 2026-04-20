# Conceptos fundamentales de redes y sockets

## ¿Qué es un socket?

Un **socket** es un punto final de una conexión de red bidireccional entre dos aplicaciones (cliente-servidor o peer-to-peer). Actúa como una "puerta" por la que entra y sale la información a través de la red usando direcciones IP y puertos.

## TCP vs UDP

| Característica | TCP | UDP |
|---------------|-----|-----|
| Conexión | Orientado a conexión (handshake) | Sin conexión |
| Fiabilidad | Entrega garantizada, retransmisiones | No garantiza entrega |
| Orden de datos | Mantiene el orden | Puede desordenarse |
| Control de flujo | Sí | No |
| Velocidad | Más lento | Más rápido |
| Cabecera | 20 bytes | 8 bytes |

### Ventajas y cuándo usarlos

**TCP:**
- **Ventajas:** Confiable, ordenado, control de congestión.
- **Cuándo usar:** Web (HTTP), email (SMTP, POP3), transferencia de archivos (FTP), SSH, bases de datos.

**UDP:**
- **Ventajas:** Baja latencia, sin overhead de conexión.
- **Cuándo usar:** Streaming en vivo, VoIP, DNS, juegos en tiempo real, DHCP, broadcast.

## Puertos y direcciones IP

- **Dirección IP:** Identifica un dispositivo en la red (IPv4: 192.168.1.1, IPv6: 2001:db8::1).
- **Puerto:** Número (0-65535) que identifica un proceso/aplicación en ese dispositivo.

### Puertos bien conocidos (0-1023)
Asignados a servicios estándar del sistema (requieren privilegios de administrador):
| Puerto | Servicio |
|--------|----------|
| 20,21 | FTP |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 3306 | MySQL |

### Puertos dinámicos/privados (49152-65535)
Usados temporalmente por aplicaciones cliente. El sistema operativo los asigna automáticamente cuando un programa inicia una conexión saliente.

## NAT y problemas de conectividad

**NAT (Network Address Translation)** permite que múltiples dispositivos en una red privada (ej: 192.168.x.x) compartan una única IP pública.

### Problemas comunes:
- **Imposibilidad de conexión entrante:** Un dispositivo interno no puede recibir conexiones directamente desde internet.
- **Hole punching:** Técnica para atravesar NAT en P2P.
- **Port forwarding:** Solución manual abriendo puertos en el router.
- **NAT traversal:** UPnP, STUN/TURN (usado en WebRTC, juegos).

> Para conectar dos redes distintas tras NAT sin configuración, se necesita un servidor intermediario o técnicas como NAT traversal.

---

## Firewalls y permisos de puerto

Un firewall filtra tráfico basado en reglas (puerto, IP, protocolo).

### Permisos típicos:
- **Permitir:** Puertos específicos para servicios necesarios (80, 443, 22).
- **Denegar:** Puertos de alto riesgo (135-139, 445, 1433, 3389).
- **Estado:** Permite tráfico relacionado con conexiones establecidas (estado `ESTABLISHED`).

### En desarrollo:
- Desactivar firewall local durante pruebas solo en entornos aislados.
- En producción, usar reglas específicas y firewalls de aplicación (WAF).


## Wi‑Fi Direct vs Hotspot vs Misma red

| Tecnología | Descripción | Limitaciones |
|------------|-------------|---------------|
| **Misma red** | Dispositivos conectados al mismo router/AP | Depende del router, alcance limitado por el AP |
| **Hotspot** | Un dispositivo crea una red Wi‑Fi que otros usan para salir a internet | Solo el anfitrión tiene datos; consume batería; desconexión si el anfitrión se mueve |
| **Wi‑Fi Direct** | Conexión directa peer-to-peer sin router ni internet | Compatibilidad mixta; alcance limitado (típico <100m); configuración más compleja |

### Diferencias clave:
- **Misma red:** Necesitan un punto de acceso común.
- **Hotspot:** Un dispositivo provee internet a los demás.
- **Wi‑Fi Direct:** Comunicación directa entre dos dispositivos, sin internet y sin router.

## Seguridad básica: TLS/SSL

### TLS (Transport Layer Security) - sucesor de SSL
Cifra la comunicación entre cliente y servidor, evitando escuchas, manipulaciones o suplantaciones.

### Recomendaciones para pruebas:
1. **Usa siempre TLS en producción** (nunca HTTP plano).
2. **Certificados autofirmados** solo para pruebas locales (aceptar advertencia del navegador).
3. **No deshabilitar la verificación de certificados** en código de producción.

### Advertencias:
- TLS no protege contra todas las amenazas (solo cifra el canal).
- En pruebas, evita exponer servicios sin TLS a redes no confiables.
- Usa TLS 1.2 o superior; desactiva SSLv3, TLS 1.0 y 1.1.