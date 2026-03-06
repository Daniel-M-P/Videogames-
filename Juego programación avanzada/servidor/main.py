import socket
import json
import threading

class Servidor:
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.sockets = []

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Servidor escuchando en {self.host}:{self.port}")

    def start(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Conexión establecida con {addr}")
            self.sockets.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            mensaje = json.loads(data.decode('utf-8'))
            self.procesar_mensaje(mensaje, client_socket)

    def procesar_mensaje(self, mensaje, client_socket):
        # Lógica para procesar y verificar el puzzle
        pass

if __name__ == "__main__":
    servidor = Servidor()
    servidor.start()
