import socket

from constants import *


class Server: 
    def __init__ (self): 
        return
    
    
    def start_broadcast_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server: 
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', BROADCAST_PORT))

            print("Server started. Waiting for devices...")

            while True:
                data, addr = server.recvfrom(1024)
                print(f"Received message from {addr}: {data.decode()}")
                # TODO: send the public key 


    # TODO: make another listener to listen 42069 for public key 

    