import socket
import threading
import logging

from server import Server
from client import Client
from constants import *

logging.basicConfig(level=logging.DEBUG)

def main():
    server = Server()
    broadcast_listener_thread = threading.Thread(target=server.start_broadcast_listener)
    broadcast_listener_thread.start()

    client = Client() 
    device_identifier_thread = threading.Thread(target=client.start_identifier)
    device_identifier_thread.start()

    client_thread = threading.Thread(target=client.broadcast_self)
    client_thread.start()

    broadcast_listener_thread.join()
    client_thread.join()


if __name__ == "__main__":
    main()