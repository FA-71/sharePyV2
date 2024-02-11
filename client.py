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
    