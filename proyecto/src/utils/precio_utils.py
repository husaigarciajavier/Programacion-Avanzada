"""
Utilidades para manejo de precios y cobros
"""

from src.config.constants import MIN_PRECIO, MAX_PRECIO

class PrecioUtils:
    """Clase con funciones auxiliares para manejo de precios"""
    
    @staticmethod
    def validar_precio(precio):
        """
        Valida que el precio esté dentro del rango permitido
        
        Args:
            precio: float a validar
        
        Returns:
            bool: True si es válido, False si no
        """
        try:
            precio_float = float(precio)
            return MIN_PRECIO <= precio_float <= MAX_PRECIO
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def formatear_precio(precio):
        """
        Formatea un precio a moneda
        
        Args:
            precio: float o int
        
        Returns:
            string: Precio formateado (ej: "$5.00 MXN")
        """
        return f"${round(float(precio), 2):.2f} MXN"
    
    @staticmethod
    def calcular_cobro(horas, precio_por_hora, fraccion_por_hora=True):
        """
        Calcula el cobro según el tiempo y política de fracciones
        
        Args:
            horas: float (horas de estadía)
            precio_por_hora: float
            fraccion_por_hora: bool (True = fracciones se cobran como hora completa)
        
        Returns:
            dict: {'total': float, 'horas_cobradas': float, 'detalle': str}
        """
        import math
        
        horas_cobradas = horas
        
        if fraccion_por_hora:
            # Redondear hacia arriba (cobrar hora completa aunque sea fracción)
            horas_cobradas = math.ceil(horas)
        
        # Asegurar mínimo 1 hora
        if horas_cobradas < 1 and horas > 0:
            horas_cobradas = 1
        
        total = horas_cobradas * precio_por_hora
        
        return {
            'total': round(total, 2),
            'horas_cobradas': horas_cobradas,
            'detalle': f"{horas} horas de estadía → cobrando {horas_cobradas} horas"
        }
    
    @staticmethod
    def aplicar_descuento(total, porcentaje):
        """
        Aplica un descuento al total
        
        Args:
            total: float
            porcentaje: float (ej: 10 = 10% de descuento)
        
        Returns:
            float: Total con descuento
        """
        descuento = total * (porcentaje / 100)
        return round(total - descuento, 2)