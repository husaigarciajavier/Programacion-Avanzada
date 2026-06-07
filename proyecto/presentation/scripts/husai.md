# Guion - Husai ( minutos)
## Constantes + GUI + Inscripción de placas + Optimización v1.1

Yo trabajé en los archivos configurables, la interfaz gráfica completa y la optimización del sistema.

Centralicé todas las constantes del sistema en constants.py para que sean fácilmente modificables. El usuario puede cambiar la capacidad y el precio desde la interfaz, y config_manager.py guarda esos cambios en un JSON sin necesidad de reiniciar la aplicación.

La ventana de registro de vehículos valida la placa, asigna un ID único y verifica espacios disponibles.

La ventana principal muestra toda la información en tiempo real.

Además de optimizar la mayoría de códigos, en total, se redujo el código en un 39%, pasando de aproximadamente 2500 líneas a 1500 líneas.

También implementé el redondeo hacia arriba para el cobro. Si un vehículo estuvo 1 hora con 3 minutos, se cobran 2 horas completas.