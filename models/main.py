import socket
import server

socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = '100.104.64.29'
PORT = '5001'

if __name__ == "__main__":
    server = server.Server(socket_server, IP, PORT)