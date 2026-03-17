import socket
import os
import sys

# ─── Configuración ───────────────────────────────────────────────
# SERVER_HOST = os.getenv("SERVER_HOST", "tcp_server")
# SERVER_PORT = int(os.getenv("SERVER_PORT", 9000))

# para pruebas locales
SERVER_HOST = 'localhost'
SERVER_PORT = 9000


def iniciar_cliente():
    print(f"Conectando a {SERVER_HOST}:{SERVER_PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
            cliente.connect((SERVER_HOST, SERVER_PORT))
            print("[CONECTADO] Conexión exitosa con el servidor TCP.\n")

            # Bienvenida del servidor
            bienvenida = cliente.recv(1024).decode().strip()
            print(f"Servidor: {bienvenida}\n")

            while True:
                try:
                    comando = input("Ingresa comando (INCREMENTAR / CONSULTAR / SALIR): ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[INFO] Cerrando cliente...")
                    break

                if not comando:
                    continue

                try:
                    cliente.sendall(comando.encode())
                    respuesta = cliente.recv(1024).decode().strip()
                    print(f"Servidor: {respuesta}\n")
                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("[ERROR] Se perdió la conexión con el servidor.")
                    break

                if comando.upper() == "SALIR":
                    break

    except ConnectionRefusedError:
        print(f"[ERROR] No se pudo conectar a {SERVER_HOST}:{SERVER_PORT}. ¿Está el servidor activo?")
        sys.exit(1)
    except OSError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    print("[INFO] Cliente finalizado.")

if __name__ == "__main__":
    iniciar_cliente()
