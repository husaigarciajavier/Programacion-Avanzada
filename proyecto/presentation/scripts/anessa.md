# Guion - Anessa ( minutos)
## Estructura de carpetas + Integración base de datos

Buenos días. Presentamos el Sistema de Gestión de Estacionamiento, desarrollado en Python con interfaz gráfica Tkinter. El sistema permite registrar vehículos, controlar tiempos de estadía, procesar pagos con redondeo hacia arriba y generar reportes diarios con persistencia en JSON.

Yo fui responsable de la estructura del proyecto y la integración con la base de datos.

Organicé el proyecto en una estructura de capas para mantener el código limpio y mantenible. La separación en config, database, models, ui y utils permite que cada módulo sea independiente. Si alguien quiere modificar la interfaz, no afecta la base de datos. Si cambia la lógica de negocio, no afecta la interfaz.

Para mantener un orden, implementé un sistema basado en archivos JSON. Cada día se genera un archivo diferente. Los datos se guardan automáticamente después de cada ingreso o salida, y se recuperan al iniciar la aplicación. También implementé un sistema de guardados automáticos.