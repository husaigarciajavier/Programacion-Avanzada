import socket
import threading
import logging
import argparse
import os
from datetime import datetime

# Crear carpeta de logs si no existe
os.makedirs('results/logs', exist_ok=True)

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('results/logs/server.log'),
        logging.StreamHandler()
    ]
)

class ChatServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.running = False
        
    def start(self):
        """Inicia el servidor y espera una conexión entrante."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            self.running = True
            
            logging.info(f"[OK] Servidor escuchando en {self.host}:{self.port}")
            logging.info(f"[IP] Tu direccion IP local es: {self.get_local_ip()}")
            logging.info("[*] Esperando conexion de un cliente...")
            
            self.client_socket, self.client_address = self.server_socket.accept()
            logging.info(f"[OK] Cliente conectado desde {self.client_address[0]}:{self.client_address[1]}")
            
            self.chat_loop()
            
        except KeyboardInterrupt:
            logging.info("[*] Servidor detenido por el usuario")
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        finally:
            self.stop()
    
    def chat_loop(self):
        """Bucle principal del chat."""
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        print("\n" + "="*50)
        print("CHAT INICIADO - Escribe '-salir-' para terminar")
        print("="*50 + "\n")
        
        try:
            while self.running:
                message = input("Tu: ")
                
                if message.lower() == '-salir-':
                    logging.info("[*] Chat finalizado por el servidor")
                    break
                    
                if message.strip():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] Servidor: {message}"
                    self.client_socket.send(full_message.encode('utf-8'))
                    logging.info(f"[>>>] {message}")
                    
        except (ConnectionResetError, BrokenPipeError):
            logging.warning("[!] Cliente desconectado inesperadamente")
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        finally:
            self.stop()
    
    def receive_messages(self):
        """Recibe mensajes del cliente en un hilo separado."""
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                
                if not data:
                    logging.info("[*] Cliente cerro la conexion")
                    self.running = False
                    break
                    
                message = data.decode('utf-8')
                print(f"\n{message}")
                print("Tu: ", end='', flush=True)
                logging.info(f"[<<<] {message}")
                
        except (ConnectionResetError, ConnectionAbortedError):
            logging.info("[*] Cliente desconectado")
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        finally:
            self.running = False
    
    def get_local_ip(self):
        """Obtiene la direccion IP local de la maquina."""
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_socket.connect(("8.8.8.8", 80))
            local_ip = temp_socket.getsockname()[0]
            temp_socket.close()
            return local_ip
        except:
            return "No disponible (ejecuta ipconfig)"
    
    def stop(self):
        """Detiene el servidor y cierra conexiones."""
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        logging.info("[*] Servidor detenido")

def main():
    parser = argparse.ArgumentParser(description='Servidor de Chat Punto a Punto')
    parser.add_argument('--host', default='0.0.0.0', help='Direccion IP del servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto de escucha')
    
    args = parser.parse_args()
    
    server = ChatServer(host=args.host, port=args.port)
    server.start()

if __name__ == "__main__":
    main()