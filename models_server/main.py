import socket
from server import SocketServer
from handler_m.request_handler import RequestHandler
from handler_m.message_processor import MessageProcessor

IP = "100.104.64.29"
PORT = 5001

if __name__ == "__main__":
    processor = MessageProcessor()
    handler = RequestHandler(processor)
    server = SocketServer(IP, PORT, handler)
    server.start()
