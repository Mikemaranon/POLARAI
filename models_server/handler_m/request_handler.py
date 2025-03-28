class RequestHandler:
    def __init__(self, processor):
        self.processor = processor

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                response = self.processor.process_message(data.decode())
                client_socket.sendall(response.encode())

        except Exception as e:
            print(f"Error manejando cliente: {e}")
        finally:
            client_socket.close()
            print("Conexión cerrada.")