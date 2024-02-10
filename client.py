import socket 
import logging
import time
import selectors

from message import BroadcastMessage
from config import DEVICE_IP
from constants import *


class Client: 
    def __init__(self): 
        self._sel: selectors.DefaultSelector | None = None
    
    def broadcast_self(self):
        """
        broadcast message 
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            broadcast_addr = ('<broadcast>', BROADCAST_PORT)

            while True: 
                if (input("send ping: ") == "y"):
                    logging.debug(f"client: broadcasting")
                    for i in range(5): 
                        s.sendto(BroadcastMessage.pack_message(), broadcast_addr)
                        time.sleep(2)
    
    def start_identifier(self): 
        """
        start the device identifier
        """
        # TODO: open this only for some time 
        # TODO: make this a secure connection with ssl
        logging.debug("client: device identifier started")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((DEVICE_IP, COMMON_PORT))
            client_socket.listen(5)
            client_socket.setblocking(False)

            self._sel = selectors.DefaultSelector()
            self._sel.register(client_socket, selectors.EVENT_READ, data=self._accept_server)

            while True: 
                events = self._sel.select()
                for key, mask in events: 
                    callback = key.data
                    callback(key.fileobj) 


    def _accept_server(self, sock: socket.socket):
        """
        accept socket from the server
        """
        server_socket, addr = sock.accept()
        logging.debug(f"client: made a connection with {addr}")
        server_socket.setblocking(False)
        self._sel.register(server_socket, selectors.EVENT_READ, data=self._handle_server)

    def _handle_server(self, server_socket: socket.socket):
        """
        handle server responses
        """
        data = server_socket.recv(4096) 
        if data: 
            logging.debug(f"client: {server_socket.getsockname()}: data - {data}")

