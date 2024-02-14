import logging
import time
import socket
import threading
import selectors
from typing import Set 

from constants import COMMON_PORT
from config import DEVICE_IP
from keys import Keys
from peerDevice import PeerDevice
from message import PublicKeyMessage


class PeerDeviceManager:
    def __init__(self, key_pair: Keys):
        self.key_pair = key_pair
        self.peer_ip_set: Set[str] = set()
        self.peers: Set[PeerDevice] = set()
        self._sel: selectors.DefaultSelector | None = None

    def peer_manager_listener(self):
        """
        start the peer listener and register to the selector 
        """
        logging.debug("peerDeviceManager: listener started")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as peer_manager_socket:
            peer_manager_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            peer_manager_socket.bind((DEVICE_IP, COMMON_PORT))
            peer_manager_socket.listen(5)
            peer_manager_socket.setblocking(False)

            logging.debug(f"peerDeviceManager: listening on {DEVICE_IP}:{COMMON_PORT}")

            # register socket to a selector
            self._sel = selectors.DefaultSelector()
            self._sel.register(peer_manager_socket, selectors.EVENT_READ, data=self._accept_new_connection)

            # handle socket event
            while True: 
                events = self._sel.select()
                for key, mask in events: 
                    callback = key.data
                    callback(key.fileobj) 

    def handle_new_peer_ip(self, ip):
        """
        get ip and start a new connection thread using that ip
        """
        self.peer_ip_set.add(ip)
        logging.debug(f"peerManager: start connecting {ip}")
        threading.Thread(target=self._make_new_connection, args=[ip,]).start()

    def _make_new_connection(self, ip): 
        """
        get peer ip and make a connection with peer and register it to selector 
        """
        logging.debug(f"peerManager: making connection {ip}:{COMMON_PORT} ")
        peer_socket =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        peer_socket.connect((ip, COMMON_PORT))

        # make new PeerDevice
        peer_device = PeerDevice(ip, self.key_pair, peer_socket)
        peer_device.send_key()
        self.peers.add(peer_device)

        # register peer socket to selector
        self._sel.register(peer_socket, selectors.EVENT_READ, data=peer_device.handle_peer_messages)

    def _remove_addr_after_delay(self, ip): 
        """
        remove client ip from the client_ip_list after 10s
        """
        def _remove_after_delay():
            time.sleep(10)
            self._remove_client_ip(ip)
        threading.Thread(target=_remove_after_delay).start()

    def _remove_client_ip(self, ip): 
        """
        remove the client ip from the client_ip_list
        """
        self.peer_ip_set.discard(ip) 


    def _accept_new_connection(self, sock: socket.socket):
        """
        accept socket from the peer  and make new PeerDevice and register socket to selector
        """ 
        peer_sock, addr = sock.accept()
        peer_sock.setblocking(False)

        # make a new PeerDevice
        peer_device = PeerDevice(ip = addr[0], key_pair=self.key_pair, peer_socket=peer_sock)
        self.peers.add(peer_device)
        logging.debug(f"peerDeviceManager: made a connection with {addr}")

        # register socket to selector 
        self._sel.register(peer_sock, selectors.EVENT_READ, data=peer_device.handle_peer_messages)