"""
Utilidades para manejo de precios y cobros
"""

from src.config.constants import MIN_PRECIO, MAX_PRECIO

class PrecioUtils:
    """Clase con funciones auxiliares para manejo de precios"""
    
    @staticmethod
    def validar_precio(precio):
        try:
            precio_float = float(precio)
            return MIN_PRECIO <= precio_float <= MAX_PRECIO
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def formatear_precio(precio, moneda="MXN"):  # CAMBIADO
        """Ahora con moneda configurable"""
        return f"${float(precio):.2f} {moneda}"
    
    @staticmethod
    def formatear_precio_simple(precio):  # NUEVO MÉTODO
        """Formato sin moneda: $5.00"""
        return f"${float(precio):.2f}"
    
    @staticmethod
    def calcular_cobro(horas, precio_por_hora, redondear_arriba=True):
        import math
        
        if redondear_arriba:
            horas_cobradas = math.ceil(horas)
        else:
            horas_cobradas = horas
        
        if horas_cobradas < 1 and horas > 0:
            horas_cobradas = 1
        
        total = horas_cobradas * precio_por_hora
        
        return {
            'total': round(total, 2),
            'horas_cobradas': horas_cobradas,
            'detalle': f"{horas:.2f} horas → cobrando {horas_cobradas} horas"
        }
    
    @staticmethod
    def aplicar_descuento(total, porcentaje):  # NUEVO MÉTODO
        """Aplica descuento y retorna detalle"""
        descuento = total * (porcentaje / 100)
        return {
            'total_con_descuento': round(total - descuento, 2),
            'descuento_aplicado': round(descuento, 2)
        }