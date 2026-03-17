import socket
import threading
import os

# ─── Configuración ───────────────────────────────────────────────
TCP_HOST = "0.0.0.0"
TCP_PORT = int(os.getenv("TCP_PORT", 9000))
UDP_HOST = os.getenv("UDP_HOST", "localhost")
UDP_PORT = int(os.getenv("UDP_PORT", 9001))

# ─── Estado compartido ───────────────────────────────────────────
contador = 0
lock = threading.Lock()          # Sincronización del contador
clientes_activos = 0
clientes_lock = threading.Lock()

# ─── UDP: enviar notificación ─────────────────────────────────────
def notificar_udp(valor: int):
    """Envía una notificación UDP cada vez que el contador cambia."""
    mensaje = f"Evento: Contador actualizado a: {valor}"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sock:
            udp_sock.sendto(mensaje.encode(), (UDP_HOST, UDP_PORT))
        print(f"[UDP] Notificación enviada → {mensaje}")
    except Exception as e:
        print(f"[UDP] Error al notificar: {e}")

# ─── Manejo de cada cliente TCP ───────────────────────────────────
def manejar_cliente(conn: socket.socket, addr):
    global contador, clientes_activos

    with clientes_lock:
        clientes_activos += 1

    print(f"[TCP] Cliente conectado: {addr}  (activos: {clientes_activos})")
    conn.sendall(b"Bienvenido. Comandos: INCREMENTAR | CONSULTAR | SALIR\n")

    try:
        while True:
            datos = conn.recv(1024)
            if not datos:
                break

            comando = datos.decode().strip().upper()
            print(f"[TCP] {addr} → {comando}")

            if comando == "INCREMENTAR":
                with lock:
                    contador += 1
                    nuevo_valor = contador
                respuesta = f"OK: Contador incrementado. Nuevo valor: {nuevo_valor}\n"
                conn.sendall(respuesta.encode())
                notificar_udp(nuevo_valor)

            elif comando == "CONSULTAR":
                with lock:
                    valor_actual = contador
                respuesta = f"OK: Valor actual del contador: {valor_actual}\n"
                conn.sendall(respuesta.encode())

            elif comando == "SALIR":
                conn.sendall(b"Hasta luego.\n")
                break

            else:
                conn.sendall(b"ERROR: Comando no reconocido. Use INCREMENTAR | CONSULTAR | SALIR\n")

    except (ConnectionResetError, BrokenPipeError):
        print(f"[TCP] Cliente {addr} se desconectó abruptamente.")
    finally:
        conn.close()
        with clientes_lock:
            clientes_activos -= 1
        print(f"[TCP] Cliente desconectado: {addr}  (activos: {clientes_activos})")

# ─── Servidor principal ───────────────────────────────────────────
def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((TCP_HOST, TCP_PORT))
        servidor.listen(10)
        print(f"[TCP] Servidor escuchando en {TCP_HOST}:{TCP_PORT}")

        while True:
            conn, addr = servidor.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            hilo.start()

if __name__ == "__main__":
    iniciar_servidor()
