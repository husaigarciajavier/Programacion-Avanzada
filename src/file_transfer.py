import hashlib
import os

def calculate_sha256(file_path):
    """Calcula la huella digital SHA-256 del archivo por bloques."""
    sha256_hash = hashlib.sha256() # Se inicializa el algoritmo SHA-256
    try:
        if not os.path.exists(file_path): return None
        with open(file_path, "rb") as f:
            # Lectura por bloques para evitar saturar la memoria RAM
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block) # El corazón del proceso: 64 rondas de mezcla
        return sha256_hash.hexdigest() # Retorna la cadena de 64 caracteres hexadecimales
    except Exception:
        return None

def get_file_metadata(file_path):
    """Prepara el nombre, tamaño y checksum para el encabezado."""
    if not os.path.exists(file_path):
        return None
    return {
        "name": os.path.basename(file_path),
        "size": os.path.getsize(file_path),
        "checksum": calculate_sha256(file_path)
        
    }