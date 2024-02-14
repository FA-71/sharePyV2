import socket
import threading
import logging

from server import Server
from client import Client
from constants import *
from keys import Keys
from utils import check_network
from peerDeviceManager import PeerDeviceManager


logging.basicConfig(level=logging.DEBUG)

def main():
    network_status = check_network()
    if not network_status:
        print("not connected to a network")
        exit()

    # generate key pair
    key_pair = Keys()

    # start the peer manager
    peer_device_manager = PeerDeviceManager(key_pair) 
    peer_manager_listener = threading.Thread(target=peer_device_manager.peer_manager_listener)
    peer_manager_listener.start()

    # start the broadcast listener 
    server = Server(key_pair, peer_device_manager)
    broadcast_listener_thread = threading.Thread(target=server.start_broadcast_listener)
    broadcast_listener_thread.start()

    # start broadcast thread
    client = Client() 
    broadcast_thread = threading.Thread(target=client.broadcast_self)
    broadcast_thread.start()

    broadcast_listener_thread.join()
    broadcast_thread.join()


if __name__ == "__main__":
    main()