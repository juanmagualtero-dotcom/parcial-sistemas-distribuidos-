import socket
import os
from datetime import datetime

# UDP_HOST = "0.0.0.0"
UDP_HOST = 'localhost'
UDP_PORT = int(os.getenv("UDP_PORT", 9001))

def iniciar_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
        udp_sock.bind((UDP_HOST, UDP_PORT))
        print(f"[UDP] Servidor de notificaciones escuchando en {UDP_HOST}:{UDP_PORT}")

        while True:
            datos, origen = udp_sock.recvfrom(1024)
            mensaje = datos.decode().strip()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Notificación de {origen}: {mensaje}")

if __name__ == "__main__":
    iniciar_listener()
