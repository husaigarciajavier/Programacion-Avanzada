import socket
import os
import argparse
from file_transfer_lib import calculate_sha256, asegurar_ruta_destino

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except: ip = '127.0.0.1'
    finally: s.close()
    return ip

def start_server(host, port):
    BUFFER_SIZE = 4096
    SAVE_PATH = asegurar_ruta_destino()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            s.listen(1)
            print(f"\n[*] SERVIDOR INICIADO")
            print(f"[*] IP Local para conectar: {get_local_ip()}")
            print(f"[*] Puerto: {port}")
            print(f"[*] Carpeta de destino: {SAVE_PATH}\n")
            
            conn, addr = s.accept()
            with conn:
                print(f"[OK] Cliente conectado desde {addr}")
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    if not data: break
                    
                    try:
                        msg = data.decode('utf-8', errors='ignore')
                        if msg.startswith("FILE_CMD|"):
                            # PROTOCOLO DE ARCHIVO
                            _, name, size, client_hash = msg.split('|')
                            size = int(size)
                            conn.sendall(b"READY")
                            
                            f_path = os.path.join(SAVE_PATH, name)
                            with open(f_path, "wb") as f:
                                received = 0
                                while received < size:
                                    chunk = conn.recv(min(BUFFER_SIZE, size - received))
                                    if not chunk: break
                                    f.write(chunk)
                                    received += len(chunk)
                            
                            server_hash = calculate_sha256(f_path)
                            if server_hash == client_hash:
                                print(f"[LOG] {name} recibido con éxito. SHA256 verificado.")
                                conn.sendall(b"OK_VERIFICADO")
                            else:
                                print(f"[!] Error de integridad en {name}")
                                conn.sendall(b"ERROR_HASH")
                        else:
                            print(f"\nCliente: {msg}\nTu: ", end='', flush=True)
                    except Exception as e:
                        print(f"\n[!] Error: {e}")
                        break
        except Exception as e:
            print(f"[CRÍTICO] No se pudo iniciar el servidor: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    start_server(args.host, args.port)