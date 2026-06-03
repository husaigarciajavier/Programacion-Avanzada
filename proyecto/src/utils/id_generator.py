"""
Generador de IDs únicos para vehículos
"""

import uuid
import random
import string
from datetime import datetime

class GeneradorID:
    """Clase para generar identificadores únicos"""
    
    @staticmethod
    def generar_id_unico():
        """Formato: a1b2c3d4-143052123"""
        uuid_parte = str(uuid.uuid4()).split('-')[0]
        timestamp_parte = datetime.now().strftime("%H%M%S%f")[:-3]
        return f"{uuid_parte}-{timestamp_parte}"
    
    @staticmethod
    def generar_id_corto():
        """Ejemplo: 3F9K2L"""
        caracteres = string.ascii_uppercase + string.digits
        return ''.join(random.choices(caracteres, k=6))
    
    @staticmethod
    def generar_id_numerico():  # NUEVO MÉTODO
        """Ejemplo: 1623456789123"""
        return int(datetime.now().timestamp() * 1000)
    
    @staticmethod
    def validar_id(id_string):  # NUEVO MÉTODO
        """Valida formato de ID"""
        if not id_string or len(id_string) < 6:
            return False
        tiene_guion = '-' in id_string
        es_alfanumerico = id_string.replace('-', '').isalnum()
        return es_alfanumerico and (len(id_string) >= 6)