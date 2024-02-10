import socket
import time
import threading
import logging

from message import BroadcastMessage
from constants import *


class Server: 
    def __init__ (self): 
        self.client_ip_list = set()
        return
    
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
                logging.debug(f"server: {addr} - {data}")
                logging.debug(BroadcastMessage.check_message(data))

                # TODO: check if peerdevice is connected 
                if BroadcastMessage.check_message(data) and addr not in self.client_ip_list:
                    self.__add_to_client_ip_list(addr[0])
                    logging.debug(f"server: new client ip {addr}")
                    logging.debug(f"server: start connecting {addr}")
                    threading.Thread(target=self._make_connection(addr[0])).start()

    def _make_connection(self, ip): 
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket: 
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.connect((ip, COMMON_PORT))
            client_socket.sendall("this is test")
            # TODO: send the msg with public key 
    
    def _add_to_client_ip_list(self, ip): 
        """
        add to new client ip to the client_ip_list and set 10s time to remove from the list
        """
        self.client_ip_list.add(ip)
        # self.__remove_addr_after_delay(ip)

    def _remove_addr_after_delay(self, ip): 
        """
        remove client ip from the client_ip_list after 10s
        """
        def _remove_after_delay():
            time.sleep(10)
            self.remove_client_ip(ip)
        threading.Thread(target=_remove_after_delay).start()

    def remove_client_ip(self, ip): 
        """
        remove the client ip from the client_ip_list
        """
        self.client_ip_list.discard(ip) 