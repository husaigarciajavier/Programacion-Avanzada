import socket
import os
import argparse
from file_transfer_lib import get_file_metadata

def start_client(host, port):
    BUFFER_SIZE = 4096
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print(f"[*] Conectando a {host}:{port}...")
            s.connect((host, port))
            print("[OK] Conexión establecida.")
            print("Instrucciones: Escribe para chatear o '/enviar ruta_del_archivo'")
            
            while True:
                msg = input("Tu: ")
                if not msg: continue
                if msg.lower() == 'salir': break
                
                if msg.startswith('/enviar '):
                    path = msg.split(' ', 1)[1].strip()
                    meta = get_file_metadata(path)
                    
                    if not meta:
                        print(f"[!] ERROR: El archivo '{path}' no existe o es inaccesible.")
                        continue
                        
                    # Enviar comando de archivo
                    header = f"FILE_CMD|{meta['name']}|{meta['size']}|{meta['checksum']}"
                    s.sendall(header.encode('utf-8'))
                    
                    # Esperar READY
                    s.settimeout(10)
                    ack = s.recv(1024).decode('utf-8')
                    if ack == "READY":
                        print(f"[*] Enviando {meta['name']}...")
                        with open(path, "rb") as f:
                            s.sendall(f.read())
                        
                        resultado = s.recv(1024).decode('utf-8')
                        print(f"[SISTEMA] Servidor: {resultado}")
                    s.settimeout(None)
                else:
                    s.sendall(msg.encode('utf-8'))
        except ConnectionRefusedError:
            print("[!] Error: Servidor no disponible. Verifica la IP y el Puerto.")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    start_client(args.host, args.port)