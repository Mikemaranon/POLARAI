import socket
import threading

class Server:
    def __init__(self, server_socket, host, port):
        # Guardar la instancia del socket y la IP/puerto
        self.server_socket = server_socket
        self.host = host
        self.port = port
        
        # Configurar el socket para escuchar conexiones entrantes
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)  # Número de conexiones permitidas en espera
        print(f"Server listening on {self.host}:{self.port}...")

        # Iniciar el hilo de escucha
        self.start_server()

    def start_server(self):
        # Usamos un hilo para manejar las conexiones entrantes de manera concurrente
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.daemon = True
        accept_thread.start()

    def accept_connections(self):
        # Aceptar las conexiones entrantes
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection established with {client_address}")
            
            # Crear un hilo para manejar la comunicación con el cliente
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()

    def handle_client(self, client_socket):
        # Aquí gestionas la comunicación con el cliente
        try:
            while True:
                # Recibir datos del cliente
                data = client_socket.recv(1024)  # Tamaño del buffer
                if not data:
                    break  # Si no hay datos, cerramos la conexión
                
                print(f"Received data: {data.decode()}")

                # Aquí puedes realizar cualquier procesamiento con los datos que recibas
                # Por ejemplo, puedes enviar el mensaje al modelo o realizar alguna operación.
                
                # Responder al cliente con un mensaje
                response = "Message received successfully"
                client_socket.sendall(response.encode())
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            # Cerrar la conexión al cliente
            client_socket.close()
            print("Connection closed.")

