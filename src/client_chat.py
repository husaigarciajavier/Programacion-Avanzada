import socket
import os
import sys
import io
import logging
from file_transfer import get_file_metadata

# Forzar UTF-8 en consola Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuración de rutas para logs
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, "results", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'client.log')),
        logging.StreamHandler()
    ]
)

def print_separator(char="=", length=50):
    """Imprime una línea separadora."""
    print(char * length)

def print_header(title):
    """Imprime un título formateado."""
    print_separator()
    print(f"  {title}")
    print_separator()

def print_info(label, value=""):
    """Imprime información con formato etiqueta: valor."""
    if value:
        print(f"  [{label}] {value}")
    else:
        print(f"  {label}")

def format_size(bytes_size):
    """Convierte bytes a formato legible."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = 4096

    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # --- PANTALLA DE CONEXION ---
            print_header("CLIENTE DE CHAT PUNTO A PUNTO - Wi-Fi")
            print_info("Conectando a", f"{self.host}:{self.port}")
            
            s.connect((self.host, self.port))
            
            print_info("Estado", "CONECTADO")
            print_separator("-")
            print_info("Comandos disponibles:")
            print_info("  mensaje", "Enviar texto al servidor")
            print_info("  /enviar RUTA", "Enviar archivo al servidor")
            print_info("  salir", "Finalizar chat")
            print_separator("=")
            
            while True:
                msg = input("  [TU] > ")
                
                if msg.lower() == 'salir':
                    print_info("Chat finalizado", "")
                    break
                
                if msg.startswith('/enviar '):
                    path = msg.split(' ', 1)[1]
                    self.send_file(s, path)
                    print_separator("-")
                elif msg.strip():
                    s.sendall(msg.encode('utf-8'))
                    logging.info(f"[>>>] {msg}")

    def send_file(self, sock, path):
        """Envia un archivo al servidor con barra de progreso."""
        meta = get_file_metadata(path)
        if not meta:
            print_info("ERROR", "Archivo no encontrado: " + path)
            return

        # --- PANTALLA DE ENVIO ---
        print_separator("-")
        print_header("ENVIANDO ARCHIVO")
        print_info("Nombre", meta['name'])
        print_info("Tamaño", format_size(meta['size']))
        print_info("Hash SHA256", f"{meta['checksum'][:32]}...")
        print_separator("-")

        header = f"FILE_CMD|{meta['name']}|{meta['size']}|{meta['checksum']}"
        sock.sendall(header.encode('utf-8'))
        logging.info(f"[FILE] Enviando encabezado: {meta['name']}")

        ack = sock.recv(1024).decode('utf-8')
        if ack == "READY":
            print_info("Servidor", "Listo para recibir")
            print_info("Enviando datos", "0%")
            
            # Lectura y envío con indicador de progreso
            with open(path, "rb") as f:
                file_data = f.read()
                total_size = len(file_data)
                chunk_size = 8192
                sent = 0
                
                for i in range(0, total_size, chunk_size):
                    chunk = file_data[i:i + chunk_size]
                    sock.sendall(chunk)
                    sent += len(chunk)
                    progress = int((sent / total_size) * 100)
                    print(f"\r  [PROGRESO] {progress}% ({format_size(sent)} / {format_size(total_size)})", end='', flush=True)
            
            print()  # Nueva línea después de la barra
            
            # Recibir resultado
            result = sock.recv(1024).decode('utf-8')
            print_info("Resultado", result)
            
            if result == "OK_VERIFIED":
                print_info("Transferencia", "EXITOSA - Archivo verificado por el servidor")
            else:
                print_info("Transferencia", "FALLIDA - Error de integridad")
            
            logging.info(f"[FILE] Resultado: {result}")

if __name__ == "__main__":
    ChatClient().connect()