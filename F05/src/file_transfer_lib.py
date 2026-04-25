import hashlib
import os

def calculate_sha256(file_path):
    """Calcula el hash SHA-256 de un archivo por bloques."""
    sha256_hash = hashlib.sha256()
    try:
        if not os.path.exists(file_path): return None
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def get_file_metadata(file_path):
    """Obtiene metadatos. Si el archivo no existe, retorna None para evitar bloqueos."""
    if not os.path.exists(file_path):
        return None
    return {
        "name": os.path.basename(file_path),
        "size": os.path.getsize(file_path),
        "checksum": calculate_sha256(file_path)
    }

def asegurar_ruta_destino():
    """Crea y retorna la ruta absoluta de results/received."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base_dir, "results", "received")
    os.makedirs(ruta, exist_ok=True)
    return ruta