import socket

from constants import *


class Server: 
    def __init__ (self): 
        self.client_socket = None
        self.client_ip = set()
        return
    
    
    def start_broadcast_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server: 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', BROADCAST_PORT))

            print("Server started. Waiting for devices...")

            while True:
                data, addr = server.recvfrom(1024)
                print(f"Received message from {addr}: {data.decode()}")
                # TODO: check if the server already got msg from this addr  

    # TODO: make a connection with addr
    def __make_connection(self): 
        #TODO: check if client ip list is empty.
        #TODO: loop though client ip list  
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket: 
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.connect(())
    
            