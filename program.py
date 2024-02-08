import socket
import threading

from server import Server
from client import Client
from constants import *


def main():
    server = Server()
    broadcast_listener_thread = threading.Thread(target=server.start_broadcast_listener)
    broadcast_listener_thread.start()

    if (input("enter y: ") == "y"): 
        client = Client() 
        client_thread = threading.Thread(target=client.broadcast_self)
        client_thread.start()

    broadcast_listener_thread.join()
    client_thread.join()


if __name__ == "__main__":
    main()