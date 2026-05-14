"""
Generador de IDs únicos para vehículos
"""

import uuid
from datetime import datetime

class GeneradorID:
    """Clase para generar identificadores únicos"""
    
    @staticmethod
    def generar_id_unico():
        """
        Genera un ID único usando UUID.
        Retorna un string con formato simplificado (primeros 8 caracteres + timestamp)
        """
        # Combinar UUID con timestamp para mayor unicidad
        uuid_parte = str(uuid.uuid4()).split('-')[0]  # Primeros 8 caracteres del UUID
        timestamp_parte = datetime.now().strftime("%H%M%S%f")[:-3]  # Hora + microsegundos
        
        id_completo = f"{uuid_parte}-{timestamp_parte}"
        return id_completo
    
    @staticmethod
    def generar_id_numerico():
        """
        Genera un ID numérico incremental (alternativa más simple)
        Nota: Requiere mantener un contador externo
        """
        import time
        return int(time.time() * 1000)  # Timestamp en milisegundos
    
    @staticmethod
    def generar_id_corto():
        """
        Genera un ID corto de 6 caracteres alfanuméricos
        Útil para mostrar al usuario
        """
        import random
        import string
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(random.choices(caracteres, k=6))