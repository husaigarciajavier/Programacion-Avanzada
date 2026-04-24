import socket
import os
import logging
import sys
import io
from file_transfer import calculate_sha256

# Forzar UTF-8 en consola Windows (por si acaso)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIVED_DIR = os.path.join(BASE_DIR, "results", "received")
LOGS_DIR = os.path.join(BASE_DIR, "results", "logs")
os.makedirs(RECEIVED_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'server.log')),
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

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.BUFFER_SIZE = 4096

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(1)
            
            # --- PANTALLA DE INICIO ---
            print_header("SERVIDOR DE CHAT PUNTO A PUNTO - Wi-Fi")
            print_info("Estado", "ESCUCHANDO")
            print_info("Direccion", f"{self.host}:{self.port}")
            print_info("IP Local", self.get_local_ip())
            print_separator("-")
            print_info("Esperando conexion entrante...")
            print_info("Presiona Ctrl+C para detener el servidor")
            print_separator("=")
            
            logging.info(f"[OK] Servidor escuchando en {self.host}:{self.port}")
            
            conn, addr = s.accept()
            with conn:
                # --- PANTALLA DE CONEXION ESTABLECIDA ---
                print(f"\n  >>> CLIENTE CONECTADO <<<")
                print_info("IP Cliente", f"{addr[0]}")
                print_info("Puerto Cliente", f"{addr[1]}")
                print_separator()
                print_info("Chat iniciado. Escribe mensajes o espera archivos.")
                print_info("Comandos disponibles:")
                print_info("  salir", "Finalizar chat")
                print_separator("=")
                
                logging.info(f"[OK] Conexion desde {addr}")
                
                while True:
                    data = conn.recv(self.BUFFER_SIZE)
                    if not data:
                        print("\n  [*] Cliente desconectado.")
                        break
                    
                    try:
                        message = data.decode('utf-8')
                        
                        if message.startswith("FILE_CMD|"):
                            self.handle_file_reception(conn, message)
                            print_info("Listo para continuar", "")
                            print_separator("-")
                        else:
                            print(f"\n  [CLIENTE] {message}")
                            print(f"  [TU] ", end='', flush=True)
                            logging.info(f"[<<<] {message}")
                    except UnicodeDecodeError:
                        continue

    def handle_file_reception(self, conn, header):
        try:
            _, name, size, client_hash = header.split('|')
            size = int(size)
            save_path = os.path.join(RECEIVED_DIR, name)

            conn.sendall(b"READY")
            
            # --- PANTALLA DE RECEPCION DE ARCHIVO ---
            print_separator("-")
            print_header("ARCHIVO ENTRANTE")
            print_info("Nombre", name)
            print_info("Tamaño", format_size(size))
            print_info("Hash SHA256", f"{client_hash[:32]}...")
            print_separator("-")
            print_info("Recibiendo datos...", "")
            
            logging.info(f"[*] Recibiendo archivo: {name} ({size} bytes)")
            
            with open(save_path, "wb") as f:
                remaining = size
                while remaining > 0:
                    chunk = conn.recv(min(remaining, self.BUFFER_SIZE))
                    if not chunk:
                        break
                    f.write(chunk)
                    remaining -= len(chunk)

            # Verificación de integridad
            server_hash = calculate_sha256(save_path)
            
            print_header("VERIFICACION DE INTEGRIDAD")
            print_info("Hash recibido", f"{client_hash[:32]}...")
            print_info("Hash calculado", f"{server_hash[:32]}...")
            
            if server_hash == client_hash:
                print_info("Resultado", "EXITOSO - Los hashes coinciden")
                conn.sendall(b"OK_VERIFIED")
                logging.info(f"[OK] Archivo {name} verificado correctamente")
            else:
                print_info("Resultado", "ERROR - Los hashes NO coinciden")
                conn.sendall(b"ERR_HASH")
                logging.error(f"[!] Hash no coincide para {name}")
            
            print_info("Guardado en", save_path)
            print_separator("=")
                
        except Exception as e:
            print_info("ERROR", f"Transferencia fallida: {e}")
            logging.error(f"Error en transferencia: {e}")

    def get_local_ip(self):
        """Obtiene la direccion IP local de la maquina."""
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except:
            try:
                temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                temp_socket.connect(("8.8.8.8", 80))
                local_ip = temp_socket.getsockname()[0]
                temp_socket.close()
                return local_ip
            except:
                return "No disponible"

if __name__ == "__main__":
    ChatServer().start()