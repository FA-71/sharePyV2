import socket 
import logging
import time
import selectors

from message import BroadcastMessage
from constants import *


class Client: 
    def __init__(self): 
        self.client_ip = self._get_client_ip()
        self._client_socket: socket.socket | None = None
        self._sel: selectors.DefaultSelector | None = None
    
    def broadcast_self(self):
        """
        broadcast message 
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            broadcast_addr = ('<broadcast>', BROADCAST_PORT)

            logging.debug(f"client: broadcasting")
            while True: 
                if (input("send ping: ") == "y"):
                    for i in range(5): 
                        s.sendto(BroadcastMessage.pack_message(), broadcast_addr)
                        time.sleep(2)
    
    def start_identifier(self): 
        # TODO: open this only for some time 
        # TODO: handle more than one connection(selection)
        # TODO: make this a secure connection with ssl
        logging.debug("device identifier started")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.bind((self.client_ip, COMMON_PORT))
            client_socket.listen(5)
            client_socket.setblocking(False)
            self._client_socket = client_socket

            sel = selectors.DefaultSelector()
            sel.register(client_socket, selectors.EVENT_READ, data=None)
            self._sel = sel

            while True: 
                events = sel.select(timeout=None)
                for key, mask in events: 
                    if key.data is None: 
                        self._accept_server()
                    else: 
                        callback = key.data
                        callback(key.fileobj) 


    def _accept_server(self):
            server_socket, addr = self.client_sock.accept()
            logging.debug(f"client: made a connection with {addr}")
            server_socket.setblocking(False)
            self._sel.register(server_socket, selectors.EVENT_READ, data=self._handle_server)

    def _handle_server(self, server_socket: socket.socket):
        data = server_socket.recv(1024) 
        if data: 
            logging.debug(f"{server_socket.getsockname}: data - {data}")


    def _get_client_ip(self):
        try: 
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(('8.8.8.8', 53))
                    local_ip = s.getsockname()[0]
            return local_ip

        except socket.error as se:
            print("Socket error occurred, trying local way")

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.connect(('192.255.255.252', 1))    
                ip = s.getsockname()[0]
            return ip

        except Exception as e: 
            print("can't get the client ip: ", e)
            exit() 
    