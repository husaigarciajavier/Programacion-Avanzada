import socket
import threading
import logging
import argparse
import os
from datetime import datetime

# Crear carpeta de logs si no existe
os.makedirs('results/logs', exist_ok=True)

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('results/logs/client.log'),
        logging.StreamHandler()
    ]
)

class ChatClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.client_socket = None
        self.running = False
        
    def connect(self):
        """Conecta al servidor."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.running = True
            
            logging.info(f"[OK] Conectado al servidor {self.host}:{self.port}")
            
            self.chat_loop()
            
        except ConnectionRefusedError:
            logging.error(f"[ERROR] No se pudo conectar a {self.host}:{self.port}. Asegurate de que el servidor este ejecutandose.")
        except socket.gaierror:
            logging.error(f"[ERROR] Direccion IP invalida: {self.host}")
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
                    logging.info("[*] Chat finalizado por el cliente")
                    break
                    
                if message.strip():
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    full_message = f"[{timestamp}] Cliente: {message}"
                    self.client_socket.send(full_message.encode('utf-8'))
                    logging.info(f"[>>>] {message}")
                    
        except (ConnectionResetError, BrokenPipeError):
            logging.warning("[!] Servidor desconectado inesperadamente")
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        finally:
            self.stop()
    
    def receive_messages(self):
        """Recibe mensajes del servidor en un hilo separado."""
        try:
            while self.running:
                data = self.client_socket.recv(1024)
                
                if not data:
                    logging.info("[*] Servidor cerro la conexion")
                    self.running = False
                    break
                    
                message = data.decode('utf-8')
                print(f"\n{message}")
                print("Tu: ", end='', flush=True)
                logging.info(f"[<<<] {message}")
                
        except (ConnectionResetError, ConnectionAbortedError):
            logging.info("[*] Servidor desconectado")
        except Exception as e:
            logging.error(f"[ERROR] {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Detiene el cliente y cierra la conexion."""
        self.running = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
                
        logging.info("[*] Cliente desconectado")

def main():
    parser = argparse.ArgumentParser(description='Cliente de Chat Punto a Punto')
    parser.add_argument('--host', default='127.0.0.1', help='Direccion IP del servidor')
    parser.add_argument('--port', type=int, default=5000, help='Puerto del servidor')
    
    args = parser.parse_args()
    
    client = ChatClient(host=args.host, port=args.port)
    client.connect()

if __name__ == "__main__":
    main()