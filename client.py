import socket 
import logging
import time

from message import BroadcastMessage
from constants import *


class Client: 
    def __init__(self): 
        self.client_ip = self.__get_client_ip()
    
    def broadcast_self(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s: 
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            broadcast_addr = ('<broadcast>', BROADCAST_PORT)

            logging.debug(f"client: broadcasting")
            for i in range(5): 
                s.sendto(BroadcastMessage.pack_message(), broadcast_addr)
                time.sleep(2)
    
    def start_identifier(self): 
        # TODO: open this only for some time 
        # TODO: handle more than one connection(selection or asyncio)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.client_ip, COMMON_PORT))
            sock.listen(5)

            conn, addr = sock.accept()
            with conn: 
                return 

    # TODO: if connection accept check the id of the msg and get the public key
    # TODO: send the public key and device info with that public key. 

    def __get_client_ip(self):
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
    