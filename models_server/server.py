import socket
import threading

class SocketServer:
    def __init__(self, host, port, request_handler):
        self.host = host
        self.port = port
        self.request_handler = request_handler
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on {self.host}:{self.port}...")
        self.accept_connections()
    
    def accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection established with {client_address}")
            threading.Thread(target=self.request_handler.handle_client, args=(client_socket,)).start()
