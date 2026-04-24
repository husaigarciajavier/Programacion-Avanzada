# Documento de Decisiones Técnicas (DECISION.md)

## Chat Punto a Punto Wi-Fi - Proyecto de Redes

---

## 1. Método de Conexión Elegido

### Decisión final: Uso combinado (Hotspot + Misma Red Wi-Fi)

Tras múltiples pruebas, se determinó que **ningún método único fue suficiente** para cubrir todos los escenarios. Se adoptó un **enfoque híbrido**:

| Fase | Método utilizado | Propósito |
| :--- | :--- | :--- |
| **Desarrollo y depuración** | Misma red local (router doméstico) | Probar código rápidamente con IP fija |
| **Prueba definitiva 1** | Hotspot creado desde Windows 10 | Garantizar conectividad directa sin intermediarios |
| **Prueba definitiva 2** | Misma red Wi-Fi (infraestructura) | Demostrar portabilidad del código |

### Justificación del enfoque combinado

Durante el desarrollo se enfrentaron los siguientes problemas:

1.  **Aislamiento de cliente (Client Isolation):** En redes universitarias y algunos routers modernos, los dispositivos conectados a la misma red Wi-Fi **no pueden verse entre sí**. Esto impedía la conexión TCP aunque ambas laptops estuvieran en la misma subred.

2.  **Firewall del router:** Algunos routers bloquean puertos no estándar (como el 5000) por defecto, impidiendo la comunicación incluso con IP correcta.

3.  **IP dinámica:** En redes con DHCP, la IP cambia entre sesiones, lo que obligaba a modificar el comando del cliente constantemente.

**Solución adoptada:** Usar **Hotspot** como método principal confiable y **misma red** como método alternativo documentado.

---

## 2. Ventajas y Limitaciones de Cada Método

### Hotspot (Punto de acceso móvil)

| Ventajas | Limitaciones |
| :--- | :--- |
| Conexión directa sin router intermediario | Requiere que una laptop tenga capacidad de crear hotspot |
| No hay aislamiento de cliente | Consume batería y recursos de la laptop anfitriona |
| Control total sobre IP y puertos | La IP del servidor suele ser fija (192.168.137.1 en Windows) |
| Funciona sin internet externo | No disponible en todas las versiones de Windows |
| Más seguro: red privada temporal | Requiere permisos de administrador en algunos SO |

### Misma Red Wi-Fi (Infraestructura)

| Ventajas | Limitaciones |
| :--- | :--- |
| Ambas laptops se conectan al router existente | Sujeto a aislamiento de cliente del router |
| No consume batería extra creando hotspot | La IP puede cambiar (DHCP) |
| Útil en entornos domésticos controlados | Firewall del router puede bloquear puertos |
| No requiere permisos especiales | Depende de la configuración del administrador de red |

---

## 3. Comandos Utilizados

### Windows 10/11 - Verificar IP local

```batch
ipconfig