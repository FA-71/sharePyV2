import socket
import time
import threading
import logging

from message import BroadcastMessage
from config import DEVICE_IP
from constants import *
from keys import Keys
from peerDeviceManager import PeerDeviceManager


class Server: 
    def __init__ (self, key_pair: Keys, peer_manager: PeerDeviceManager): 
        self.client_ip_list = set()
        self.key_pair = key_pair
        self.peerManager = peer_manager
    
    def start_broadcast_listener(self):
        """
        listen to the broadcast msg from the other devices
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server: 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', BROADCAST_PORT))

            logging.debug("Server started. Waiting for devices...")

            while True:
                data, addr = server.recvfrom(1024)
                self._handle_broadcast_messages(addr, data)


    def _handle_broadcast_messages(self, addr, data):
        if addr[0] != DEVICE_IP:
            logging.debug(f"server: {addr} - {data}")

            # TODO: check if peerdevice is connected 
            if BroadcastMessage.check_message(data) and addr[0] not in self.peerManager.peer_ip_set:
                self.peerManager.handle_new_peer_ip(addr[0])