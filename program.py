import socket
import threading
import logging

from server import Server
from client import Client
from constants import *
from keys import Keys
from utils import check_network


logging.basicConfig(level=logging.DEBUG)

def main():
    network_status = check_network()
    if not network_status:
        print("not connected to a network")
        exit()

    # generate key pair
    key_pair = Keys()

    server = Server(key_pair)
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